import subprocess
import sys

CODE_SOURCE_PATH = "flask_calendar/*.py"
TEST_SOURCE_PATH = "test"


def test_mypy_compliance() -> None:
    mypy_binary = subprocess.check_output("which mypy", shell=True, stderr=sys.stderr).decode("ascii").replace("\n", "")

    result = subprocess.call(
        "{} --config-file ./mypy.ini {}".format(mypy_binary, " ".join([CODE_SOURCE_PATH, TEST_SOURCE_PATH])),
        shell=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    assert result == 0
