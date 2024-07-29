from datetime import timedelta
import os
from pathlib import Path
from unittest import mock
from pyfakefs.fake_filesystem_unittest import Patcher
import pytest
import time_machine

from timcol.tool.main import main

timcol_home = Path("/timcol-home")
ledger_path = timcol_home / "ledger.dat"


@pytest.fixture(autouse=True)
def mock_fs():
    with mock.patch.dict(
        os.environ, {"TIMCOL_HOME": str(timcol_home)}
    ), Patcher() as patcher:
        fs = patcher.fs
        assert fs
        fs.create_dir("/timcol-home")

        yield


@pytest.fixture()
def mock_time():
    with time_machine.travel("2023/07/30 10:01:12", tick=False) as traveller:
        yield traveller


def test_task_lifecycle(mock_time):
    main(["start", "TestAccount", "Test task"])

    mock_time.move_to(timedelta(hours=1))

    main(["stop"])

    with ledger_path.open("r") as f:
        ledger_contents = f.read()

    expected_contents = """i 2023/07/30 10:01:12 AM TestAccount  Test task
o 2023/07/30 11:01:12 AM
"""
    assert ledger_contents == expected_contents
