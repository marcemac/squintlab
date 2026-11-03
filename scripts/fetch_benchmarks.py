"""Download the benchmark images listed in benchmarks/manifest.toml into the local cache."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from squintlab.benchmarks import (
    HashMismatchError,
    ManifestError,
    SizeMismatchError,
    fetch_image,
    import_command,
    import_file,
    load_manifest,
    resolve_cache_dir,
)

DEFAULT_MANIFEST = Path(__file__).resolve().parent.parent / "benchmarks" / "manifest.toml"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--id", dest="image_id", help="fetch only this image id (default: all)")
    mode.add_argument(
        "--import",
        dest="import_args",
        nargs=2,
        metavar=("ID", "FILE"),
        help="verify a file you downloaded by hand against the manifest and copy it into the cache",
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="manifest path")
    args = parser.parse_args(argv)

    try:
        images = load_manifest(args.manifest)
        location = resolve_cache_dir()
    except ManifestError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    wanted = args.image_id if args.import_args is None else args.import_args[0]
    if wanted is not None:
        images = [image for image in images if image.id == wanted]
        if not images:
            print(f"error: no image with id {wanted!r} in {args.manifest}", file=sys.stderr)
            return 2

    print(f"cache folder: {location.path} (from {location.origin})")
    if args.import_args is not None:
        image = images[0]
        try:
            result = import_file(image, Path(args.import_args[1]), location.path)
        except (HashMismatchError, SizeMismatchError) as error:
            print(f"{image.id}: REFUSED, nothing saved ({error})", file=sys.stderr)
            return 1
        except OSError as error:
            print(f"{image.id}: FAILED ({error})", file=sys.stderr)
            return 1
        print(f"{image.id}: {result.path} (imported, SHA-256 and size verified)")
        return 0

    failures = 0
    for image in images:
        if image.access == "manual" and args.image_id is None:
            print(
                f"{image.id}: skipped (access is manual). Download it in a browser from "
                f"{image.object_url} and run: {import_command(image.id)}"
            )
            continue
        try:
            result = fetch_image(image, location.path)
        except HashMismatchError as error:
            print(f"{image.id}: FAILED, not saved ({error})", file=sys.stderr)
            failures += 1
        except (OSError, ValueError) as error:
            print(f"{image.id}: FAILED ({error})", file=sys.stderr)
            failures += 1
        else:
            state = "downloaded" if result.downloaded else "already present"
            print(f"{image.id}: {result.path} ({state}, SHA-256 verified)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
