#!/usr/bin/env python3
"""Checks registry.json the way Abstract reads it, and each listing's package
at its approved commit the way Abstract checks one before installing it.
Fetches and reads files only: no plugin code runs."""

import io
import json
import re
import subprocess
import sys
import tarfile
import tempfile

LIMIT = 25 * 1024 * 1024
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}")
REPO = re.compile(r"[A-Za-z0-9._-]{1,100}")
COMMIT = re.compile(r"[0-9a-f]{40}")


def entry_problems(entry: dict) -> list[str]:
    problems = []
    for key in ("owner", "slug", "name", "description", "pluginId", "repository", "commit"):
        if not isinstance(entry.get(key), str) or not entry[key]:
            problems.append(f"no {key}")
    if problems:
        return problems
    if not NAME.fullmatch(entry["owner"]) or not REPO.fullmatch(entry["slug"]):
        problems.append("owner/slug isn't a GitHub-style name")
    parts = entry["repository"].split("/")
    if len(parts) != 2 or not NAME.fullmatch(parts[0]) or not REPO.fullmatch(parts[1]) or parts[1] in (".", ".."):
        problems.append(f"repository {entry['repository']!r} isn't owner/repo on GitHub")
    path = entry.get("path")
    if path is not None and (not isinstance(path, str) or any(p in ("", ".", "..") or "\\" in p or ":" in p
                                                              for p in path.split("/"))):
        problems.append(f"path {path!r} isn't a folder inside the repository")
    if not COMMIT.fullmatch(entry["commit"]):
        problems.append("commit must be 40 lowercase hex characters")
    for shot in entry.get("screenshots", []):
        if not isinstance(shot, str) or not shot.startswith("https://"):
            problems.append(f"screenshot {shot!r} isn't https")
    return problems


def package_problems(entry: dict) -> list[str]:
    url = f"https://github.com/{entry['repository']}.git"
    with tempfile.TemporaryDirectory() as scratch:
        def git(*args: str) -> subprocess.CompletedProcess:
            return subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-C", scratch, *args], capture_output=True)
        git("init", "--quiet", "--bare")
        if git("fetch", "--quiet", "--depth", "1", "--no-tags", "--", url, entry["commit"]).returncode:
            return [f"commit {entry['commit']} can't be fetched from {url}"]
        tree = f"{entry['commit']}:{entry['path']}" if entry.get("path") else f"{entry['commit']}^{{tree}}"
        archived = git("archive", "--format=tar", tree)
        if archived.returncode:
            return [f"no folder {entry.get('path')!r} at that commit"]
    problems, files, manifest = [], {}, None
    with tarfile.open(fileobj=io.BytesIO(archived.stdout)) as tar:
        for member in tar.getmembers():
            if member.name.startswith("/") or ".." in member.name.split("/"):
                problems.append(f"{member.name}: outside the package")
            if member.issym() or member.islnk():
                problems.append(f"{member.name}: links aren't allowed")
            elif member.isfile():
                if member.mode & 0o111:
                    problems.append(f"{member.name}: executable files aren't allowed")
                files[member.name] = member.size
                if member.name == "manifest.json":
                    manifest = json.load(tar.extractfile(member))
    if sum(files.values()) > LIMIT:
        problems.append("the package is over 25 MB")
    if manifest is None:
        problems.append("no manifest.json at the package's root")
    elif manifest.get("id") != entry["pluginId"]:
        problems.append(f"manifest id {manifest.get('id')!r} isn't pluginId {entry['pluginId']!r}")
    return problems


def main() -> int:
    with open("registry.json") as f:
        registry = json.load(f)
    problems = []
    if registry.get("format") != 1 or not isinstance(registry.get("plugins"), list):
        problems.append("registry.json needs \"format\": 1 and a \"plugins\" list")
        registry["plugins"] = []
    ids = [f"{e.get('owner')}/{e.get('slug')}".lower() for e in registry["plugins"]]
    problems += [f"{i} is listed twice" for i in sorted({i for i in ids if ids.count(i) > 1})]
    for entry in registry["plugins"]:
        listing = f"{entry.get('owner')}/{entry.get('slug')}"
        found = entry_problems(entry)
        if not found:
            found = package_problems(entry)
        problems += [f"{listing}: {p}" for p in found]
        print(f"{listing}: {'ok' if not found else 'refused'}")
    for problem in problems:
        print(f"::error::{problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
