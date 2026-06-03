"""Command-line entry point: format ICS events as a sorted table."""

import argparse
import sys

import tabulate

import ics_render.events


def main(argv=None):
    """Parse arguments, load ICS files, and print a sorted event table."""

    argument_list = sys.argv[1:]
    if argv is not None:
        argument_list = argv

    parser = argparse.ArgumentParser(
        description="Parse ICS calendar files and print events sorted by time."
    )
    parser.add_argument(
        "--filepath",
        action="append",
        required=True,
        metavar="PATH",
        help="Path to an ICS file (repeat for multiple files)",
    )
    arguments = parser.parse_args(argument_list)

    # Combine events from every input file and render as a table.
    combined_events = ics_render.events.combine_events_gen(arguments.filepath)
    table_rows = ics_render.events.get_events_as_table_rows_gen(combined_events)
    table_text = tabulate.tabulate(
        table_rows,
        headers=["Timestamp", "Duration", "Name"],
    )
    print(table_text)


if __name__ == "__main__":
    main()
