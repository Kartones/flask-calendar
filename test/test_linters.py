import subprocess
import sys

CODE_SOURCE_PATH = "flask_calendar/*.py"
TEST_SOURCE_PATH = "test"


def test_mypy_compliance() -> None:
    mypy_binary = subprocess.check_output("which mypy", shell=True, stderr=sys.stderr).decode("ascii").replace("\n", "")

    result = subprocess.call(
        "{} --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs"
        " --warn-redundant-casts --warn-return-any --warn-unused-ignores --strict-optional"
        " {}".format(mypy_binary, " ".join([CODE_SOURCE_PATH, TEST_SOURCE_PATH])),
        shell=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    assert result == 0
