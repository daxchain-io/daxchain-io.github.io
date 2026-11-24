"""Render the DaxToken pages listed in sitemap.xml from the public metadata API."""

import json
import re
from html import escape
from pathlib import Path
from string import Template
from urllib.request import urlopen
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
TOKEN_URL = re.compile(r"https://daxchain\.io/daxtoken/(0|[1-9][0-9]*)/")
ARTWORK = "ipfs://QmcifXX4WU5kUyVcLePo3LAM3UYHKZbGUbHpQCX6pgHvh2"


def render(template, token_id, canonical):
    url = "https://api.daxchain.io/tokens"
    if token_id != "0":
        url += f"?token={token_id}"
    with urlopen(url, timeout=20) as response:
        metadata = json.load(response)
    traits = {item["trait_type"]: item["value"] for item in metadata["attributes"]}
    if traits["id"] != token_id or metadata["external_url"] != canonical.rstrip("/"):
        raise ValueError(f"Metadata from {url} does not identify {canonical}")
    if metadata["image"] != ARTWORK:
        raise ValueError(f"Token {token_id} requires a different artwork file")
    return template.substitute(
        token_id=token_id,
        name=escape(metadata["name"]),
        description=escape(metadata["description"]),
        contract=escape(traits["contract/token"]),
        canonical=canonical,
        metadata_url=url,
    )


def main():
    template = Template((ROOT / "scripts" / "daxtoken.html.tmpl").read_text(encoding="utf-8"))
    sitemap = ElementTree.parse(ROOT / "sitemap.xml")
    pages = {}
    for location in sitemap.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
        match = TOKEN_URL.fullmatch(location.text or "")
        if match:
            token_id = match.group(1)
            pages[ROOT / "daxtoken" / token_id / "index.html"] = render(template, token_id, location.text)

    for path, html in pages.items():
        path.parent.mkdir(exist_ok=True)
        path.write_text(html, encoding="utf-8")
    print(f"Rendered {len(pages)} token pages")


if __name__ == "__main__":
    main()
