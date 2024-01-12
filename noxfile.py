from __future__ import annotations

import os
from pathlib import Path

import nox

PY38 = "3.8"
PY39 = "3.9"
PY310 = "3.10"
PY311 = "3.11"
PY312 = "3.12"
PY_VERSIONS = [PY38, PY39, PY310, PY311, PY312]
PY_DEFAULT = PY_VERSIONS[0]
PY_LATEST = PY_VERSIONS[-1]

DJ32 = "3.2"
DJ42 = "4.2"
DJ50 = "5.0"
DJMAIN = "main"
DJMAIN_MIN_PY = PY310
DJ_VERSIONS = [DJ32, DJ42, DJ50, DJMAIN]
DJ_LTS = [DJ32, DJ42]
DJ_DEFAULT = DJ_LTS[-1]
DJ_LATEST = DJ_VERSIONS[-2]


def version(ver: str) -> tuple[int, ...]:
    """Convert a string version to a tuple of ints, e.g. "3.10" -> (3, 10)"""
    return tuple(map(int, ver.split(".")))


def should_skip(python: str, django: str) -> tuple[bool, str | None]:
    """Return True if the test should be skipped"""
    if django == DJMAIN and version(python) < version(DJMAIN_MIN_PY):
        return True, f"Django {DJMAIN} requires Python {DJMAIN_MIN_PY}+"

    if django == DJ32 and version(python) >= version(PY312):
        return True, f"Django {DJ32} requires Python < {PY312}"

    if django == DJ50 and version(python) < version(PY310):
        return True, f"Django {DJ50} requires Python {PY310}+"

    return False, None


@nox.session
def test(session):
    session.notify(f"tests(python='{PY_DEFAULT}', django='{DJ_DEFAULT}')")
    session.skip()


@nox.session
@nox.parametrize(
    "python,django",
    [
        (python, django)
        for python in PY_VERSIONS
        for django in DJ_VERSIONS
        if not should_skip(python, django)[0]
    ],
)
def tests(session, django):
    session.install(".[dev]")

    if django == DJMAIN:
        session.install("https://github.com/django/django/archive/refs/heads/main.zip")
    else:
        session.install(f"django=={django}")

    session.run("python", "-m", "pytest")


@nox.session
def coverage(session):
    session.install(".[dev]")
    session.run("python", "-m", "pytest", "--cov=django_twc_toolbox")

    try:
        summary = os.environ["GITHUB_STEP_SUMMARY"]
        with Path(summary).open("a") as output_buffer:
            output_buffer.write("")
            output_buffer.write("### Coverage\n\n")
            output_buffer.flush()
            session.run(
                "python",
                "-m",
                "coverage",
                "report",
                "--skip-covered",
                "--skip-empty",
                "--format=markdown",
                stdout=output_buffer,
            )
    except KeyError:
        session.run(
            "python", "-m", "coverage", "html", "--skip-covered", "--skip-empty"
        )

    session.run("python", "-m", "coverage", "report")


@nox.session
def lint(session):
    session.install(".[lint]")
    session.run("python", "-m", "pre_commit", "run", "--all-files")


@nox.session
def mypy(session):
    session.install(".[dev]")
    session.run("python", "-m", "mypy", ".")
