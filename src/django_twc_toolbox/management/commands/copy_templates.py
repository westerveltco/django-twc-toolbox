from __future__ import annotations

import asyncio
import os
from pathlib import Path
from shutil import copy2
from typing import cast

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.template import loader
from django.template.utils import get_app_template_dirs


def get_template_path(template_path: str, target_app: str | None = None) -> Path | None:
    try:
        if target_app:
            app_config = apps.get_app_config(target_app)
            template_dirs = [Path(app_config.path) / "templates"]
        else:
            template_dirs = list(get_app_template_dirs("templates"))
            template_dirs.extend(settings.TEMPLATES[0]["DIRS"])

        template_dirs = cast(list[Path], template_dirs)

        for template_dir in template_dirs:
            full_path = Path(template_dir) / template_path
            if full_path.is_file():
                return full_path
            elif full_path.is_dir():
                return full_path

        # If not found in specific dirs, try the default template loader
        template = loader.get_template(template_path)
        return Path(template.origin.name)
    except Exception as e:
        print(f"Error occurred while getting template path: {e}")
        return None


class Command(BaseCommand):
    help = (
        "Copies a template or a directory of templates from a package into your project"
    )

    def add_arguments(self, parser):
        parser.add_argument("source", type=str)
        parser.add_argument("destination", type=str, nargs="?")
        parser.add_argument(
            "--app", type=str, help="Specify the source app for the template"
        )

    def handle(self, *args, **options):
        source = options["source"]
        destination = options.get("destination")
        target_app = options.get("app")
        base_dir = Path(settings.BASE_DIR)

        if destination is not None:
            app_config = apps.get_app_config(destination)
            destination_path = base_dir / app_config.path / "templates"
        else:
            try:
                destination_path = Path(settings.TEMPLATES[0]["DIRS"][0])
            except IndexError:
                destination_path = base_dir / "templates"
                self.stdout.write(
                    self.style.WARNING(
                        'Update TEMPLATES["DIRS"] to include the following entry "BASE_DIR / "templates","'
                    )
                )

        source_path = get_template_path(source, target_app)
        if source_path is None:
            self.stdout.write(self.style.ERROR("Source doesn't exist"))
            return

        asyncio.run(self.process_source(source_path, destination_path, source))

    async def process_source(self, source_path, destination_path, original_source):
        if source_path.is_file():
            await self.copy_template(source_path, destination_path / original_source)
        elif source_path.is_dir():
            await self.copy_directory(source_path, destination_path / original_source)
        else:
            self.stdout.write(
                self.style.ERROR("Source is neither a file nor a directory")
            )

    async def copy_template(self, source, destination):
        destination.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(copy2, source, destination)
        self.stdout.write(self.style.SUCCESS(f"Copied {source} to {destination}"))

    async def copy_directory(self, source_dir, destination_dir):
        tasks = []
        for root, _, files in os.walk(source_dir):
            for file in files:
                rel_path = os.path.relpath(root, source_dir)
                source_file = Path(root) / file
                dest_file = destination_dir / rel_path / file
                tasks.append(self.copy_template(source_file, dest_file))

        if tasks:
            await asyncio.gather(*tasks)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Copied all templates from {source_dir} to {destination_dir}"
                )
            )
        else:
            self.stdout.write(self.style.WARNING(f"No files found in {source_dir}"))
