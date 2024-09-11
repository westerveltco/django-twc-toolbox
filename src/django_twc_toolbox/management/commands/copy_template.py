# Taken from https://github.com/softwarecrafts/django-cptemplate
#
# MIT License
#
# Copyright (c) 2024 Andrew Miller
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

from pathlib import Path
from shutil import copy2

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.template import loader


def get_template_absolute_path(template_path):
    try:
        template = loader.get_template(template_path)
        return template.origin.name  # type: ignore[attr-defined]
    except Exception as e:
        print(f"Error occurred while getting template path: {e}")
        return None


class Command(BaseCommand):
    help = "Copies a template from a package into your project"

    def add_arguments(self, parser):
        parser.add_argument("source", type=str)
        parser.add_argument("destination", type=str, nargs="?")

    def handle(self, *args, **options):
        print(options)
        # 1. extract the options
        source = options["source"]
        destination = options.get("destination")
        # 2. Check that the source file exists - use template loaders for this
        source_file = get_template_absolute_path(source)
        if source_file is None:
            self.stdout.write(self.style.ERROR("Source Template doesn't exist"))
            return
        base_dir = Path(settings.BASE_DIR)  # type: ignore[misc]
        # 4. if destination, then create Path object and copy
        if destination is not None:
            app_config = apps.get_app_config(destination)
            destination_path = base_dir / app_config.path / "templates" / source
        # 5/ else inspect TEMPLATES[DIRS] setting and use first option if available
        else:
            try:
                template_dir = Path(settings.TEMPLATES[0]["DIRS"][0])  # type: ignore[index]
                destination_path = template_dir / source
            except IndexError:
                # 6/ otherwise create project level template directory and dump file there.
                destination_path = base_dir / "templates" / source
                # PRINT what settings need to be modified
                self.stdout.write(
                    self.style.WARNING(
                        'Update TEMPLATES["DIRS"] to include the following entry "BASE_DIR / "templates","'
                    )
                )

        destination_path.parent.mkdir(parents=True, exist_ok=True)
        copy2(source_file, destination_path)
