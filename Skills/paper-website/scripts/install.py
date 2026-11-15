#!/usr/bin/env python3
"""
install.py

Copies the site template into a project, or upgrades a project's copy.

    python3 install.py <project>/code/website_build

First run: copies the scripts, theme/ and content/ and records what it copied
in .template.json (template version and a hash of every file).

Later runs: replaces the scripts and the theme with the current template.
site.json and content/ belong to the author and are never touched. A script
or theme file the author has edited is kept, and the new version is written
beside it as <name>.new for comparison. New content templates are not added.
"""

import hashlib
import json
import shutil
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "template"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    dest = Path(sys.argv[1]).resolve()
    version = (TEMPLATE / "VERSION").read_text().strip()
    manifest_path = dest / ".template.json"
    files = [f for f in TEMPLATE.rglob("*") if f.is_file() and f.name != ".DS_Store" and "__pycache__" not in f.parts]
    fresh = not (dest / "build_site.py").exists()
    manifest = {"version": None, "files": {}}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
    replaced, kept, added = [], [], []
    for f in files:
        rel = f.relative_to(TEMPLATE).as_posix()
        target = dest / rel
        is_content = rel.startswith("content/")
        if not target.exists():
            if is_content and not fresh:
                continue                      # a page the author chose not to have
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)
            manifest["files"][rel] = sha(f)
            added.append(rel)
            continue
        if is_content or sha(target) == sha(f):
            if not is_content:
                manifest["files"][rel] = sha(f)
            continue
        recorded = manifest["files"].get(rel)
        if recorded == sha(f):                        # the template has not changed, only the author's copy has
            continue
        if recorded and sha(target) == recorded:      # untouched since it was copied
            shutil.copy2(f, target)
            manifest["files"][rel] = sha(f)
            replaced.append(rel)
        else:                                         # edited by the author, or copied before the manifest existed
            shutil.copy2(f, target.with_name(target.name + ".new"))
            kept.append(rel)
    old = manifest.get("version")
    manifest["version"] = version
    manifest_path.write_text(json.dumps(manifest, indent=1))
    if fresh:
        print(f"Template {version} installed in {dest} ({len(added)} files).")
        return
    print(f"Template {old or 'unknown'} -> {version} in {dest}")
    for label, lst in (("replaced", replaced), ("added", added)):
        if lst:
            print(f"  {label}: {', '.join(lst)}")
    if kept:
        print("  kept, because the project's copy differs from what was installed: " + ", ".join(kept))
        print("  The new versions are beside them as <name>.new. Compare, merge what the author changed, and delete the .new files.")
    if not (replaced or added or kept):
        print("  Already up to date.")


if __name__ == "__main__":
    main()
