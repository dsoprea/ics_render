"""Load and normalize calendar events from ICS files."""

import datetime
import operator

import icalendar


def get_events_from_file_gen(filepath):
    """Yield event dicts with timestamp, name, and sort_key from one ICS file."""

    with open(filepath, "rb") as file_handle:
        raw_bytes = file_handle.read()
    calendar = icalendar.Calendar.from_ical(raw_bytes)

    # Walk the calendar tree and yield each VEVENT component.
    for component in calendar.walk():
        if component.name != "VEVENT":
            continue

        start_property = component.get("dtstart")
        if start_property is None:
            continue

        start_value = start_property.dt
        sort_key = _sort_key_for_start(start_value)
        timestamp_label = _format_start(start_value)
        duration_label = _duration_label_for_component(component, start_value)
        summary_property = component.get("summary")
        if summary_property is None:
            event_name = ""
        else:
            event_name = str(summary_property)

        yield {
            "timestamp": timestamp_label,
            "duration": duration_label,
            "name": event_name,
            "sort_key": sort_key,
        }


def combine_events_gen(filepaths):
    """Yield events from every filepath sorted by start timestamp."""

    combined = []

    # Load each file and append its events into one list.
    for filepath in filepaths:
        for event in get_events_from_file_gen(filepath):
            combined.append(event)

    combined.sort(key=operator.itemgetter("sort_key"))

    # Yield each event in sorted order.
    for event in combined:
        yield event


def get_events_as_table_rows_gen(events):
    """Yield (timestamp, duration, name) tuples for tabulate from event dicts."""

    # Project each event to the three display columns.
    for event in events:
        row = (event["timestamp"], event["duration"], event["name"])
        yield row


def _duration_label_for_component(component, start_value):
    duration_property = component.get("duration")
    if duration_property is not None:
        duration_timedelta = duration_property.dt
        return _format_timedelta(duration_timedelta)

    end_property = component.get("dtend")
    if end_property is not None:
        end_value = end_property.dt
        duration_timedelta = _timedelta_between(start_value, end_value)
        if duration_timedelta is not None:
            return _format_timedelta(duration_timedelta)

    return ""


def _timedelta_between(start_value, end_value):
    start_normalized = _normalize_for_duration_math(start_value)
    end_normalized = _normalize_for_duration_math(end_value)
    if start_normalized is None:
        return None
    if end_normalized is None:
        return None

    return end_normalized - start_normalized


def _normalize_for_duration_math(value):
    if isinstance(value, datetime.datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=datetime.timezone.utc)
        return value

    if isinstance(value, datetime.date):
        combined = datetime.datetime.combine(
            value,
            datetime.time.min,
            tzinfo=datetime.timezone.utc,
        )
        return combined

    return None


def _format_timedelta(delta):
    day_count = delta.days
    total_seconds = delta.seconds
    hours, leftover = divmod(total_seconds, 3600)
    minutes, seconds = divmod(leftover, 60)

    if day_count and not total_seconds:
        if day_count == 1:
            return "1 day"
        return "{day_count} days".format(day_count=day_count)

    time_portion = "{hours}:{minutes:02d}:{seconds:02d}".format(
        hours=day_count * 24 + hours,
        minutes=minutes,
        seconds=seconds,
    )
    if day_count:
        day_prefix = "{day_count} days, ".format(day_count=day_count)
        return day_prefix + time_portion

    return time_portion


def _sort_key_for_start(start_value):
    if isinstance(start_value, datetime.datetime):
        if start_value.tzinfo is None:
            return start_value.replace(tzinfo=datetime.timezone.utc)
        return start_value

    if isinstance(start_value, datetime.date):
        combined = datetime.datetime.combine(
            start_value,
            datetime.time.min,
            tzinfo=datetime.timezone.utc,
        )
        return combined

    message = "unsupported DTSTART type: {type_name}".format(
        type_name=type(start_value).__name__
    )
    raise TypeError(message)


def _format_start(start_value):
    if isinstance(start_value, datetime.datetime):
        if start_value.tzinfo is None:
            normalized = start_value.replace(tzinfo=datetime.timezone.utc)
        else:
            normalized = start_value
        return normalized.isoformat()

    if isinstance(start_value, datetime.date):
        return start_value.isoformat()

    message = "unsupported DTSTART type: {type_name}".format(
        type_name=type(start_value).__name__
    )
    raise TypeError(message)
