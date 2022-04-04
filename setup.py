import os
import sys
from shutil import rmtree

from setuptools import Command, find_packages, setup

# -----------------------------------------------------------------------------

here = os.path.abspath(os.path.dirname(__file__))

# -----------------------------------------------------------------------------


class BaseCommand(Command):
    @staticmethod
    def status(s: str) -> None:
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))  # noqa: T001

    def system(self, command: str) -> None:
        os.system(command)  # noqa: S605

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class BuildCommand(BaseCommand):
    """Support setup.py building."""

    description = "Build the package."
    user_options = []

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        self.system("{0} -m build --sdist --wheel .".format(sys.executable))

        self.status("Checking wheel contents…")
        self.system("check-wheel-contents dist/*.whl")

        self.status("Running twine check…")
        self.system("{0} -m twine check dist/*".format(sys.executable))


class UploadTestCommand(BaseCommand):
    """Support uploading to test PyPI."""

    description = "Build the package."
    user_options = []

    def run(self):
        self.status("Uploading the package to PyPi via Twine…")
        self.system(
            "twine upload --repository-url https://test.pypi.org/legacy/ dist/*"
        )


class UploadCommand(BaseCommand):
    """Support uploading to PyPI."""

    description = "Build the package."
    user_options = []

    def run(self):
        self.status("Uploading the package to PyPi via Twine…")
        self.system("twine upload dist/*")


# -----------------------------------------------------------------------------

DESCRIPTION = "Python DB-API and SQLAlchemy interface for Airtable."

setup(
    name="sqlalchemy-airtable",
    version="0.0.1.dev0",
    description=DESCRIPTION,
    long_description=DESCRIPTION,
    author="Alex Rothberg",
    author_email="agrothberg@gmail.com",
    url="https://github.com/cancan101/airtable-db-api",
    packages=find_packages(exclude=("tests",)),
    entry_points={
        "sqlalchemy.dialects": [
            "airtable = airtabledb.dialect:APSWAirtableDialect",
        ],
        "shillelagh.adapter": [
            "airtable = airtabledb.adapter:AirtableAdapter",
        ],
        "superset.db_engine_specs": [
            "airtable = airtabledb.db_engine_specs:AirtableEngineSpec"
        ],
    },
    install_requires=(
        "pyairtable",
        "shillelagh >= 1.0.6",
        "sqlalchemy >= 1.3.0",
        "typing-extensions",
    ),
    license="MIT",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    # $ setup.py publish support.
    cmdclass={
        "buildit": BuildCommand,
        "uploadtest": UploadTestCommand,
        "upload": UploadCommand,
    },
)
