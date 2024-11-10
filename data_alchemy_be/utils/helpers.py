import pandas as pd


def convert_to_integer(val):
    if not val or pd.isna(val):
        return ''
    # Remove commas from numbers (e.g., "1,000" -> "1000")
    cleaned_val = str(val).replace(',', '').strip()
    return str(int(float(cleaned_val)))


def convert_to_float(val):
    if not val or pd.isna(val):
        return ''
    cleaned_val = str(val).replace(',', '').strip()
    return str(float(cleaned_val))


def convert_to_datetime(val):
    if not val or pd.isna(val):
        return ''
    return str(pd.to_datetime(val))


def convert_to_boolean(val):
    if not val or pd.isna(val):
        return ''
    val_lower = str(val).lower().strip()
    if val_lower in {'true', 'yes', '1', 't', 'y', 'on'}:
        return 'true'
    elif val_lower in {'false', 'no', '0', 'f', 'n', 'off'}:
        return 'false'
    return ''


def convert_to_category(val):
    if not val or pd.isna(val):
        return ''
    return str(val).strip()