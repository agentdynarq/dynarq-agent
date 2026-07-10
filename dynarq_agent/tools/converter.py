"""A unit conversion tool: length units and temperature."""
from ..tool import Tool

_LENGTH = {
    "m": 1.0, "meter": 1.0, "meters": 1.0,
    "km": 1000.0, "cm": 0.01, "mm": 0.001,
    "mi": 1609.344, "mile": 1609.344, "miles": 1609.344,
    "ft": 0.3048, "feet": 0.3048, "foot": 0.3048,
    "in": 0.0254, "inch": 0.0254,
    "yd": 0.9144, "yard": 0.9144,
}
_TEMP = {"c": "c", "celsius": "c", "f": "f", "fahrenheit": "f", "k": "k", "kelvin": "k"}


def _fmt(x: float):
    x = round(x, 4)
    return int(x) if float(x).is_integer() else x


def _convert_temp(value, f, t):
    celsius = value if f == "c" else (value - 32) * 5 / 9 if f == "f" else value - 273.15
    return celsius if t == "c" else celsius * 9 / 5 + 32 if t == "f" else celsius + 273.15


def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    value = float(value)
    f, t = from_unit.lower(), to_unit.lower()
    if f in _LENGTH and t in _LENGTH:
        out = value * _LENGTH[f] / _LENGTH[t]
        return f"{_fmt(value)} {from_unit} = {_fmt(out)} {to_unit}"
    if f in _TEMP and t in _TEMP:
        out = _convert_temp(value, _TEMP[f], _TEMP[t])
        return f"{_fmt(value)} {from_unit} = {_fmt(out)} {to_unit}"
    return f"Error: cannot convert '{from_unit}' to '{to_unit}'"


CONVERTER = Tool(
    name="converter",
    description="Convert length (m, km, cm, mi, ft, in, yd) or temperature (c, f, k).",
    parameters={
        "type": "object",
        "properties": {
            "value": {"type": "number"},
            "from_unit": {"type": "string"},
            "to_unit": {"type": "string"},
        },
        "required": ["value", "from_unit", "to_unit"],
    },
    func=convert_units,
)
