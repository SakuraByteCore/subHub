#!/usr/bin/env python3
"""Build the merged TVBox subscription file."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCES_FILE = ROOT / "sources.json"
OUTPUT_FILE = ROOT / "tvbox.json"
MANIFEST_FILE = ROOT / "manifest.json"
USER_AGENT = "SakuraByteCore-subHub-tvbox-builder/1.0 (+https://github.com/SakuraByteCore/subHub)"

URL_FIELDS = {
    "api",
    "ext",
    "jar",
    "logo",
    "playUrl",
    "script",
    "spider",
    "url",
    "wallpaper",
}

ARRAY_KEYS = ("sites", "lives", "parses", "rules", "doh")
SET_KEYS = ("hosts", "flags", "ads")
NOTICE_SITE = {
    "key": "subHub_notice",
    "name": "subHub | 公共订阅聚合",
    "type": 3,
    "api": "https://qist.wyfc.qzz.io/lib/drpy2.min.js",
    "ext": "https://cdn.jsdelivr.net/gh/SakuraByteCore/subHub@refs/heads/main/lib/subhub_notice.js",
    "searchable": 1,
    "quickSearch": 0,
    "changeable": 1,
}


def strip_full_line_json_comments(text: str) -> str:
    """Strip JSONC-style full-line comments without touching URLs inside strings."""
    lines = []
    for line in text.splitlines():
        if line.lstrip().startswith("//"):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def fetch_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read().decode("utf-8-sig")
    data = json.loads(strip_full_line_json_comments(raw))
    if not isinstance(data, dict):
        raise ValueError(f"source root must be an object: {url}")
    return data


def is_relative_path(value: str) -> bool:
    if not value or value.startswith(("#", "csp_", "CSP_")):
        return False
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme or value.startswith("//"):
        return False
    return value.startswith(("./", "../", "/"))


def absolutize_string(value: str, base_url: str) -> str:
    """Convert relative URL/path strings to absolute URLs.

    TVBox values may contain a md5 suffix, e.g. ./jar/spider.jar;md5;xxx.
    Only the first segment is a path in that format.
    """
    if ";" in value:
        head, *tail = value.split(";")
        if is_relative_path(head):
            head = urllib.parse.urljoin(base_url, head)
        return ";".join([head, *tail])
    if is_relative_path(value):
        return urllib.parse.urljoin(base_url, value)
    return value


def normalize_urls(value: Any, base_url: str, field: str | None = None) -> Any:
    if isinstance(value, dict):
        return {key: normalize_urls(item, base_url, key) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_urls(item, base_url, field) for item in value]
    if isinstance(value, str) and (field in URL_FIELDS or is_relative_path(value.split(";", 1)[0])):
        return absolutize_string(value, base_url)
    return value


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()[:12]


def tagged_name(item: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    item = copy.deepcopy(item)
    name = item.get("name")
    if isinstance(name, str) and not name.startswith(f"[{source['id']}]"):
        item["name"] = f"[{source['id']}] {name}"
    return item


def unique_key(base: str, used: set[str], source_id: str) -> str:
    candidate = f"{source_id}_{base}"
    if candidate not in used:
        return candidate
    index = 2
    while f"{candidate}_{index}" in used:
        index += 1
    return f"{candidate}_{index}"


def add_site(target: list[dict[str, Any]], used_keys: dict[str, str], item: dict[str, Any], source: dict[str, Any]) -> None:
    item = copy.deepcopy(item)
    key = item.get("key")
    if not isinstance(key, str) or not key:
        key = f"{source['id']}_{digest(item)}"
        item["key"] = key

    body = stable_json(item)
    existing = used_keys.get(key)
    if existing is None:
        used_keys[key] = body
        target.append(item)
        return
    if existing == body:
        return

    item = tagged_name(item, source)
    item["key"] = unique_key(key, set(used_keys), source["id"])
    used_keys[item["key"]] = stable_json(item)
    target.append(item)


def add_named(target: list[dict[str, Any]], used_names: dict[str, str], item: dict[str, Any], source: dict[str, Any]) -> None:
    item = copy.deepcopy(item)
    name = item.get("name")
    if not isinstance(name, str) or not name:
        name = f"{source['id']}_{digest(item)}"
        item["name"] = name

    body = stable_json(item)
    existing = used_names.get(name)
    if existing is None:
        used_names[name] = body
        target.append(item)
        return
    if existing == body:
        return

    item = tagged_name(item, source)
    used_names[item["name"]] = stable_json(item)
    target.append(item)


def add_live(target: list[dict[str, Any]], used: set[str], item: dict[str, Any]) -> None:
    item = copy.deepcopy(item)
    marker = f"{item.get('name', '')}\u0000{item.get('url', '')}"
    if marker in used:
        return
    used.add(marker)
    target.append(item)


def attach_source_jar_to_sites(data: dict[str, Any]) -> None:
    jar = data.get("spider")
    if not isinstance(jar, str):
        return
    for site in data.get("sites", []):
        if not isinstance(site, dict):
            continue
        if site.get("type") == 3 and "jar" not in site:
            site["jar"] = jar


def add_notice_site(merged: dict[str, Any]) -> None:
    sites = merged.setdefault("sites", [])
    sites[:] = [site for site in sites if not (isinstance(site, dict) and site.get("key") == NOTICE_SITE["key"])]
    notice = copy.deepcopy(NOTICE_SITE)
    if isinstance(merged.get("spider"), str):
        notice["jar"] = merged["spider"]
    sites.insert(0, notice)


def load_sources() -> list[dict[str, Any]]:
    sources = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    enabled = [source for source in sources if source.get("enabled", True)]
    return sorted(enabled, key=lambda source: int(source.get("priority", 100)))


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    sources = load_sources()
    merged: dict[str, Any] = {}
    manifest: dict[str, Any] = {
        "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sources": [],
        "counts": {},
    }

    site_keys: dict[str, str] = {}
    named_keys: dict[str, dict[str, str]] = {key: {} for key in ("parses", "rules", "doh")}
    live_keys: set[str] = set()
    set_values: dict[str, set[str]] = {key: set() for key in SET_KEYS}

    merged["sites"] = []
    merged["lives"] = []

    for source in sources:
        source_status: dict[str, Any] = {
            "id": source["id"],
            "name": source.get("name", source["id"]),
            "url": source["url"],
            "priority": source.get("priority"),
        }
        try:
            data = fetch_json(source["url"])
            data = normalize_urls(data, source["url"])
            attach_source_jar_to_sites(data)
            source_status["ok"] = True
            source_status["counts"] = {
                key: len(data.get(key, [])) for key in (*ARRAY_KEYS, *SET_KEYS) if isinstance(data.get(key), list)
            }
        except (OSError, urllib.error.URLError, json.JSONDecodeError, ValueError) as exc:
            source_status["ok"] = False
            source_status["error"] = str(exc)
            manifest["sources"].append(source_status)
            continue

        if "spider" not in merged and isinstance(data.get("spider"), str):
            merged["spider"] = data["spider"]
        if "wallpaper" not in merged and isinstance(data.get("wallpaper"), str):
            merged["wallpaper"] = data["wallpaper"]
        if "logo" not in merged and isinstance(data.get("logo"), str):
            merged["logo"] = data["logo"]

        for item in data.get("sites", []):
            if isinstance(item, dict):
                add_site(merged["sites"], site_keys, item, source)
        for item in data.get("lives", []):
            if isinstance(item, dict):
                add_live(merged["lives"], live_keys, item)
        for key in ("parses", "rules", "doh"):
            if key not in merged:
                merged[key] = []
            for item in data.get(key, []):
                if isinstance(item, dict):
                    add_named(merged[key], named_keys[key], item, source)
        for key in SET_KEYS:
            if key not in merged:
                merged[key] = []
            for item in data.get(key, []):
                if isinstance(item, str) and item not in set_values[key]:
                    set_values[key].add(item)
                    merged[key].append(item)

        manifest["sources"].append(source_status)

    add_notice_site(merged)
    manifest["generated"] = {"notice_site": NOTICE_SITE["key"]}

    for key in ["sites", "lives", "parses", "hosts", "flags", "doh", "rules", "ads"]:
        if key in merged:
            manifest["counts"][key] = len(merged[key])

    return merged, manifest


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    merged, manifest = build()
    write_json(OUTPUT_FILE, merged)
    write_json(MANIFEST_FILE, manifest)
    print(f"wrote {OUTPUT_FILE.relative_to(ROOT)}")
    print(f"wrote {MANIFEST_FILE.relative_to(ROOT)}")
    print(json.dumps(manifest["counts"], ensure_ascii=False, sort_keys=True))
    failed = [source for source in manifest["sources"] if not source.get("ok")]
    if failed:
        print(json.dumps({"failed_sources": failed}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
