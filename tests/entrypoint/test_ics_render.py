"""Tests for the ics_render CLI entrypoint."""

import json
import os

import ics_render.entrypoint.ics_render

_FIXTURES_DIRECTORY = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "fixtures",
)


def test_main_jsonl_prints_sorted_events(capsys):
    early_path = os.path.join(_FIXTURES_DIRECTORY, "early.ics")
    argv = [
        "--jsonl",
        "--filepath",
        early_path,
    ]

    ics_render.entrypoint.ics_render.main(argv)
    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    parsed_events = []

    # Parse each JSONL line into a dict for assertion.
    for line in lines:
        parsed_events.append(json.loads(line))

    assert len(parsed_events) == 1
    assert parsed_events[0]["summary"]["value"] == "Morning standup"
    assert parsed_events[0]["start"]["value"] == "2024-06-01T09:00:00+00:00"


def test_main_html_list_prints_blocks(capsys):
    early_path = os.path.join(_FIXTURES_DIRECTORY, "early.ics")
    argv = [
        "--html-list",
        "--filepath",
        early_path,
    ]

    ics_render.entrypoint.ics_render.main(argv)
    captured = capsys.readouterr()

    assert '<article class="event-block">' in captured.out
    assert "<table>" not in captured.out
    assert 'title="Daily team sync"' in captured.out
    assert '<p class="event-description">Daily team sync</p>' in captured.out


def test_main_html_prints_month_grid(capsys):
    early_path = os.path.join(_FIXTURES_DIRECTORY, "early.ics")
    late_path = os.path.join(_FIXTURES_DIRECTORY, "late.ics")
    argv = [
        "--html",
        "--filepath",
        early_path,
        "--filepath",
        late_path,
    ]

    ics_render.entrypoint.ics_render.main(argv)
    captured = capsys.readouterr()

    assert '<table class="calendar-grid">' in captured.out
    assert "Morning standup" in captured.out
    assert "All-day planning" in captured.out
    assert "<th>Start</th>" not in captured.out


def test_main_html_table_prints_document(capsys):
    early_path = os.path.join(_FIXTURES_DIRECTORY, "early.ics")
    argv = [
        "--html-table",
        "--filepath",
        early_path,
    ]

    ics_render.entrypoint.ics_render.main(argv)
    captured = capsys.readouterr()

    assert "<!DOCTYPE html>" in captured.out
    assert "Morning standup" in captured.out
    assert "2024-06-01T09:00:00+00:00" in captured.out
    assert "2024-06-01T09:30:00+00:00" in captured.out
    assert 'title="Daily team sync"' in captured.out
