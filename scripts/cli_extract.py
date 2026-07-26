#!/usr/bin/env python
"""
AuraStack Module Extractor CLI
Allows developers to bundle and extract specific domain modules (payments, teams, users, blog)
into standalone packages ready to be imported into any Django project.
"""

import argparse
import os
import shutil
import sys


def extract_module(module_name: str, output_dir: str):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_app_dir = os.path.join(base_dir, "apps", module_name)

    if not os.path.exists(target_app_dir):
        print(f"❌ Error: Module '{module_name}' not found in apps/")
        sys.exit(1)

    dist_dir = os.path.join(base_dir, output_dir, f"aurastack-module-{module_name}")
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)

    print(f"📦 Extracting module '{module_name}' to {dist_dir}...")
    shutil.copytree(target_app_dir, dist_dir)

    readme_content = f"""# AuraStack Extracted Module: {module_name.upper()}

This standalone module was extracted from auraStack SaaS Engine.

## Quick Setup Instructions:

1. Copy this directory into your Django project's `apps/{module_name}`.
2. Add `'apps.{module_name}'` to your `INSTALLED_APPS` in `settings.py`.
3. Run `python manage.py migrate`.
"""
    with open(os.path.join(dist_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

    archive_format = "zip"
    archive_name = shutil.make_archive(dist_dir, archive_format, dist_dir)
    print(f"✅ Successfully created module package: {archive_name}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract AuraStack domain modules as standalone packages."
    )
    parser.add_argument(
        "--module",
        required=True,
        choices=["payments", "teams", "users", "blog"],
        help="Module name to extract",
    )
    parser.add_argument(
        "--output", default="dist", help="Output directory for generated module package"
    )
    args = parser.parse_args()

    extract_module(args.module, args.output)


if __name__ == "__main__":
    main()
