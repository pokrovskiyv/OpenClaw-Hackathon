"""
Configuration for the eval loop system.
Supports Anthropic Claude API. Set your API key as environment variable.
"""
import os

# --- LLM Configuration ---
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Model for running agents (the "workers")
AGENT_MODEL = "claude-haiku-4-5-20251001"  # Fast + cost-efficient for structured output

# Model for evaluation (the "judge") — use a stronger model
EVAL_MODEL = "claude-sonnet-4-6"

# Model for improvement (the "coach") — strongest available
IMPROVER_MODEL = "claude-sonnet-4-6"

# Model for Claims Manager evaluation (peer-chain final reviewer)
MANAGER_MODEL = "claude-sonnet-4-6"

# --- Pipeline Configuration ---
AGENT_ORDER = [
    "front_desk",
    "claims_officer",
    "assessor",
    "fraud_analyst",
    "senior_reviewer",
    "finance",
]

# --- Eval Configuration ---
MAX_ITERATIONS = 10
PASSING_SCORE = 85  # Score threshold to stop improving

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTS_DIR = os.path.join(BASE_DIR, "agents")
TEST_CASES_DIR = os.path.join(BASE_DIR, "test_cases")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
DATA_DIR = os.path.join(BASE_DIR, "data", "policies")
CLAIMS_DIR = os.path.join(BASE_DIR, "claims")
