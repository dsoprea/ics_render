"""Build static HTML pages from normalized calendar events."""

import html


def build_static_calendar_html_page(events):
    """Return a complete HTML document listing calendar events in time order."""

    table_body_rows = []

    # Build one table row per event with escaped cell text.
    for event in events:
        start_cell = html.escape(event["start"])
        stop_cell = html.escape(event["stop"])
        duration_cell = html.escape(event["duration"])
        name_text = html.escape(event["name"])
        description_text = event["description"]
        if description_text:
            description_attribute = html.escape(description_text, quote=True)
            name_cell = (
                '          <td title="{description}">{name}</td>'
            ).format(description=description_attribute, name=name_text)
        else:
            name_cell = "          <td>{name}</td>".format(name=name_text)

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
