"""All settings in one place. Change things here, not scattered through the code."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent      # the project folder

# Load ANTHROPIC_API_KEY from THIS project's .env file, if python-dotenv is installed.
# (A bare load_dotenv() would search parent folders and could pick up some other
# project's key without you noticing.)
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

# ---- Folders --------------------------------------------------------------
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"                         # the big 311 CSV (not in git)
MESSAGES_DIR = DATA_DIR / "messages"               # resident messages for training/testing
CITY_INFO_DIR = DATA_DIR / "city_info"             # knowledge base articles
MODELS_DIR = ROOT / "models"                       # trained classifier is saved here
LOG_DIR = ROOT / "logs"                            # audit logs
OUTBOX_DIR = ROOT / "outbox"                       # "submitted" requests (demo only)
REPORTS_DIR = ROOT / "eval" / "reports"

# ---- The 311 open data file -----------------------------------------------
DATA_YEAR = 2025
DATA_URL = (
    "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/"
    "2e54bc0e-4399-4076-b717-351df5918ae7/resource/"
    "f3db05ab-2588-4159-89f7-56c74d1d8201/download/sr2025.zip"
)
DATA_FILE = RAW_DIR / f"SR{DATA_YEAR}.csv"

# ---- The request types this agent handles ----------------------------------
# These are exact "Service Request Type" names from the City's data.
# Anything that doesn't fit one of these gets escalated to a human.
REQUEST_TYPES = [
    "Road Pothole / Road Damage",
    "Res / Garbage / Not Picked Up",
    "Res / Organic Green Bin / Not Picked Up",
    "Residential Bin Lid Damaged",
    "Pick up Dead Wildlife",
    "Injured - Wildlife",
    "General Pruning",
    "Tree Emergency Clean-Up",
    "Sidewalk Snow Clearing Required",
    "Sewer Service Line-Blocked",
    "Traffic Signal Repair",
    "Amplified Sound or Instrument Sound",
    "Construction Noise",
    "Clean up Illegal Dumping on City Road Allowance",
    "Property Standards and Maintenance Violations",
]

# ---- Models ----------------------------------------------------------------
AGENT_MODEL = "claude-opus-5-5"
# Models compared in the evaluation (classification only).
# Prices are USD per 1 million tokens: (input, output).
MODEL_PRICES = {
    "claude-opus-5-5": (4.00, 20.00),
    "claude-haiku-5-5": (0.10, 0.50),
}
EVAL_MODELS = ["claude-opus-5-5", "claude-haiku-5-5"]

# ---- Guardrails ------------------------------------------------------------
# If the classifier's best guess is below this, the agent must ask a
# clarifying question instead of assuming a request type.
# Picked from the threshold table in the eval report: at 0.3 the agent asks
# about 1 in 4 times. (Caveat: chosen on the test set; see governance/model_card.md.)
CONFIDENCE_THRESHOLD = 0.3
# Safety stop: the agent may call at most this many tools per user message.
MAX_TOOL_STEPS = 8


def has_api_key():
    return bool(os.getenv("ANTHROPIC_API_KEY"))
