import json
import datetime
import os

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs", "security_events.jsonl")

def log_security_event(event_type: str, details: dict):
    """보안 이벤트를 JSON Lines 형식으로 기록합니다."""
    event = {
        "timestamp": datetime.datetime.now().isoformat(),
        "event_type": event_type,
        "details": details
    }
    
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Failed to write log: {e}")
