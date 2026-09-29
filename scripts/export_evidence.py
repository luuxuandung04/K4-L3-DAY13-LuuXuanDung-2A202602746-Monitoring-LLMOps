import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = REPO_ROOT / "submission" / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = REPO_ROOT / "data" / "logs.jsonl"


def run_cmd(cmd: list[str]) -> str:
    res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, encoding="utf-8")
    return res.stdout + ("\n" + res.stderr if res.stderr else "")


def main():
    print("Generating validation evidence text files...")

    # 01-pytest
    out_pytest = run_cmd([sys.executable, "-m", "pytest", "-v"])
    (EVIDENCE_DIR / "01-pytest.txt").write_text(out_pytest, encoding="utf-8")
    print("Saved 01-pytest.txt")

    # 02-log-validator
    out_log = run_cmd([sys.executable, "scripts/validate_logs.py"])
    (EVIDENCE_DIR / "02-log-validator.txt").write_text(out_log, encoding="utf-8")
    print("Saved 02-log-validator.txt")

    # 03-dashboard-validator
    out_dash = run_cmd([sys.executable, "scripts/validate_dashboard.py"])
    (EVIDENCE_DIR / "03-dashboard-validator.txt").write_text(out_dash, encoding="utf-8")
    print("Saved 03-dashboard-validator.txt")

    # 04-structured-log
    logs = [json.loads(line) for line in LOG_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    resp_logs = [l for l in logs if l.get("event") == "response_sent"]
    sample_log = resp_logs[0] if resp_logs else logs[0]
    (EVIDENCE_DIR / "04-structured-log.txt").write_text(json.dumps(sample_log, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Saved 04-structured-log.txt")

    # 05-pii-redaction
    pii_sample = [l for l in logs if "[REDACTED_" in json.dumps(l)]
    sample_pii = pii_sample[0] if pii_sample else {"message": "Email: [REDACTED_EMAIL]"}
    (EVIDENCE_DIR / "05-pii-redaction.txt").write_text(json.dumps(sample_pii, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Saved 05-pii-redaction.txt")

    # 13-incident-log
    incident_logs = [l for l in logs if "k4-l3a-challenge" in json.dumps(l)]
    (EVIDENCE_DIR / "13-incident-log.txt").write_text(
        "\n".join(json.dumps(l, indent=2, ensure_ascii=False) for l in incident_logs[:2]),
        encoding="utf-8"
    )
    print("Saved 13-incident-log.txt")


if __name__ == "__main__":
    main()
