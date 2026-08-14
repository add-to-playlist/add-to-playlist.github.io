import hashlib
import os

from functools import cache


def make_asset_url(assets_dir: str):
    @cache
    def asset_url(file_name: str):
        path = os.path.join(assets_dir, file_name)

        with open(path, mode="rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()[:12]

        return f"/{file_name}?v={digest}"

    return asset_url
