"""Tests for static HTML calendar page generation."""

import os

import ics_render.events
import ics_render.html_calendar

_FIXTURES_DIRECTORY = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "fixtures",
)


def test_build_static_calendar_html_page_includes_sorted_events():
    early_path = os.path.join(_FIXTURES_DIRECTORY, "early.ics")
    late_path = os.path.join(_FIXTURES_DIRECTORY, "late.ics")
    filepaths = [early_path, late_path]
    combined = ics_render.events.combine_events_gen(filepaths)

    document = ics_render.html_calendar.build_static_calendar_html_page(combined)

    assert "<!DOCTYPE html>" in document
    assert "<title>Calendar</title>" in document
    assert document.index("Morning standup") < document.index("All-day planning")
    assert document.index("All-day planning") < document.index("Release review")
    assert "0:30:00" in document
    assert "<th>Start</th>" in document
    assert "<th>Stop</th>" in document
    assert "2024-06-01T09:00:00+00:00" in document
    assert "2024-06-01T09:30:00+00:00" in document


def test_build_static_calendar_html_page_escapes_markup_in_names():
    events = [
        {
            "start": "2024-06-01T09:00:00+00:00",
            "stop": "2024-06-01T09:30:00+00:00",
            "duration": "0:30:00",
            "name": "<script>alert(1)</script>",
            "description": "",
            "sort_key": None,
        }
    ]

    document = ics_render.html_calendar.build_static_calendar_html_page(events)

    assert "<script>alert(1)</script>" not in document
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in document


def test_build_static_calendar_html_page_shows_description_tooltip():
    early_path = os.path.join(_FIXTURES_DIRECTORY, "early.ics")
    events = list(ics_render.events.get_events_from_file_gen(early_path))

    document = ics_render.html_calendar.build_static_calendar_html_page(events)

    assert 'title="Daily team sync"' in document
    assert "Morning standup" in document
