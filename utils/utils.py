# utils.py
import math


def safe_float(value):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    try:
        f = float(value)
        return f if math.isfinite(f) else None
    except Exception:
        return None

def safe_int(value):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    try:
        return int(value)
    except Exception:
        return None
