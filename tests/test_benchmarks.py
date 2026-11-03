from __future__ import annotations

import hashlib
import importlib.util
import json
import threading
from collections.abc import Iterator
from dataclasses import replace
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

import pytest

from squintlab.benchmarks import (
    USER_AGENT,
    BenchmarkImage,
    DownloadBlockedError,
    FetchResult,
    HashMismatchError,
    ManifestError,
    SizeMismatchError,
    fetch_image,
    import_file,
    load_manifest,
    parse_manifest,
    resolve_cache_dir,
)

PAYLOAD = bytes(range(256)) * 64  # small generated stand-in for an image
PAYLOAD_SHA = hashlib.sha256(PAYLOAD).hexdigest()
REPO_ROOT = Path(__file__).resolve().parent.parent


class FileServer:
    def __init__(self, httpd: HTTPServer, requests: list[dict[str, str]]) -> None:
        self.httpd = httpd
        self.requests = requests

    @property
    def url(self) -> str:
        host, port = self.httpd.server_address[:2]
        return f"http://{host!s}:{port}/image.jpg"


@pytest.fixture
def server() -> Iterator[FileServer]:
    requests: list[dict[str, str]] = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            requests.append({k: v for k, v in self.headers.items()})
            if self.path == "/blocked.jpg":
                self.send_error(403)
                return
            if self.path != "/image.jpg":
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Length", str(len(PAYLOAD)))
            self.end_headers()
            self.wfile.write(PAYLOAD)

        def log_message(self, format: str, *args: Any) -> None:
            pass

    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield FileServer(httpd, requests)
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join()


def make_image(url: str, sha256: str = PAYLOAD_SHA) -> BenchmarkImage:
    return BenchmarkImage(
        id="test-image",
        title="Test",
        artist="Nobody",
        museum="Nowhere",
        object_number="0",
        licence="CC0",
        object_url="https://example.org/object",
        download_url=url,
        access="script",
        width=16,
        height=16,
        chroma_subsampling="4:2:0",
        jpeg_quality=90,
        size_bytes=len(PAYLOAD),
        sha256=sha256,
        checked_on="2026-11-02",
    )


# --- download ---------------------------------------------------------------


def test_correct_hash_saves_file(server: FileServer, tmp_path: Path) -> None:
    result = fetch_image(make_image(server.url), tmp_path)
    assert result.path == tmp_path / "test-image.jpg"
    assert result.path.read_bytes() == PAYLOAD
    assert result.verified is True
    assert result.downloaded is True
    assert [p.name for p in tmp_path.iterdir()] == ["test-image.jpg"]


def test_user_agent_names_project_without_personal_details(
    server: FileServer, tmp_path: Path
) -> None:
    fetch_image(make_image(server.url), tmp_path)
    sent = server.requests[0]["User-Agent"]
    assert sent == USER_AGENT
    lowered = {k.lower(): v for k, v in server.requests[0].items()}
    assert lowered["aic-user-agent"] == USER_AGENT
    assert "squintlab" in sent
    assert "https://github.com/marcemac/squintlab" in sent
    assert "@" not in sent


def test_wrong_hash_raises_and_leaves_nothing(server: FileServer, tmp_path: Path) -> None:
    wrong = "0" * 64
    with pytest.raises(HashMismatchError) as excinfo:
        fetch_image(make_image(server.url, sha256=wrong), tmp_path)
    message = str(excinfo.value)
    assert "test-image" in message
    assert wrong in message
    assert PAYLOAD_SHA in message
    assert list(tmp_path.iterdir()) == []


def test_wrong_hash_does_not_replace_existing_file(server: FileServer, tmp_path: Path) -> None:
    target = tmp_path / "test-image.jpg"
    target.write_bytes(b"old")
    with pytest.raises(HashMismatchError):
        fetch_image(make_image(server.url, sha256="0" * 64), tmp_path)
    assert target.read_bytes() == b"old"
    assert [p.name for p in tmp_path.iterdir()] == ["test-image.jpg"]


def test_existing_file_with_right_hash_is_skipped(server: FileServer, tmp_path: Path) -> None:
    (tmp_path / "test-image.jpg").write_bytes(PAYLOAD)
    result = fetch_image(make_image(server.url), tmp_path)
    assert result.downloaded is False
    assert result.verified is True
    assert server.requests == []


def test_existing_file_with_wrong_content_is_redownloaded(
    server: FileServer, tmp_path: Path
) -> None:
    (tmp_path / "test-image.jpg").write_bytes(b"corrupt")
    result = fetch_image(make_image(server.url), tmp_path)
    assert result.downloaded is True
    assert (tmp_path / "test-image.jpg").read_bytes() == PAYLOAD


def test_http_error_leaves_nothing(server: FileServer, tmp_path: Path) -> None:
    bad = replace(make_image(server.url), download_url=server.url.replace("image", "missing"))
    with pytest.raises(OSError):
        fetch_image(bad, tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_403_names_object_page_and_import_command(server: FileServer, tmp_path: Path) -> None:
    image = replace(make_image(server.url), download_url=server.url.replace("image", "blocked"))
    with pytest.raises(DownloadBlockedError) as excinfo:
        fetch_image(image, tmp_path)
    message = str(excinfo.value)
    assert "127.0.0.1 blocks scripted downloads" in message
    assert image.object_url in message
    assert "--import test-image" in message
    assert list(tmp_path.iterdir()) == []


def test_non_http_scheme_is_refused(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="scheme"):
        fetch_image(make_image("file:///etc/passwd"), tmp_path)


def test_cache_folder_is_created(server: FileServer, tmp_path: Path) -> None:
    cache = tmp_path / "a" / "b"
    fetch_image(make_image(server.url), cache)
    assert (cache / "test-image.jpg").exists()


# --- import -----------------------------------------------------------------


def test_import_accepts_the_right_file(tmp_path: Path) -> None:
    source = tmp_path / "downloads" / "browser-name (1).jpg"
    source.parent.mkdir()
    source.write_bytes(PAYLOAD)
    cache = tmp_path / "cache"
    result = import_file(make_image("https://example.org/d.jpg"), source, cache)
    assert result.path == cache / "test-image.jpg"
    assert result.path.read_bytes() == PAYLOAD
    assert result.imported is True
    assert result.verified is True
    assert [p.name for p in cache.iterdir()] == ["test-image.jpg"]
    assert source.read_bytes() == PAYLOAD  # the original is copied, not moved


def test_import_rejects_wrong_content_of_the_right_size(tmp_path: Path) -> None:
    source = tmp_path / "wrong.jpg"
    source.write_bytes(bytes(len(PAYLOAD)))
    cache = tmp_path / "cache"
    with pytest.raises(HashMismatchError) as excinfo:
        import_file(make_image("https://example.org/d.jpg"), source, cache)
    assert "test-image" in str(excinfo.value)
    assert PAYLOAD_SHA in str(excinfo.value)
    assert not cache.exists() or list(cache.iterdir()) == []


def test_import_rejects_wrong_size(tmp_path: Path) -> None:
    source = tmp_path / "short.jpg"
    source.write_bytes(PAYLOAD[:-1])
    cache = tmp_path / "cache"
    with pytest.raises(SizeMismatchError) as excinfo:
        import_file(make_image("https://example.org/d.jpg"), source, cache)
    assert str(len(PAYLOAD)) in str(excinfo.value)
    assert str(len(PAYLOAD) - 1) in str(excinfo.value)
    assert not cache.exists() or list(cache.iterdir()) == []


def test_refused_import_keeps_existing_cached_file(tmp_path: Path) -> None:
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / "test-image.jpg").write_bytes(b"old")
    source = tmp_path / "wrong.jpg"
    source.write_bytes(bytes(len(PAYLOAD)))
    with pytest.raises(HashMismatchError):
        import_file(make_image("https://example.org/d.jpg"), source, cache)
    assert [p.name for p in cache.iterdir()] == ["test-image.jpg"]
    assert (cache / "test-image.jpg").read_bytes() == b"old"


def test_import_of_missing_file_leaves_nothing(tmp_path: Path) -> None:
    cache = tmp_path / "cache"
    with pytest.raises(FileNotFoundError):
        import_file(make_image("https://example.org/d.jpg"), tmp_path / "nope.jpg", cache)
    assert not cache.exists() or list(cache.iterdir()) == []


# --- cache folder order -----------------------------------------------------


def write_config(path: Path, cache_dir: Path) -> Path:
    path.write_text(f'cache_dir = "{cache_dir.as_posix()}"\n', encoding="utf-8")
    return path


def test_env_var_wins(tmp_path: Path) -> None:
    config = write_config(tmp_path / "config.toml", tmp_path / "from-config")
    env = {"SQUINTLAB_CACHE_DIR": str(tmp_path / "from-env")}
    location = resolve_cache_dir(env=env, config_path=config)
    assert location.path == tmp_path / "from-env"
    assert location.source == "environment"
    assert "SQUINTLAB_CACHE_DIR" in location.origin


def test_config_file_used_without_env_var(tmp_path: Path) -> None:
    config = write_config(tmp_path / "config.toml", tmp_path / "from-config")
    location = resolve_cache_dir(env={}, config_path=config)
    assert location.path == tmp_path / "from-config"
    assert location.source == "config"
    assert str(config) in location.origin


def test_empty_env_var_is_ignored(tmp_path: Path) -> None:
    config = write_config(tmp_path / "config.toml", tmp_path / "from-config")
    location = resolve_cache_dir(env={"SQUINTLAB_CACHE_DIR": ""}, config_path=config)
    assert location.source == "config"


def test_default_used_when_nothing_else_is_set(tmp_path: Path) -> None:
    location = resolve_cache_dir(env={}, config_path=tmp_path / "missing.toml")
    assert location.source == "default"
    assert "squintlab" in str(location.path)


def test_default_used_when_config_has_no_cache_dir(tmp_path: Path) -> None:
    config = tmp_path / "config.toml"
    config.write_text("other = 1\n", encoding="utf-8")
    assert resolve_cache_dir(env={}, config_path=config).source == "default"


def test_default_config_path_comes_from_platformdirs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    monkeypatch.delenv("SQUINTLAB_CACHE_DIR", raising=False)
    (tmp_path / "squintlab").mkdir()
    write_config(tmp_path / "squintlab" / "config.toml", tmp_path / "from-config")
    location = resolve_cache_dir()
    assert location.source == "config"
    assert location.path == tmp_path / "from-config"


def test_invalid_config_file_is_an_error(tmp_path: Path) -> None:
    config = tmp_path / "config.toml"
    config.write_text("cache_dir = [", encoding="utf-8")
    with pytest.raises(ManifestError, match="config.toml"):
        resolve_cache_dir(env={}, config_path=config)


def test_non_string_cache_dir_is_an_error(tmp_path: Path) -> None:
    config = tmp_path / "config.toml"
    config.write_text("cache_dir = 3\n", encoding="utf-8")
    with pytest.raises(ManifestError, match="cache_dir"):
        resolve_cache_dir(env={}, config_path=config)


# --- manifest ---------------------------------------------------------------


def valid_entry() -> dict[str, Any]:
    return {
        "id": "some-image",
        "title": "T",
        "artist": "A",
        "museum": "M",
        "object_number": "1",
        "licence": "CC0",
        "object_url": "https://example.org/o",
        "download_url": "https://example.org/d.jpg",
        "access": "script",
        "width": 100,
        "height": 80,
        "chroma_subsampling": "4:2:0",
        "jpeg_quality": 95,
        "size_bytes": 1234,
        "sha256": "a" * 64,
        "checked_on": "2026-11-02",
    }


def test_repository_manifest_is_valid() -> None:
    images = load_manifest(REPO_ROOT / "benchmarks" / "manifest.toml")
    first = images[0]
    assert first.access == "script"
    assert first.id == "aic-poppy-field-giverny"
    assert first.width == 3000
    assert first.height == 1948
    assert first.size_bytes == 2066120
    assert first.sha256 == "32adf0f2bd984c982f7d87246653139c669d3eaa565888f4d0139a96391cb920"
    assert first.checked_on == "2026-11-02"


def test_valid_entry_parses() -> None:
    (image,) = parse_manifest({"images": [valid_entry()]})
    assert image.id == "some-image"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("id", "Bad Id"),
        ("id", ""),
        ("title", ""),
        ("width", 0),
        ("width", "100"),
        ("height", -5),
        ("width", True),
        ("jpeg_quality", 0),
        ("jpeg_quality", 101),
        ("size_bytes", 0),
        ("sha256", "abc"),
        ("sha256", "G" * 64),
        ("sha256", "A" * 64),
        ("chroma_subsampling", "4:9:9"),
        ("access", "sometimes"),
        ("download_url", "http://example.org/d.jpg"),
        ("download_url", "not a url"),
        ("object_url", "ftp://example.org/o"),
        ("checked_on", "yesterday"),
        ("checked_on", "2026-13-40"),
    ],
)
def test_invalid_values_are_rejected(field: str, value: object) -> None:
    entry = valid_entry()
    entry[field] = value
    with pytest.raises(ManifestError, match=field):
        parse_manifest({"images": [entry]})


@pytest.mark.parametrize("field", list(valid_entry()))
def test_missing_field_is_rejected(field: str) -> None:
    entry = valid_entry()
    del entry[field]
    with pytest.raises(ManifestError, match=field):
        parse_manifest({"images": [entry]})


def test_unknown_field_is_rejected() -> None:
    entry = valid_entry()
    entry["extra"] = "x"
    with pytest.raises(ManifestError, match="extra"):
        parse_manifest({"images": [entry]})


def test_duplicate_ids_are_rejected() -> None:
    with pytest.raises(ManifestError, match="duplicate"):
        parse_manifest({"images": [valid_entry(), valid_entry()]})


def test_missing_or_empty_images_table_is_rejected() -> None:
    with pytest.raises(ManifestError, match="images"):
        parse_manifest({})
    with pytest.raises(ManifestError, match="images"):
        parse_manifest({"images": []})


def test_malformed_toml_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "manifest.toml"
    path.write_text("[[images]\n", encoding="utf-8")
    with pytest.raises(ManifestError, match="manifest.toml"):
        load_manifest(path)


def test_missing_manifest_file_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ManifestError, match="manifest.toml"):
        load_manifest(tmp_path / "manifest.toml")


# --- network ----------------------------------------------------------------


@pytest.mark.network
def test_fetch_aic_poppy_field(tmp_path: Path) -> None:
    images = {i.id: i for i in load_manifest(REPO_ROOT / "benchmarks" / "manifest.toml")}
    image = images["aic-poppy-field-giverny"]
    try:
        result = fetch_image(image, tmp_path)
    except DownloadBlockedError as error:
        pytest.skip(f"host answered HTTP 403 and blocks scripted downloads: {error}")
    assert result.verified is True
    assert result.path.stat().st_size == image.size_bytes


# --- command-line script ----------------------------------------------------


def load_script() -> Any:
    spec = importlib.util.spec_from_file_location(
        "fetch_benchmarks_script", REPO_ROOT / "scripts" / "fetch_benchmarks.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_manifest(path: Path, access: str, image_id: str = "manual-one") -> Path:
    entry = valid_entry() | {"id": image_id, "access": access}
    lines = ["[[images]]"]
    for key, value in entry.items():
        lines.append(f"{key} = {value!r}".replace("'", '"'))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_fetch_all_skips_manual_entries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    script = load_script()
    manifest = write_manifest(tmp_path / "manifest.toml", access="manual")
    monkeypatch.setenv("SQUINTLAB_CACHE_DIR", str(tmp_path / "cache"))

    def fail(*args: object, **kwargs: object) -> None:
        raise AssertionError("manual entry must not be downloaded")

    monkeypatch.setattr(script, "fetch_image", fail)
    assert script.main(["--manifest", str(manifest)]) == 0
    out = capsys.readouterr().out
    assert "manual-one: skipped" in out
    assert "https://example.org/o" in out
    assert "--import manual-one" in out


def test_manual_entry_is_fetched_when_asked_for_by_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    script = load_script()
    manifest = write_manifest(tmp_path / "manifest.toml", access="manual")
    monkeypatch.setenv("SQUINTLAB_CACHE_DIR", str(tmp_path / "cache"))
    calls: list[str] = []

    def fake(image: BenchmarkImage, cache_dir: Path) -> FetchResult:
        calls.append(image.id)
        return FetchResult(image.id, cache_dir / "x.jpg", downloaded=True, verified=True)

    monkeypatch.setattr(script, "fetch_image", fake)
    assert script.main(["--manifest", str(manifest), "--id", "manual-one"]) == 0
    assert calls == ["manual-one"]


def test_script_import_accepts_and_refuses(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    script = load_script()
    entry = valid_entry() | {"id": "manual-one", "size_bytes": len(PAYLOAD), "sha256": PAYLOAD_SHA}
    manifest = tmp_path / "manifest.toml"
    manifest.write_text(
        "[[images]]\n" + "".join(f"{k} = {json.dumps(v)}\n" for k, v in entry.items()),
        encoding="utf-8",
    )
    cache = tmp_path / "cache"
    monkeypatch.setenv("SQUINTLAB_CACHE_DIR", str(cache))
    good = tmp_path / "good.jpg"
    good.write_bytes(PAYLOAD)
    bad = tmp_path / "bad.jpg"
    bad.write_bytes(bytes(len(PAYLOAD)))

    assert script.main(["--manifest", str(manifest), "--import", "manual-one", str(bad)]) == 1
    assert not cache.exists() or list(cache.iterdir()) == []
    assert "REFUSED" in capsys.readouterr().err

    assert script.main(["--manifest", str(manifest), "--import", "manual-one", str(good)]) == 0
    assert (cache / "manual-one.jpg").read_bytes() == PAYLOAD
    assert "imported" in capsys.readouterr().out

    assert script.main(["--manifest", str(manifest), "--import", "other", str(good)]) == 2
