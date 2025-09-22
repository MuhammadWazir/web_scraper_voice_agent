import time
from typing import Dict

CAMPAIGN_NAME = "web chat"
USAGE_SECONDS_BY_SESSION: Dict[str, int] = {}
TOTAL_CAMPAIGN_SECONDS: int = 0


def mark_session_start(session_id: str) -> float:
	USAGE_SECONDS_BY_SESSION[session_id] = 0
	return time.monotonic()


def mark_session_end(session_id: str, started_at: float) -> int:
	elapsed = int(max(0, time.monotonic() - started_at))
	USAGE_SECONDS_BY_SESSION[session_id] = elapsed
	global TOTAL_CAMPAIGN_SECONDS
	TOTAL_CAMPAIGN_SECONDS += elapsed
	return elapsed 