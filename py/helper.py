"""A set of helper functions."""
import fileinput
import re
from datetime import date


def update_ref_access(reference):
    """Update reference access date."""
    today = date.today().strftime('%B %d, %Y')
    reference_sub = re.escape(reference) + ' \((.*)\)'
    reference_new = reference + ' (Retrieved on {})'.format(today)
    print(reference_new)
    with fileinput.FileInput('README.md', inplace=True, backup='.bak') as file:
        for line in file:
            print(
                re.sub(
                    reference_sub,
                    reference_new,
                    line
                ), end=''
            )
