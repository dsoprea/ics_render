"""Tests for static HTML calendar page generation."""

import datetime
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


def test_build_static_calendar_html_list_page_renders_spaced_blocks():
    early_path = os.path.join(_FIXTURES_DIRECTORY, "early.ics")
    late_path = os.path.join(_FIXTURES_DIRECTORY, "late.ics")
    filepaths = [early_path, late_path]
    combined = ics_render.events.combine_events_gen(filepaths)

    document = ics_render.html_calendar.build_static_calendar_html_list_page(
        combined
    )

    assert '<article class="event-block">' in document
    assert "event-list" in document
    assert "<table>" not in document
    assert document.count('<article class="event-block">') == 3
    assert "Morning standup" in document
    assert "Start:" in document
    assert "Stop:" in document


def test_build_static_calendar_html_list_page_converts_description_newlines_to_br():
    events = [
        {
            "start": "2024-06-01T09:00:00+00:00",
            "stop": "2024-06-01T09:30:00+00:00",
            "duration": "0:30:00",
            "name": "Morning standup",
            "description": "Daily team sync\nAgenda review",
            "sort_key": None,
        }
    ]

    document = ics_render.html_calendar.build_static_calendar_html_list_page(events)

    assert (
        '<p class="event-description">Daily team sync<br />Agenda review</p>'
        in document
    )


def test_build_static_calendar_html_list_page_shows_description_tooltip():
    early_path = os.path.join(_FIXTURES_DIRECTORY, "early.ics")
    events = list(ics_render.events.get_events_from_file_gen(early_path))

    document = ics_render.html_calendar.build_static_calendar_html_list_page(events)

    assert 'title="Daily team sync"' in document
    assert '<h2 class="event-name"' in document
    assert '<p class="event-description">Daily team sync</p>' in document


def test_build_static_calendar_html_grid_page_renders_month_grid():
    early_path = os.path.join(_FIXTURES_DIRECTORY, "early.ics")
    late_path = os.path.join(_FIXTURES_DIRECTORY, "late.ics")
    filepaths = [early_path, late_path]
    combined = ics_render.events.combine_events_gen(filepaths)

    document = ics_render.html_calendar.build_static_calendar_html_grid_page(
        combined
    )

    assert '<table class="calendar-grid">' in document
    assert '<h2 class="month-heading">June 2024</h2>' in document
    assert "Morning standup" in document
    assert "All-day planning" in document
    assert "Release review" in document
    assert "09:00" in document
    assert "<th>Start</th>" not in document


def test_build_static_calendar_html_grid_page_shows_month_selector_for_multiple_months():
    events = [
        {
            "start": "2024-06-01T09:00:00+00:00",
            "stop": "2024-06-01T09:30:00+00:00",
            "duration": "0:30:00",
            "name": "June event",
            "description": "",
            "sort_key": datetime.datetime(
                2024, 6, 1, 9, 0, tzinfo=datetime.timezone.utc
            ),
        },
        {
            "start": "2024-07-15T14:00:00+00:00",
            "stop": "2024-07-15T15:00:00+00:00",
            "duration": "1:00:00",
            "name": "July event",
            "description": "",
            "sort_key": datetime.datetime(
                2024, 7, 15, 14, 0, tzinfo=datetime.timezone.utc
            ),
        },
    ]

    document = ics_render.html_calendar.build_static_calendar_html_grid_page(
        events
    )

    assert 'id="month-select"' in document
    assert 'value="month-2024-06"' in document
    assert 'value="month-2024-07"' in document
    assert "has-month-select" in document
    assert 'class="month-calendar is-active"' in document
    assert "sync_month_select_to_calendar" in document
    assert 'window.addEventListener("pageshow", sync_month_select_to_calendar)' in document
    assert "June event" in document
    assert "July event" in document
    assert '<h2 class="month-heading">' not in document


def test_build_static_calendar_html_grid_page_includes_event_modal():
    early_path = os.path.join(_FIXTURES_DIRECTORY, "early.ics")
    events = list(ics_render.events.get_events_from_file_gen(early_path))

    document = ics_render.html_calendar.build_static_calendar_html_grid_page(
        events
    )

    assert 'id="event-modal"' in document
    assert 'class="event-modal-dialog"' in document
    assert 'class="event-modal-copy-description"' in document
    assert "copy_description_to_clipboard" in document
    assert 'id="copy-toast"' in document
    assert "show_copied_toast" in document
    assert 'hidden>Copied</div>' in document
    assert "copy_toast.hidden = false" in document
    assert 'data-event-name="Morning standup"' in document
    assert 'data-event-start="2024-06-01T09:00:00+00:00"' in document
    assert 'data-event-description="Daily team sync"' in document
    assert "open_event_modal" in document
    assert 'role="button"' in document


def test_build_static_calendar_html_grid_page_escapes_markup_in_event_data():
    events = [
        {
            "start": "2024-06-01T09:00:00+00:00",
            "stop": "2024-06-01T09:30:00+00:00",
            "duration": "0:30:00",
            "name": '<script>alert("x")</script>',
            "description": 'Say "hello"',
            "sort_key": datetime.datetime(
                2024, 6, 1, 9, 0, tzinfo=datetime.timezone.utc
            ),
        }
    ]

    document = ics_render.html_calendar.build_static_calendar_html_grid_page(
        events
    )

    assert "<script>alert" not in document
    assert "&lt;script&gt;alert" in document
    assert 'data-event-description="Say &quot;hello&quot;"' in document


def test_build_static_calendar_html_page_shows_description_tooltip():
    early_path = os.path.join(_FIXTURES_DIRECTORY, "early.ics")
    events = list(ics_render.events.get_events_from_file_gen(early_path))

    document = ics_render.html_calendar.build_static_calendar_html_page(events)

    assert 'title="Daily team sync"' in document
    assert "Morning standup" in document
