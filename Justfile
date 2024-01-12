set dotenv-load := true

@_default:
    just --list

##################
#  DEPENDENCIES  #
##################

bootstrap:
    python -m pip install --editable '.[dev]'

pup:
    python -m pip install --upgrade pip

update:
    @just pup
    @just bootstrap

##################
#  TESTING/TYPES #
##################

test:
    python -m nox --reuse-existing-virtualenvs --session "test"

test-all:
    python -m nox --reuse-existing-virtualenvs --session "tests"

coverage:
    python -m nox --reuse-existing-virtualenvs --session "coverage"

types:
    python -m nox --reuse-existing-virtualenvs --session "mypy"

##################
#     DJANGO     #
##################

manage *COMMAND:
    #!/usr/bin/env python
    import sys

    try:
        from django.conf import settings
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    settings.configure(INSTALLED_APPS=["django_twc_toolbox"])
    execute_from_command_line(sys.argv + "{{ COMMAND }}".split(" "))

alias mm := makemigrations

makemigrations *APPS:
    @just manage makemigrations {{ APPS }}

migrate *ARGS:
    @just manage migrate {{ ARGS }}

shell:
    @just manage shell_plus

createsuperuser USERNAME="admin" EMAIL="" PASSWORD="admin":
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('{{ USERNAME }}', '{{ EMAIL }}', '{{ PASSWORD }}') if not User.objects.filter(username='{{ USERNAME }}').exists() else None" | python manage.py shell

##################
#     DOCS       #
##################

@docs-install:
    python -m pip install '.[docs]'

@docs-serve:
    #!/usr/bin/env sh
    if [ -f "/.dockerenv" ]; then
        sphinx-autobuild docs docs/_build/html --host "0.0.0.0"
    else
        sphinx-autobuild docs docs/_build/html --host "localhost"
    fi

@docs-build LOCATION="docs/_build/html":
    sphinx-build docs {{ LOCATION }}

##################
#     UTILS      #
##################

lint:
    python -m nox --reuse-existing-virtualenvs --session "lint"

mypy:
    python -m nox --reuse-existing-virtualenvs --session "mypy"
