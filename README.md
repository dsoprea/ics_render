# ics-render

Parse one or more ICS calendar files, merge their events, sort by start time, and print the result in several formats.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Basic usage

`--filepath` is required and may be repeated. Paths are read in order; events from every file are combined and sorted by start time.

```bash
ir_format --filepath calendar-a.ics --filepath calendar-b.ics
```

Without an output flag, `ir_format` prints a text table to stdout.

## Output modes

Output format flags are mutually exclusive. Pick one per run.

### Default text table

Sorted columns: **Start**, **Duration**, **Name**.

```bash
ir_format --filepath tests/fixtures/early.ics --filepath tests/fixtures/late.ics
```

![Default text table output](asset/screenshots/default-table.png)

### JSON Lines (`--jsonl`)

Each event is one JSON object on its own line. Keys are lower-case, underscore-separated names taken from the original VEVENT properties (`summary`, `start`, `end`, and so on). Timestamp values use ISO 8601.

```bash
ir_format --jsonl --filepath tests/fixtures/early.ics --filepath tests/fixtures/late.ics
```

![JSONL output](asset/screenshots/jsonl.png)

Redirect to a file:

```bash
ir_format --jsonl --filepath calendar.ics > events.jsonl
```

### HTML month grid (`--html`)

A self-contained HTML page with a traditional calendar layout: weeks as rows, days as columns (Sunday first), events listed inside each day cell. Timed events show `HH:MM` before the name.

When events span more than one month, a **Month** drop-down at the top switches between month grids. The visible grid stays in sync with the selection after refresh.

Click an event to open a detail modal (start, stop, duration, description). Use **Copy** beside the description to copy it to the clipboard; a **Copied** toast confirms success.

```bash
ir_format --html --filepath tests/fixtures/early.ics --filepath tests/fixtures/late.ics > calendar.html
```

![HTML month grid](asset/screenshots/html-grid.png)

![HTML month grid with event modal](asset/screenshots/html-grid-modal.png)

Open in a browser:

```bash
xdg-open calendar.html
```

### HTML table (`--html-table`)

A self-contained HTML page: one table row per event with **Start**, **Stop**, **Duration**, and **Name**. Hover the name to see the description as a tooltip.

```bash
ir_format --html-table --filepath tests/fixtures/early.ics --filepath tests/fixtures/late.ics > calendar-table.html
```

![HTML table output](asset/screenshots/html-table.png)

### HTML list (`--html-list`)

A self-contained HTML page: each event is a spaced block with name, start, stop, duration, and the full description at the bottom (newlines rendered as line breaks).

```bash
ir_format --html-list --filepath tests/fixtures/early.ics --filepath tests/fixtures/late.ics > calendar-list.html
```

![HTML list output](asset/screenshots/html-list.png)

## Tests

```bash
python -m pytest -q
```

## Regenerating README screenshots

Screenshots under `asset/screenshots/` are produced from the test fixtures using Brave in headless mode:

```bash
./make_screenshots
```

Requires `brave` (or adjust the browser command in the script). Intermediate `.html` files in `asset/screenshots/` are updated at the same time.
