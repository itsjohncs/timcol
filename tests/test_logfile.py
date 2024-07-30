import datetime
import io
from timcol.logfile import directive, parse_file, LogFile


def test_checkin_parse():
    valid_checkin = "i 2023/07/30 10:00:00 AM TestAccount  Test task"
    parsed_checkin = directive.CheckIn.parse(valid_checkin)

    expected_checkin = directive.CheckIn(
        timestamp=datetime.datetime(2023, 7, 30, 10, 0, 0),
        account="TestAccount",
        task="Test task",
    )
    assert parsed_checkin == expected_checkin

    invalid_checkin = "invalid checkin format"
    assert directive.CheckIn.parse(invalid_checkin) is None


def test_checkout_parse():
    valid_checkout = "o 2023/07/30 11:00:00 AM"
    parsed_checkout = directive.CheckOut.parse(valid_checkout)

    expected_checkout = directive.CheckOut(
        timestamp=datetime.datetime(2023, 7, 30, 11, 0, 0)
    )
    assert parsed_checkout == expected_checkout

    invalid_checkout = "invalid checkout format"
    assert directive.CheckOut.parse(invalid_checkout) is None


def test_parse_file():
    log_content = """
i 2023/07/30 10:00:00 AM TestAccount  Test task 1
    ; metadata1: value1
o 2023/07/30 11:00:00 AM
    ; metadata2: value2
i 2023/07/30 12:00:00 PM TestAccount  Test task 2
o 2023/07/30 01:00:00 PM
i 2023/07/30 02:00:00 PM TestAccount  Pending task
"""
    log_file = io.StringIO(log_content.strip())
    parsed_log = parse_file(log_file)

    assert isinstance(parsed_log, LogFile)
    assert len(parsed_log.entries) == 2
    assert parsed_log.pending is not None

    # Check first entry
    expected_check_in_1 = directive.CheckIn(
        timestamp=datetime.datetime(2023, 7, 30, 10, 0, 0),
        account="TestAccount",
        task="Test task 1",
    )
    expected_check_in_1.metadata = {"metadata1": "value1"}
    expected_check_out_1 = directive.CheckOut(
        timestamp=datetime.datetime(2023, 7, 30, 11, 0, 0)
    )
    expected_check_out_1.metadata = {"metadata2": "value2"}
    assert parsed_log.entries[0].check_in == expected_check_in_1
    assert parsed_log.entries[0].check_out == expected_check_out_1

    # Check second entry
    expected_check_in_2 = directive.CheckIn(
        timestamp=datetime.datetime(2023, 7, 30, 12, 0, 0),
        account="TestAccount",
        task="Test task 2",
    )
    expected_check_out_2 = directive.CheckOut(
        timestamp=datetime.datetime(2023, 7, 30, 13, 0, 0)
    )
    assert parsed_log.entries[1].check_in == expected_check_in_2
    assert parsed_log.entries[1].check_out == expected_check_out_2

    # Check pending task
    expected_pending = directive.CheckIn(
        timestamp=datetime.datetime(2023, 7, 30, 14, 0, 0),
        account="TestAccount",
        task="Pending task",
    )
    assert parsed_log.pending == expected_pending
