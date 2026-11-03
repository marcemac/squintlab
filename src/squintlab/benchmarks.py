"""Benchmark manifest, cache-folder resolution and verified downloads.

The benchmark images are never stored in the repository. ``benchmarks/manifest.toml``
describes each one, including its SHA-256, and :func:`fetch_image` downloads it into a
local cache folder and keeps it only if the hash matches.
"""

from __future__ import annotations

import hashlib
import os
import re
import tempfile
import tomllib
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Final, Literal
from urllib.parse import urlparse

import platformdirs

from squintlab import __version__

APP_NAME: Final = "squintlab"
REPOSITORY_URL: Final = "https://github.com/marcemac/squintlab"
USER_AGENT: Final = f"squintlab/{__version__} (+{REPOSITORY_URL})"
CACHE_ENV_VAR: Final = "SQUINTLAB_CACHE_DIR"

_CHUNK_SIZE: Final = 1024 * 1024
_TIMEOUT_SECONDS: Final = 60
_ID_PATTERN: Final = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
_SHA256_PATTERN: Final = re.compile(r"[0-9a-f]{64}")
_CHROMA_SUBSAMPLING: Final = frozenset({"4:4:4", "4:2:2", "4:2:0", "4:4:0", "4:1:1", "gray"})


class ManifestError(ValueError):
    """The manifest or the user's config file is missing, malformed or invalid."""


class HashMismatchError(Exception):
    """A downloaded file did not have the SHA-256 recorded in the manifest."""

    def __init__(self, image_id: str, expected: str, actual: str) -> None:
        super().__init__(f"{image_id}: SHA-256 mismatch: expected {expected}, got {actual}")
        self.image_id = image_id
        self.expected = expected
        self.actual = actual


@dataclass(frozen=True)
class BenchmarkImage:
    id: str
    title: str
    artist: str
    museum: str
    object_number: str
    licence: str
    object_url: str
    download_url: str
    width: int
    height: int
    chroma_subsampling: str
    jpeg_quality: int
    size_bytes: int
    sha256: str
    checked_on: str


@dataclass(frozen=True)
class CacheLocation:
    path: Path
    source: Literal["environment", "config", "default"]
    origin: str  # human-readable description of where the path came from


@dataclass(frozen=True)
class FetchResult:
    image_id: str
    path: Path
    downloaded: bool  # False when a verified copy was already in the cache
    verified: bool


# --- manifest ---------------------------------------------------------------


def _text(entry: Mapping[str, Any], key: str, where: str) -> str:
    value = entry[key]
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{where}: {key} must be a non-empty string")
    return value


def _positive_int(
    entry: Mapping[str, Any], key: str, where: str, maximum: int | None = None
) -> int:
    value = entry[key]
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ManifestError(f"{where}: {key} must be a positive integer")
    if maximum is not None and value > maximum:
        raise ManifestError(f"{where}: {key} must be at most {maximum}")
    return value


def _https_url(entry: Mapping[str, Any], key: str, where: str) -> str:
    value = _text(entry, key, where)
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ManifestError(f"{where}: {key} must be an https URL")
    return value


def _parse_image(entry: object, index: int) -> BenchmarkImage:
    where = f"images[{index}]"
    if not isinstance(entry, dict):
        raise ManifestError(f"{where}: must be a table")
    fields = set(BenchmarkImage.__dataclass_fields__)
    missing = sorted(fields - entry.keys())
    if missing:
        raise ManifestError(f"{where}: missing field(s): {', '.join(missing)}")
    unknown = sorted(entry.keys() - fields)
    if unknown:
        raise ManifestError(f"{where}: unknown field(s): {', '.join(unknown)}")

    image_id = _text(entry, "id", where)
    if not _ID_PATTERN.fullmatch(image_id):
        raise ManifestError(f"{where}: id must be lowercase letters, digits and hyphens")
    where = f"images[{index}] ({image_id})"

    sha256 = _text(entry, "sha256", where)
    if not _SHA256_PATTERN.fullmatch(sha256):
        raise ManifestError(f"{where}: sha256 must be 64 lowercase hex digits")
    chroma = _text(entry, "chroma_subsampling", where)
    if chroma not in _CHROMA_SUBSAMPLING:
        allowed = ", ".join(sorted(_CHROMA_SUBSAMPLING))
        raise ManifestError(f"{where}: chroma_subsampling must be one of {allowed}")
    checked_on = _text(entry, "checked_on", where)
    try:
        date.fromisoformat(checked_on)
    except ValueError:
        raise ManifestError(f"{where}: checked_on must be a YYYY-MM-DD date") from None

    return BenchmarkImage(
        id=image_id,
        title=_text(entry, "title", where),
        artist=_text(entry, "artist", where),
        museum=_text(entry, "museum", where),
        object_number=_text(entry, "object_number", where),
        licence=_text(entry, "licence", where),
        object_url=_https_url(entry, "object_url", where),
        download_url=_https_url(entry, "download_url", where),
        width=_positive_int(entry, "width", where),
        height=_positive_int(entry, "height", where),
        chroma_subsampling=chroma,
        jpeg_quality=_positive_int(entry, "jpeg_quality", where, maximum=100),
        size_bytes=_positive_int(entry, "size_bytes", where),
        sha256=sha256,
        checked_on=checked_on,
    )


def parse_manifest(data: Mapping[str, Any]) -> list[BenchmarkImage]:
    """Validate parsed manifest data and return its images."""
    entries = data.get("images")
    if not isinstance(entries, list) or not entries:
        raise ManifestError("manifest must contain a non-empty [[images]] array")
    images = [_parse_image(entry, i) for i, entry in enumerate(entries)]
    seen: set[str] = set()
    for image in images:
        if image.id in seen:
            raise ManifestError(f"duplicate image id: {image.id}")
        seen.add(image.id)
    return images


def load_manifest(path: Path) -> list[BenchmarkImage]:
    """Read and validate the manifest file at ``path``."""
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except OSError as error:
        raise ManifestError(f"cannot read {path}: {error.strerror or error}") from error
    except tomllib.TOMLDecodeError as error:
        raise ManifestError(f"{path}: invalid TOML: {error}") from error
    try:
        return parse_manifest(data)
    except ManifestError as error:
        raise ManifestError(f"{path}: {error}") from error


# --- cache folder -----------------------------------------------------------


def default_config_path() -> Path:
    return platformdirs.user_config_path(APP_NAME) / "config.toml"


def resolve_cache_dir(
    env: Mapping[str, str] | None = None, config_path: Path | None = None
) -> CacheLocation:
    """Find the cache folder: environment variable, then config file, then platform default."""
    environment = os.environ if env is None else env
    from_env = environment.get(CACHE_ENV_VAR, "")
    if from_env:
        return CacheLocation(
            path=Path(from_env).expanduser(),
            source="environment",
            origin=f"{CACHE_ENV_VAR} environment variable",
        )

    config = default_config_path() if config_path is None else config_path
    if config.is_file():
        try:
            with config.open("rb") as handle:
                data = tomllib.load(handle)
        except OSError as error:
            raise ManifestError(f"cannot read {config}: {error.strerror or error}") from error
        except tomllib.TOMLDecodeError as error:
            raise ManifestError(f"{config}: invalid TOML: {error}") from error
        if "cache_dir" in data:
            value = data["cache_dir"]
            if not isinstance(value, str) or not value.strip():
                raise ManifestError(f"{config}: cache_dir must be a non-empty string")
            return CacheLocation(
                path=Path(value).expanduser(),
                source="config",
                origin=f"cache_dir in {config}",
            )

    return CacheLocation(
        path=platformdirs.user_cache_path(APP_NAME),
        source="default",
        origin="platform default user cache folder",
    )


# --- download ---------------------------------------------------------------


def _sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(_CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def cached_path(image: BenchmarkImage, cache_dir: Path) -> Path:
    return cache_dir / f"{image.id}.jpg"


def is_cached(image: BenchmarkImage, cache_dir: Path) -> bool:
    """True if a file with the expected SHA-256 is already in ``cache_dir``."""
    target = cached_path(image, cache_dir)
    return target.is_file() and _sha256_of_file(target) == image.sha256


def fetch_image(image: BenchmarkImage, cache_dir: Path) -> FetchResult:
    """Download ``image`` into ``cache_dir`` unless a verified copy is already there.

    The data goes to a temporary file in ``cache_dir`` and is renamed into place only if
    its SHA-256 matches the manifest. On a mismatch, or any other failure, the temporary
    file is deleted and an exception is raised.
    """
    target = cached_path(image, cache_dir)
    if is_cached(image, cache_dir):
        return FetchResult(image.id, target, downloaded=False, verified=True)

    scheme = urlparse(image.download_url).scheme
    if scheme not in ("http", "https"):
        raise ValueError(f"{image.id}: unsupported URL scheme {scheme!r}")

    cache_dir.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(image.download_url, headers={"User-Agent": USER_AGENT})
    handle, temp_name = tempfile.mkstemp(dir=cache_dir, prefix=f".{image.id}-", suffix=".part")
    temp_path = Path(temp_name)
    try:
        digest = hashlib.sha256()
        with os.fdopen(handle, "wb") as out:
            with urllib.request.urlopen(request, timeout=_TIMEOUT_SECONDS) as response:
                while chunk := response.read(_CHUNK_SIZE):
                    digest.update(chunk)
                    out.write(chunk)
        actual = digest.hexdigest()
        if actual != image.sha256:
            raise HashMismatchError(image.id, image.sha256, actual)
        temp_path.replace(target)
    except BaseException:
        temp_path.unlink(missing_ok=True)
        raise
    return FetchResult(image.id, target, downloaded=True, verified=True)
