from datetime import datetime, timedelta
import os
from pathlib import Path
from unittest import mock
from zoneinfo import ZoneInfo
from pyfakefs.fake_filesystem_unittest import Patcher
import pytest
import time_machine

from timcol.tool.main import main

test_tz_name = "America/Los_Angeles"
test_tz = ZoneInfo(test_tz_name)

timcol_home = Path("/timcol-home")
ledger_path = timcol_home / "ledger.dat"


@pytest.fixture(autouse=True)
def mock_fs():
    with mock.patch.dict(
        os.environ, {"TIMCOL_HOME": str(timcol_home), "TZ": test_tz_name}
    ), Patcher() as patcher:
        fs = patcher.fs
        assert fs
        fs.create_dir("/timcol-home")

        yield


@pytest.fixture()
def mock_time():
    with time_machine.travel(
        datetime(2023, 7, 30, 10, 1, 12, tzinfo=test_tz), tick=False
    ) as traveller:
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


def test_backfill(mock_time):
    main(
        [
            "backfill",
            "BackfillAccount",
            "Backfill task",
            "2023/07/30 09:00:00",
            "1h 30m",
        ]
    )

    with ledger_path.open("r") as f:
        ledger_contents = f.read()

    expected_contents = """i 2023/07/30 09:00:00 AM BackfillAccount  Backfill task
o 2023/07/30 10:30:00 AM
"""
    assert ledger_contents == expected_contents


def test_backfill_multiple_tasks(mock_time):
    main(["backfill", "Account1", "Task 1", "2023/07/30 09:00:00", "1h"])
    main(["backfill", "Account2", "Task 2", "2023/07/30 10:30:00", "45m"])

    with ledger_path.open("r") as f:
        ledger_contents = f.read()

    expected_contents = """i 2023/07/30 09:00:00 AM Account1  Task 1
o 2023/07/30 10:00:00 AM
i 2023/07/30 10:30:00 AM Account2  Task 2
o 2023/07/30 11:15:00 AM
"""
    assert ledger_contents == expected_contents
