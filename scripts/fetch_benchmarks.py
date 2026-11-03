"""Download the benchmark images listed in benchmarks/manifest.toml into the local cache."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from squintlab.benchmarks import (
    HashMismatchError,
    ManifestError,
    fetch_image,
    load_manifest,
    resolve_cache_dir,
)

DEFAULT_MANIFEST = Path(__file__).resolve().parent.parent / "benchmarks" / "manifest.toml"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", dest="image_id", help="fetch only this image id (default: all)")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="manifest path")
    args = parser.parse_args(argv)

    try:
        images = load_manifest(args.manifest)
        location = resolve_cache_dir()
    except ManifestError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if args.image_id is not None:
        images = [image for image in images if image.id == args.image_id]
        if not images:
            print(f"error: no image with id {args.image_id!r} in {args.manifest}", file=sys.stderr)
            return 2

    print(f"cache folder: {location.path} (from {location.origin})")
    failures = 0
    for image in images:
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
