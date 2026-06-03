"""Tests for ICS event loading and sorting."""

import json
import os

import ics_render.events

_FIXTURES_DIRECTORY = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "fixtures",
)


def test_combine_events_gen_sorts_across_files():
    early_path = os.path.join(_FIXTURES_DIRECTORY, "early.ics")
    late_path = os.path.join(_FIXTURES_DIRECTORY, "late.ics")
    filepaths = [str(early_path), str(late_path)]

    combined = ics_render.events.combine_events_gen(filepaths)
    names = []

    # Collect names in sorted order for assertion.
    for event in combined:
        names.append(event["name"])

    assert names == [
        "Morning standup",
        "All-day planning",
        "Release review",
    ]


def test_get_events_as_table_rows_gen_projects_columns():
    events = [
        {
            "timestamp": "2024-06-01T09:00:00+00:00",
            "duration": "0:30:00",
            "name": "Morning standup",
            "sort_key": None,
        }
    ]

    rows = list(ics_render.events.get_events_as_table_rows_gen(events))

    assert rows == [
        ("2024-06-01T09:00:00+00:00", "0:30:00", "Morning standup"),
    ]


def test_get_events_as_jsonl_lines_gen_serializes_ics_record():
    early_path = os.path.join(_FIXTURES_DIRECTORY, "early.ics")
    events = list(ics_render.events.get_events_from_file_gen(early_path))

    lines = list(ics_render.events.get_events_as_jsonl_lines_gen(events))
    parsed = json.loads(lines[0])

    assert parsed["summary"]["value"] == "Morning standup"
    assert parsed["start"]["value"] == "2024-06-01T09:00:00+00:00"
    assert parsed["end"]["value"] == "2024-06-01T09:30:00+00:00"
    assert parsed["uid"]["value"] == "early-1@example"


def test_ics_record_uses_friendly_keys_for_date_parameters():
    late_path = os.path.join(_FIXTURES_DIRECTORY, "late.ics")
    events = list(ics_render.events.get_events_from_file_gen(late_path))
    all_day_event = None

    # Find the all-day VEVENT in the fixture file.
    for event in events:
        if event["name"] == "All-day planning":
            all_day_event = event
            break

    assert all_day_event is not None
    assert all_day_event["ics_record"]["start"]["parameters"]["value"] == "DATE"
    assert all_day_event["ics_record"]["start"]["value"] == "2024-06-10"


def test_get_events_from_file_gen_reads_duration_from_dtend():
    early_path = os.path.join(_FIXTURES_DIRECTORY, "early.ics")
    events = list(ics_render.events.get_events_from_file_gen(early_path))

    assert len(events) == 1
    assert events[0]["duration"] == "0:30:00"
