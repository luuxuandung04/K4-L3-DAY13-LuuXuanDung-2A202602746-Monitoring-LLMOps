from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import httpx
from langfuse import get_client

client = get_client()
BASE_URL = "http://127.0.0.1:8000"


def send_chat(msg: str, user_id: str = "student-01", feature: str = "qa") -> dict:
    resp = httpx.post(
        f"{BASE_URL}/chat",
        json={
            "user_id": user_id,
            "session_id": "prompt-lifecycle-session",
            "feature": feature,
            "message": msg,
        },
        timeout=30.0,
    )
    return resp.json()


def main():
    print("=== Step 1: Ensure Prompt v1 (baseline) and v2 (candidate) ===")
    p1 = client.get_prompt("day13-chat", version=1)
    p2 = client.get_prompt("day13-chat", version=2)
    print(f"Prompt v1 labels: {p1.labels}")
    print(f"Prompt v2 labels: {p2.labels}")

    print("\n=== Step 2: Testing with Prompt v1 (label: baseline/production) ===")
    res1 = send_chat("Explain how metrics and logs correlate in observability.")
    print(f"Request 1 -> correlation_id: {res1['correlation_id']}")

    print("\n=== Step 3: Promote v2 to production ===")
    client.update_prompt(name="day13-chat", version=2, new_labels=["candidate", "production"])
    time.sleep(2)
    p2_updated = client.get_prompt("day13-chat", version=2)
    print(f"Updated Prompt v2 labels: {p2_updated.labels}")

    print("\n=== Step 4: Request with promoted v2 production ===")
    res2 = send_chat("Explain how metrics and logs correlate in observability.")
    print(f"Request 2 (promoted v2) -> correlation_id: {res2['correlation_id']}")

    print("\n=== Step 5: Rollback production to v1 ===")
    client.update_prompt(name="day13-chat", version=1, new_labels=["baseline", "production"])
    client.update_prompt(name="day13-chat", version=2, new_labels=["candidate"])
    time.sleep(2)
    p1_rolled_back = client.get_prompt("day13-chat", version=1)
    p2_rolled_back = client.get_prompt("day13-chat", version=2)
    print(f"After Rollback -> v1 labels: {p1_rolled_back.labels}, v2 labels: {p2_rolled_back.labels}")

    print("\n=== Step 6: Request after rollback (back to v1) ===")
    res3 = send_chat("Explain how metrics and logs correlate in observability.")
    print(f"Request 3 (rolled back v1) -> correlation_id: {res3['correlation_id']}")

    print("\nPrompt lifecycle test completed successfully!")


if __name__ == "__main__":
    main()
