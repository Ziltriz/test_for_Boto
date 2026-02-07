import logging


def safe_float(v):
    if v is None or v == "" or v == "null":
        return None
    try:
        return float(v)
    except (ValueError, TypeError, OverflowError):
        logging.warning(f"Invalid numeric value for float field: {v}")
        return None