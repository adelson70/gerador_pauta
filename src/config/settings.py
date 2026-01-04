from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

PAGE_SIZE = A4
PAGE_WIDTH, PAGE_HEIGHT = A4

NOTE_POSITIONS = {
    "Sol3": -25, "La3": -20, "Si3": -15, "Do4": -10, "Re4": -5,
    "Mi4": 0,   "Fa4": 5,   "Sol4": 10, "La4": 15, "Si4": 20,
    "Do5": 25,  "Re5": 30,  "Mi5": 35, "Fa5": 40,
    "Sol5": 45, "La5": 50,  "Si5": 55
}

DEFAULT_SEQUENCE = [
    "Sol3", "La3", "Si3", "Do4", "Re4",
    "Mi4", "Fa4", "Sol4", "La4",
    "Si4", "Do5", "Re5", "Mi5",
    "Fa5", "Sol5", "La5", "Si5"
]

NOTES_BY_STRING = {
    "SOL": ["Sol3", "La3", "Si3", "Do4", "Re4"],
    "RÉ": ["Mi4", "Fa4", "Sol4", "La4"],
    "LÁ": ["Si4", "Do5", "Re5", "Mi5"],
    "MI": ["Fa5", "Sol5", "La5", "Si5"]
}

X_START = 2 * cm
STAFF_WIDTH = PAGE_WIDTH - 4 * cm
Y_START = PAGE_HEIGHT - 3 * cm
CLEF_WIDTH = 1.2 * cm
BARLINE_X = X_START + STAFF_WIDTH

MAX_STAFFS_PER_PAGE = 6

CLEF_WIDTH_PT = 70
available_width_for_notes = STAFF_WIDTH - CLEF_WIDTH_PT - 0.3 * cm
NOTE_X_SPACING = available_width_for_notes / 17
NOTE_X_OFFSET = CLEF_WIDTH_PT + 0.2 * cm

NOTE_RADIUS = 4
SUPPLEMENTARY_LINE_LENGTH = 16

