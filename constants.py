from pathlib import Path

BASE_DIR = Path(__file__).parent
SUMMARY_CSV = BASE_DIR / "qld_summary_long.csv"
DETAIL_CSV = BASE_DIR / "qld_detail.csv"
STYLES_CSS = BASE_DIR / "styles.css"

PAGE_TITLE = "QLD Crime Intelligence Dashboard"
PAGE_ICON = "🚨"
MAX_YEAR = 2025

INDIGO_SCALE = [
    [0.0, "#ccfbf1"],
    [0.25, "#5eead4"],
    [0.5, "#14b8a6"],
    [0.75, "#0f766e"],
    [1.0, "#134e4a"],
]

OFFENCE_COLOURS = {
    "Offences Against the Person": "#f87171",
    "Offences Against Property": "#fb923c",
    "Drug Offences": "#facc15",
    "Traffic and Related Offences": "#4ade80",
    "Breach Domestic Violence Protection Order": "#f472b6",
    "Good Order Offences": "#60a5fa",
    "Miscellaneous Offences": "#a78bfa",
    "Other Offences": "#94a3b8",
}

GENERIC_OFFENCE_GROUPS = ["Other Offences", "Miscellaneous Offences"]

DETAIL_OFFENCE_ORDER = [
    "Assault",
    "Grievous Assault",
    "Serious Assault",
    "Sexual Offences",
    "Robbery",
    "Armed Robbery",
    "Unlawful Entry",
    "Other Property Damage",
    "Fraud",
    "Breach Domestic Violence Protection Order",
    "Drink Driving",
]
