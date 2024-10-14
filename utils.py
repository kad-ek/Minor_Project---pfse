import csv
from dataclasses import dataclass
from math import pi


def str_to_int(s: str) -> int|str:
    """
    Returns an integer. Converts 's' into an integer if possible. If not possible, keeps the string as it is.
    """
    try:
        s = int(s)
    except ValueError:
        s = s
    return s



def str_to_float(s: str) -> float|str:
    """
    Returns an float. Converts 's' into an float if possible. If not possible, keeps the string as it is.
    """
    try:
        s = float(s)
    except ValueError:
        s = s
    return s



def read_csv_file(filename: str) -> str:
    """
    Returns data contained in the file, 'filename' as a list of lists.
    It is assumed that the data in the file is "csv-ish", meaning with 
    comma-separated values.
    """
    acc = []
    with open(filename, 'r') as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            acc.append(line)
    return acc



