import os
import requests
import tarfile
from pathlib import Path

# 🔑 Replace with your MaxMind license key
LICENSE_KEY = os.getenv("MAXMIND_LICENSE_KEY")

# Databases you want to download (Country + City)
EDITIONS = ["GeoLite2-Country", "GeoLite2-City"]

# Always resolve BASE_DIR to the project root
BASE_DIR = Path(__file__).resolve().parent.parent
GEOIP_DIR = BASE_DIR / "core" / "geoip"

# Ensure geoip directory exists
GEOIP_DIR.mkdir(parents=True, exist_ok=True)


def download_and_extract(edition):
    url = f"https://download.maxmind.com/app/geoip_download?edition_id={edition}&license_key={LICENSE_KEY}&suffix=tar.gz"
    tar_file = BASE_DIR / f"{edition}.tar.gz"

    print(f"📥 Downloading {edition} database...")
    response = requests.get(url, stream=True)
    with open(tar_file, "wb") as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)

    print(f"📦 Extracting {edition}...")
    with tarfile.open(tar_file, "r:gz") as tar:
        for member in tar.getmembers():
            if member.name.endswith(".mmdb"):
                member.name = os.path.basename(member.name)  # strip folder paths
                tar.extract(member, path=GEOIP_DIR)

    print(f"✅ {edition}.mmdb is ready at:", GEOIP_DIR)
    tar_file.unlink()


for edition in EDITIONS:
    download_and_extract(edition)
