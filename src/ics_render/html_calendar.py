"""Build static HTML pages from normalized calendar events."""

import calendar
import datetime
import html
import operator


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


def _get_calendar_date_from_event(event):
    sort_key = event["sort_key"]
    if isinstance(sort_key, datetime.datetime):
        return sort_key.date()
    return None


def _format_calendar_event_time_prefix(event):
    start_label = event["start"]
    if "T" not in start_label:
        return ""

    sort_key = event["sort_key"]
    if not isinstance(sort_key, datetime.datetime):
        return ""

    time_text = sort_key.strftime("%H:%M")
    return "{time} ".format(time=time_text)


def _group_events_by_year_and_month(events):
    events_by_year_and_month = {}

    # Bucket each event under its start date year and month.
    for event in events:
        calendar_date = _get_calendar_date_from_event(event)
        if calendar_date is None:
            continue

        year_and_month = (calendar_date.year, calendar_date.month)
        if year_and_month not in events_by_year_and_month:
            events_by_year_and_month[year_and_month] = []
        events_by_year_and_month[year_and_month].append(event)

    grouped = []
    for year_and_month in sorted(events_by_year_and_month):
        grouped.append((year_and_month, events_by_year_and_month[year_and_month]))

    return grouped


def _index_events_by_day_of_month(month_events):
    events_by_day = {}

    # Map day-of-month to the events that start on that day.
    for event in month_events:
        calendar_date = _get_calendar_date_from_event(event)
        if calendar_date is None:
            continue

        day_number = calendar_date.day
        if day_number not in events_by_day:
            events_by_day[day_number] = []
        events_by_day[day_number].append(event)

    for day_number in events_by_day:
        events_by_day[day_number].sort(key=operator.itemgetter("sort_key"))

    return events_by_day


def _build_calendar_event_detail_attributes(event):
    attribute_pairs = (
        ("data-event-name", event["name"]),
        ("data-event-start", event["start"]),
        ("data-event-stop", event["stop"]),
        ("data-event-duration", event["duration"]),
        ("data-event-description", event["description"]),
    )
    attribute_parts = []

    # Encode event fields for the click-to-open detail modal.
    for attribute_name, attribute_value in attribute_pairs:
        escaped_value = html.escape(attribute_value, quote=True)
        attribute_parts.append(
            '{name}="{value}"'.format(
                name=attribute_name,
                value=escaped_value,
            )
        )

    return " " + " ".join(attribute_parts)


def _build_calendar_day_events_html(day_events):
    if not day_events:
        return ""

    event_items = []

    # Render one clickable list item per event with detail data attributes.
    for event in day_events:
        name_text = html.escape(event["name"])
        time_prefix = _format_calendar_event_time_prefix(event)
        detail_attributes = _build_calendar_event_detail_attributes(event)
        item_html = (
            '                <li class="calendar-event" role="button" tabindex="0"'
            "{detail_attributes}>{time}{name}</li>"
        ).format(
            detail_attributes=detail_attributes,
            time=html.escape(time_prefix),
            name=name_text,
        )
        event_items.append(item_html)

    items_body = "\n".join(event_items)
    return (
        '              <ul class="day-events">\n'
        "{items}\n"
        "              </ul>"
    ).format(items=items_body)


def _build_calendar_week_row_html(week_days, events_by_day):
    day_cells = []

    # Emit one table cell per weekday, including padding for outside-month days.
    for day_number in week_days:
        if day_number == 0:
            day_cells.append(
                '        <td class="padding-day">\n'
                '          <div class="day-cell-frame"></div>\n'
                "        </td>"
            )
            continue

        day_events = events_by_day.get(day_number, [])
        day_events_html = _build_calendar_day_events_html(day_events)
        if day_events_html:
            events_block = "\n" + day_events_html + "\n"
        else:
            events_block = ""

        cell_html = (
            '        <td class="day-cell">\n'
            '          <div class="day-cell-frame">\n'
            '            <div class="day-cell-content">\n'
            '              <span class="day-number">{day}</span>{events}\n'
            "            </div>\n"
            "          </div>\n"
            "        </td>"
        ).format(
            day=day_number,
            events=events_block,
        )
        day_cells.append(cell_html)

    return "      <tr>\n" + "\n".join(day_cells) + "\n      </tr>"


def _build_month_section_id(year, month):
    return "month-{year}-{month:02d}".format(year=year, month=month)


def _build_month_heading_label(year, month):
    month_name = calendar.month_name[month]
    return "{month_name} {year}".format(month_name=month_name, year=year)


def _build_month_selector_html(grouped_months):
    option_lines = []

    # Build one select option per month that has events.
    for index, year_and_month in enumerate(grouped_months):
        year, month = year_and_month
        section_id = _build_month_section_id(year, month)
        option_label = html.escape(_build_month_heading_label(year, month))
        selected_attribute = ""
        if index == 0:
            selected_attribute = " selected"
        option_lines.append(
            '      <option value="{section_id}"{selected}>{label}</option>'.format(
                section_id=section_id,
                selected=selected_attribute,
                label=option_label,
            )
        )

    options_body = "\n".join(option_lines)
    return (
        '  <div class="month-select-row">\n'
        '    <label for="month-select">Month</label>\n'
        '    <select id="month-select" class="month-select">\n'
        "{options}\n"
        "    </select>\n"
        "  </div>"
    ).format(options=options_body)


def _build_calendar_month_section_html(
    year,
    month,
    month_events,
    is_active=False,
    include_heading=True,
):
    events_by_day = _index_events_by_day_of_month(month_events)
    month_calendar = calendar.Calendar(firstweekday=calendar.SUNDAY)
    weeks = month_calendar.monthdayscalendar(year, month)
    week_rows = []

    # Build one table row per week in the month grid.
    for week_days in weeks:
        week_rows.append(_build_calendar_week_row_html(week_days, events_by_day))

    weeks_body = "\n".join(week_rows)
    section_id = _build_month_section_id(year, month)
    active_class = ""
    if is_active:
        active_class = " is-active"

    heading_html = ""
    if include_heading:
        month_heading = html.escape(_build_month_heading_label(year, month))
        heading_html = '    <h2 class="month-heading">{heading}</h2>\n'.format(
            heading=month_heading
        )

    return (
        '  <section class="month-calendar{active_class}" id="{section_id}">\n'
        "{heading_html}"
        '    <table class="calendar-grid">\n'
        "      <thead>\n"
        "        <tr>\n"
        "          <th>Sun</th>\n"
        "          <th>Mon</th>\n"
        "          <th>Tue</th>\n"
        "          <th>Wed</th>\n"
        "          <th>Thu</th>\n"
        "          <th>Fri</th>\n"
        "          <th>Sat</th>\n"
        "        </tr>\n"
        "      </thead>\n"
        "      <tbody>\n"
        "{weeks}\n"
        "      </tbody>\n"
        "    </table>\n"
        "  </section>"
    ).format(
        active_class=active_class,
        section_id=section_id,
        heading_html=heading_html,
        weeks=weeks_body,
    )


def _build_event_modal_html():
    return (
        '  <div id="event-modal" class="event-modal">\n'
        '    <div class="event-modal-backdrop"></div>\n'
        '    <div class="event-modal-dialog" role="dialog" aria-modal="true"'
        ' aria-labelledby="event-modal-title">\n'
        '      <button type="button" class="event-modal-close"'
        ' aria-label="Close">&times;</button>\n'
        '      <h2 id="event-modal-title" class="event-modal-title"></h2>\n'
        '      <dl class="event-modal-details">\n'
        '        <dt>Start</dt>\n'
        '        <dd class="event-modal-start"></dd>\n'
        '        <dt>Stop</dt>\n'
        '        <dd class="event-modal-stop"></dd>\n'
        '        <dt>Duration</dt>\n'
        '        <dd class="event-modal-duration"></dd>\n'
        "      </dl>\n"
        '      <div class="event-modal-description-block">\n'
        '        <div class="event-modal-description-row">\n'
        '          <p class="event-modal-description"></p>\n'
        '          <button type="button" class="event-modal-copy-description"'
        ' aria-label="Copy description">Copy</button>\n'
        "        </div>\n"
        "      </div>\n"
        '      <div id="copy-toast" class="copy-toast" role="status"'
        ' aria-live="polite" hidden>Copied</div>\n'
        "    </div>\n"
        "  </div>"
    )


def _build_calendar_grid_script_html(include_month_select):
    month_select_block = ""
    if include_month_select:
        month_select_block = (
            '      var month_select = document.getElementById("month-select");\n'
            "\n"
            "      function show_month_section(selected_id) {\n"
            '        var sections = document.querySelectorAll(".month-calendar");\n'
            "        for (var index = 0; index < sections.length; index++) {\n"
            "          var section = sections[index];\n"
            "          if (section.id === selected_id) {\n"
            '            section.classList.add("is-active");\n'
            "          } else {\n"
            '            section.classList.remove("is-active");\n'
            "          }\n"
            "        }\n"
            "      }\n"
            "\n"
            "      function sync_month_select_to_calendar() {\n"
            "        if (!month_select) {\n"
            "          return;\n"
            "        }\n"
            "        show_month_section(month_select.value);\n"
            "      }\n"
            "\n"
            "      if (month_select) {\n"
            '        month_select.addEventListener("change", sync_month_select_to_calendar);\n'
            "        sync_month_select_to_calendar();\n"
            '        window.addEventListener("pageshow", sync_month_select_to_calendar);\n'
            "      }\n"
            "\n"
        )

    event_modal_block = (
        '      var copy_toast = document.getElementById("copy-toast");\n'
        "      var copy_toast_hide_timeout = null;\n"
        "\n"
        "      function show_copied_toast() {\n"
        "        if (!copy_toast) {\n"
        "          return;\n"
        "        }\n"
        "        if (copy_toast_hide_timeout !== null) {\n"
        "          clearTimeout(copy_toast_hide_timeout);\n"
        "        }\n"
        "        copy_toast.hidden = false;\n"
        "        copy_toast_hide_timeout = setTimeout(function () {\n"
        "          copy_toast.hidden = true;\n"
        "          copy_toast_hide_timeout = null;\n"
        "        }, 2000);\n"
        "      }\n"
        "\n"
        "      function copy_description_using_fallback(description_text) {\n"
        "        var textarea = document.createElement(\"textarea\");\n"
        "        textarea.value = description_text;\n"
        '        textarea.setAttribute("readonly", "");\n'
        '        textarea.style.position = "fixed";\n'
        '        textarea.style.left = "-9999px";\n'
        "        document.body.appendChild(textarea);\n"
        "        textarea.select();\n"
        "        document.execCommand(\"copy\");\n"
        "        document.body.removeChild(textarea);\n"
        "      }\n"
        "\n"
        '      var modal = document.getElementById("event-modal");\n'
        "      if (!modal) {\n"
        "        return;\n"
        "      }\n"
        '      var modal_title = modal.querySelector(".event-modal-title");\n'
        '      var modal_start = modal.querySelector(".event-modal-start");\n'
        '      var modal_stop = modal.querySelector(".event-modal-stop");\n'
        '      var modal_duration = modal.querySelector(".event-modal-duration");\n'
        '      var modal_description = modal.querySelector(".event-modal-description");\n'
        '      var modal_description_block = modal.querySelector(".event-modal-description-block");\n'
        '      var modal_copy_description = modal.querySelector(".event-modal-copy-description");\n'
        '      var modal_close = modal.querySelector(".event-modal-close");\n'
        '      var modal_backdrop = modal.querySelector(".event-modal-backdrop");\n'
        "\n"
        "      function copy_description_to_clipboard() {\n"
        "        var description_text = modal_description.textContent;\n"
        "        if (!description_text) {\n"
        "          return;\n"
        "        }\n"
        "        function finish_copy() {\n"
        "          show_copied_toast();\n"
        "        }\n"
        "        if (navigator.clipboard && navigator.clipboard.writeText) {\n"
        "          navigator.clipboard.writeText(description_text).then(function () {\n"
        "            finish_copy();\n"
        "          }).catch(function () {\n"
        "            copy_description_using_fallback(description_text);\n"
        "            finish_copy();\n"
        "          });\n"
        "          return;\n"
        "        }\n"
        "        copy_description_using_fallback(description_text);\n"
        "        finish_copy();\n"
        "      }\n"
        "\n"
        "      function open_event_modal(calendar_event) {\n"
        '        modal_title.textContent = calendar_event.getAttribute("data-event-name") || "";\n'
        '        modal_start.textContent = calendar_event.getAttribute("data-event-start") || "";\n'
        '        modal_stop.textContent = calendar_event.getAttribute("data-event-stop") || "";\n'
        '        modal_duration.textContent = calendar_event.getAttribute("data-event-duration") || "";\n'
        "        var description_text = calendar_event.getAttribute("
        '"data-event-description") || "";\n'
        "        modal_description.textContent = description_text;\n"
        "        if (description_text) {\n"
        '          modal_description_block.style.display = "block";\n'
        "        } else {\n"
        '          modal_description_block.style.display = "none";\n'
        "        }\n"
        '        modal.classList.add("is-open");\n'
        "      }\n"
        "\n"
        "      function close_event_modal() {\n"
        '        modal.classList.remove("is-open");\n'
        "      }\n"
        "\n"
        '      document.addEventListener("click", function (click_event) {\n'
        "        var click_target = click_event.target;\n"
        "        if (!click_target.closest) {\n"
        "          return;\n"
        "        }\n"
        '        var calendar_event = click_target.closest(".calendar-event");\n'
        "        if (calendar_event) {\n"
        "          open_event_modal(calendar_event);\n"
        "          return;\n"
        "        }\n"
        "        if (click_target.closest(\".event-modal-copy-description\")) {\n"
        "          copy_description_to_clipboard();\n"
        "          return;\n"
        "        }\n"
        "        if (\n"
        "          click_target === modal_backdrop\n"
        "          || click_target === modal_close\n"
        "        ) {\n"
        "          close_event_modal();\n"
        "        }\n"
        "      });\n"
        "\n"
        '      document.addEventListener("keydown", function (keydown_event) {\n'
        '        if (keydown_event.key === "Escape") {\n'
        "          close_event_modal();\n"
        "        }\n"
        '        if (keydown_event.key === "Enter" || keydown_event.key === " ") {\n'
        '          var focused = document.activeElement;\n'
        '          if (focused && focused.classList.contains("calendar-event")) {\n'
        "            keydown_event.preventDefault();\n"
        "            open_event_modal(focused);\n"
        "          }\n"
        "        }\n"
        "      });\n"
    )

    return (
        "  <script>\n"
        "    (function () {\n"
        + month_select_block
        + event_modal_block
        + "    })();\n"
        "  </script>"
    )


def build_static_calendar_html_grid_page(events):
    """Return a complete HTML document with a traditional month grid calendar."""

    month_sections = []
    grouped_months = _group_events_by_year_and_month(events)
    has_multiple_months = len(grouped_months) > 1

    # Render one month grid per year/month that contains events.
    for index, month_group in enumerate(grouped_months):
        year_and_month, month_events = month_group
        year, month = year_and_month
        is_active = False
        if has_multiple_months and index == 0:
            is_active = True
        include_heading = not has_multiple_months
        month_sections.append(
            _build_calendar_month_section_html(
                year,
                month,
                month_events,
                is_active=is_active,
                include_heading=include_heading,
            )
        )

    if month_sections:
        body_parts = []
        if has_multiple_months:
            month_keys = [month_group[0] for month_group in grouped_months]
            body_parts.append(_build_month_selector_html(month_keys))
        body_parts.extend(month_sections)
        calendar_body_html = "\n".join(body_parts)
        months_container_class = "calendar-months"
        if has_multiple_months:
            months_container_class = "calendar-months has-month-select"
    else:
        calendar_body_html = '  <p class="no-events">No events</p>'
        months_container_class = "calendar-months"

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
        "    .month-select-row {\n"
        "      margin-bottom: 1rem;\n"
        "    }\n"
        "    .month-select-row label {\n"
        "      margin-right: 0.5rem;\n"
        "      font-weight: 600;\n"
        "    }\n"
        "    .month-select {\n"
        "      font-family: inherit;\n"
        "      font-size: 1rem;\n"
        "      padding: 0.35rem 0.5rem;\n"
        "    }\n"
        "    .has-month-select .month-calendar {\n"
        "      display: none;\n"
        "      margin-bottom: 0;\n"
        "    }\n"
        "    .has-month-select .month-calendar.is-active {\n"
        "      display: block;\n"
        "    }\n"
        "    .month-calendar {\n"
        "      margin-bottom: 2.5rem;\n"
        "    }\n"
        "    .month-calendar:last-child {\n"
        "      margin-bottom: 0;\n"
        "    }\n"
        "    .month-heading {\n"
        "      font-size: 1.25rem;\n"
        "      margin: 0 0 0.75rem;\n"
        "    }\n"
        "    .calendar-grid {\n"
        "      width: 100%;\n"
        "      border-collapse: collapse;\n"
        "      table-layout: fixed;\n"
        "      background: #fff;\n"
        "      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);\n"
        "    }\n"
        "    .calendar-grid th,\n"
        "    .calendar-grid td {\n"
        "      border: 1px solid #ddd;\n"
        "      vertical-align: top;\n"
        "      width: 14.28%;\n"
        "    }\n"
        "    .calendar-grid th {\n"
        "      background: #f0f0f0;\n"
        "      padding: 0.5rem;\n"
        "      text-align: center;\n"
        "      font-size: 0.85rem;\n"
        "    }\n"
        "    .calendar-grid tbody td.day-cell,\n"
        "    .calendar-grid tbody td.padding-day {\n"
        "      padding: 0;\n"
        "      vertical-align: top;\n"
        "    }\n"
        "    .day-cell-frame {\n"
        "      position: relative;\n"
        "      width: 100%;\n"
        "    }\n"
        "    .day-cell-frame::before {\n"
        "      content: \"\";\n"
        "      display: block;\n"
        "      padding-top: 100%;\n"
        "    }\n"
        "    .day-cell-content {\n"
        "      position: absolute;\n"
        "      top: 0;\n"
        "      right: 0;\n"
        "      bottom: 0;\n"
        "      left: 0;\n"
        "      padding: 0.35rem;\n"
        "      overflow-x: hidden;\n"
        "      overflow-y: auto;\n"
        "    }\n"
        "    .padding-day {\n"
        "      background: #f5f5f5;\n"
        "    }\n"
        "    .day-number {\n"
        "      display: block;\n"
        "      font-weight: 600;\n"
        "      font-size: 0.85rem;\n"
        "      margin-bottom: 0.25rem;\n"
        "      color: #333;\n"
        "    }\n"
        "    .day-events {\n"
        "      list-style: none;\n"
        "      margin: 0;\n"
        "      padding: 0;\n"
        "    }\n"
        "    .calendar-event {\n"
        "      font-size: 0.75rem;\n"
        "      margin-bottom: 0.2rem;\n"
        "      padding: 0.15rem 0.25rem;\n"
        "      background: #e8f0fe;\n"
        "      border-radius: 2px;\n"
        "      overflow: hidden;\n"
        "      text-overflow: ellipsis;\n"
        "      white-space: nowrap;\n"
        "      cursor: pointer;\n"
        "    }\n"
        "    .event-modal {\n"
        "      display: none;\n"
        "      position: fixed;\n"
        "      inset: 0;\n"
        "      z-index: 1000;\n"
        "      align-items: center;\n"
        "      justify-content: center;\n"
        "    }\n"
        "    .event-modal.is-open {\n"
        "      display: flex;\n"
        "    }\n"
        "    .event-modal-backdrop {\n"
        "      position: absolute;\n"
        "      inset: 0;\n"
        "      background: rgba(0, 0, 0, 0.45);\n"
        "    }\n"
        "    .event-modal-dialog {\n"
        "      position: relative;\n"
        "      overflow: visible;\n"
        "      background: #fff;\n"
        "      max-width: 28rem;\n"
        "      width: calc(100% - 2rem);\n"
        "      padding: 1.25rem 1.5rem;\n"
        "      border-radius: 6px;\n"
        "      box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);\n"
        "    }\n"
        "    .event-modal-close {\n"
        "      position: absolute;\n"
        "      top: 0.5rem;\n"
        "      right: 0.5rem;\n"
        "      border: none;\n"
        "      background: transparent;\n"
        "      font-size: 1.5rem;\n"
        "      line-height: 1;\n"
        "      cursor: pointer;\n"
        "      color: #555;\n"
        "    }\n"
        "    .event-modal-title {\n"
        "      font-size: 1.15rem;\n"
        "      margin: 0 2rem 0.75rem 0;\n"
        "    }\n"
        "    .event-modal-details {\n"
        "      margin: 0 0 0.75rem;\n"
        "    }\n"
        "    .event-modal-details dt {\n"
        "      font-weight: 600;\n"
        "      margin-top: 0.35rem;\n"
        "    }\n"
        "    .event-modal-details dd {\n"
        "      margin: 0.15rem 0 0;\n"
        "    }\n"
        "    .event-modal-description-block {\n"
        "      display: none;\n"
        "    }\n"
        "    .event-modal-description-row {\n"
        "      display: flex;\n"
        "      gap: 0.5rem;\n"
        "      align-items: flex-start;\n"
        "    }\n"
        "    .event-modal-description {\n"
        "      flex: 1;\n"
        "      margin: 0;\n"
        "      color: #444;\n"
        "      white-space: pre-wrap;\n"
        "    }\n"
        "    .event-modal-copy-description {\n"
        "      flex-shrink: 0;\n"
        "      font-family: inherit;\n"
        "      font-size: 0.85rem;\n"
        "      padding: 0.25rem 0.5rem;\n"
        "      border: 1px solid #ccc;\n"
        "      border-radius: 4px;\n"
        "      background: #f5f5f5;\n"
        "      cursor: pointer;\n"
        "    }\n"
        "    .copy-toast {\n"
        "      position: absolute;\n"
        "      bottom: 1rem;\n"
        "      left: 50%;\n"
        "      transform: translateX(-50%);\n"
        "      padding: 0.5rem 1rem;\n"
        "      background: #333;\n"
        "      color: #fff;\n"
        "      border-radius: 4px;\n"
        "      font-size: 0.9rem;\n"
        "      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);\n"
        "      z-index: 2;\n"
        "      pointer-events: none;\n"
        "    }\n"
        "    .copy-toast[hidden] {\n"
        "      display: none;\n"
        "    }\n"
        "    .no-events {\n"
        "      color: #555;\n"
        "    }\n"
        "  </style>\n"
        "</head>\n"
        "<body>\n"
        "  <h1>Calendar</h1>\n"
        '  <div class="'
    )
    document_prefix = document_prefix + months_container_class + '">\n'
    document_suffix = (
        "  </div>\n"
        + _build_event_modal_html()
        + "\n"
        + _build_calendar_grid_script_html(has_multiple_months)
        + "\n"
        "</body>\n"
        "</html>\n"
    )
    document = document_prefix + calendar_body_html + "\n" + document_suffix

    return document


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
