from pathlib import Path
import hashlib
import json
import sys
import urllib.request


# run it from the root directory as a package python -m scripts.download_archive


MANIFEST_PATH = Path("data/archive/archive.json")
ARCHIVE_DIR = Path("data/raw/archives")

ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)

    return h.hexdigest()


def download_file(url: str, dest: Path) -> None:
    temp_path = dest.with_suffix(dest.suffix + ".part")

    existing_size = temp_path.stat().st_size if temp_path.exists() else 0

    headers = {}
    if existing_size > 0:
        headers["Range"] = f"bytes={existing_size}-"

    request = urllib.request.Request(url, headers=headers)

    mode = "ab" if existing_size > 0 else "wb"

    print(f"Downloading: {url}")
    print(f"Destination: {dest}")
    if existing_size:
        print(f"Resuming from byte {existing_size}")

    with urllib.request.urlopen(request) as response, temp_path.open(mode) as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)

    temp_path.rename(dest)


def main() -> None:
    with MANIFEST_PATH.open("r", encoding="utf-8") as f:
        archives = json.load(f)

    total = len(archives["datasets"])
    print(f"Found {total} archives in manifest")

    for i, item in enumerate(archives["datasets"], start=1):
        name = item["archive_name"]
        url = item["url"]
        expected_sha256 = item["sha256"]
        expected_size = item.get("size")

        dest = ARCHIVE_DIR / name

        print()
        print(f"[{i}/{total}] {name}")

        if dest.exists():
            actual_size = dest.stat().st_size

            if expected_size is not None and actual_size != expected_size:
                print(
                    f"Size mismatch. Expected {expected_size}, got {actual_size}. Redownloading."
                )
                dest.unlink()
            else:
                actual_sha256 = sha256_file(dest)
                if actual_sha256 == expected_sha256:
                    print("Already downloaded and checksum verified. Skipping.")
                    continue
                else:
                    print("Checksum mismatch. Redownloading.")
                    dest.unlink()

        download_file(url, dest)

        actual_sha256 = sha256_file(dest)
        if actual_sha256 != expected_sha256:
            print("ERROR: checksum failed")
            print(f"Expected: {expected_sha256}")
            print(f"Actual:   {actual_sha256}")
            sys.exit(1)

        print("Checksum verified.")

    print()
    print("All downloads complete.")


if __name__ == "__main__":
    main()
