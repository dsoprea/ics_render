"""Build static HTML pages from normalized calendar events."""

import html


def _build_html_name_title_attribute(event):
    description_text = event["description"]
    if description_text:
        description_escaped = html.escape(description_text, quote=True)
        return ' title="{description}"'.format(description=description_escaped)
    return ""


def _build_html_name_heading(event):
    name_text = html.escape(event["name"])
    title_attribute = _build_html_name_title_attribute(event)
    return '<h2 class="event-name"{title}>{name}</h2>'.format(
        title=title_attribute,
        name=name_text,
    )


def _build_html_name_table_cell(event):
    name_text = html.escape(event["name"])
    title_attribute = _build_html_name_title_attribute(event)
    return "          <td{title}>{name}</td>".format(
        title=title_attribute,
        name=name_text,
    )


def _format_html_description_body(description_text):
    description_lines = description_text.splitlines()
    escaped_lines = []

    # Escape each line, then join with line breaks for HTML display.
    for line in description_lines:
        escaped_lines.append(html.escape(line))

    return "<br />".join(escaped_lines)


def _build_html_description_paragraph(event):
    description_text = event["description"]
    if not description_text:
        return ""

    description_body = _format_html_description_body(description_text)
    return (
        '      <p class="event-description">{description}</p>\n'
    ).format(description=description_body)


def build_static_calendar_html_list_page(events):
    """Return a complete HTML document with one block per calendar event."""

    event_blocks = []

    # Build one spaced block per event with start, stop, and duration.
    for event in events:
        start_text = html.escape(event["start"])
        stop_text = html.escape(event["stop"])
        duration_text = html.escape(event["duration"])
        name_heading = _build_html_name_heading(event)
        description_paragraph = _build_html_description_paragraph(event)
        block_html = (
            '    <article class="event-block">\n'
            "      {name_heading}\n"
            '      <p class="event-detail"><span class="event-label">Start:</span> {start}</p>\n'
            '      <p class="event-detail"><span class="event-label">Stop:</span> {stop}</p>\n'
            '      <p class="event-detail"><span class="event-label">Duration:</span> {duration}</p>\n'
            "{description_paragraph}"
            "    </article>"
        ).format(
            name_heading=name_heading,
            start=start_text,
            stop=stop_text,
            duration=duration_text,
            description_paragraph=description_paragraph,
        )
        event_blocks.append(block_html)

    if event_blocks:
        events_body_html = "\n".join(event_blocks)
    else:
        events_body_html = '    <p class="no-events">No events</p>'

    document_prefix = (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "  <title>Calendar</title>\n"
        "  <style>\n"
        "    body {\n"
        "      font-family: system-ui, sans-serif;\n"
        "      line-height: 1.5;\n"
        "      margin: 2rem;\n"
        "      color: #1a1a1a;\n"
        "      background: #fafafa;\n"
        "    }\n"
        "    h1 {\n"
        "      font-size: 1.5rem;\n"
        "      margin-bottom: 1rem;\n"
        "    }\n"
        "    .event-block {\n"
        "      background: #fff;\n"
        "      border: 1px solid #ddd;\n"
        "      padding: 1rem 1.25rem;\n"
        "      margin-bottom: 1.25rem;\n"
        "      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);\n"
        "    }\n"
        "    .event-block:last-child {\n"
        "      margin-bottom: 0;\n"
        "    }\n"
        "    .event-name {\n"
        "      font-size: 1.1rem;\n"
        "      margin: 0 0 0.5rem;\n"
        "    }\n"
        "    .event-detail {\n"
        "      margin: 0.25rem 0;\n"
        "    }\n"
        "    .event-label {\n"
        "      font-weight: 600;\n"
        "    }\n"
        "    .event-description {\n"
        "      margin: 0.75rem 0 0;\n"
        "      color: #444;\n"
        "    }\n"
        "    .no-events {\n"
        "      color: #555;\n"
        "    }\n"
        "  </style>\n"
        "</head>\n"
        "<body>\n"
        "  <h1>Calendar</h1>\n"
        "  <div class=\"event-list\">\n"
    )
    document_suffix = (
        "  </div>\n"
        "</body>\n"
        "</html>\n"
    )
    document = document_prefix + events_body_html + "\n" + document_suffix

    return document


def build_static_calendar_html_page(events):
    """Return a complete HTML document listing calendar events in time order."""

    table_body_rows = []

    # Build one table row per event with escaped cell text.
    for event in events:
        start_cell = html.escape(event["start"])
        stop_cell = html.escape(event["stop"])
        duration_cell = html.escape(event["duration"])
        name_cell = _build_html_name_table_cell(event)

        row_html = (
            "        <tr>\n"
            "          <td>{start}</td>\n"
            "          <td>{stop}</td>\n"
            "          <td>{duration}</td>\n"
            "{name_cell}\n"
            "        </tr>"
        ).format(
            start=start_cell,
            stop=stop_cell,
            duration=duration_cell,
            name_cell=name_cell,
        )
        table_body_rows.append(row_html)

    if table_body_rows:
        table_body_html = "\n".join(table_body_rows)
    else:
        table_body_html = (
            "        <tr>\n"
            '          <td colspan="4">No events</td>\n'
            "        </tr>"
        )

    document_prefix = (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "  <title>Calendar</title>\n"
        "  <style>\n"
        "    body {\n"
        "      font-family: system-ui, sans-serif;\n"
        "      line-height: 1.5;\n"
        "      margin: 2rem;\n"
        "      color: #1a1a1a;\n"
        "      background: #fafafa;\n"
        "    }\n"
        "    h1 {\n"
        "      font-size: 1.5rem;\n"
        "      margin-bottom: 1rem;\n"
        "    }\n"
        "    table {\n"
        "      width: 100%;\n"
        "      border-collapse: collapse;\n"
        "      background: #fff;\n"
        "      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);\n"
        "    }\n"
        "    th,\n"
        "    td {\n"
        "      border: 1px solid #ddd;\n"
        "      padding: 0.5rem 0.75rem;\n"
        "      text-align: left;\n"
        "      vertical-align: top;\n"
        "    }\n"
        "    th {\n"
        "      background: #f0f0f0;\n"
        "    }\n"
        "    tbody tr:nth-child(even) {\n"
        "      background: #f9f9f9;\n"
        "    }\n"
        "  </style>\n"
        "</head>\n"
        "<body>\n"
        "  <h1>Calendar</h1>\n"
        "  <table>\n"
        "    <thead>\n"
        "      <tr>\n"
        "        <th>Start</th>\n"
        "        <th>Stop</th>\n"
        "        <th>Duration</th>\n"
        "        <th>Name</th>\n"
        "      </tr>\n"
        "    </thead>\n"
        "    <tbody>\n"
    )
    document_suffix = (
        "    </tbody>\n"
        "  </table>\n"
        "</body>\n"
        "</html>\n"
    )
    document = document_prefix + table_body_html + "\n" + document_suffix

    return document
