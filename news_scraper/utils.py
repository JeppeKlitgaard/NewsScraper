"""
Contains utility functions.
"""

def normalise_space(s):
    return " ".join(s.split())


def filter_empty(lst):
    return [x.strip() for x in lst if x.strip()]
