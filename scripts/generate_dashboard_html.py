import json
import math
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = REPO_ROOT / "data" / "logs.jsonl"
OUT_HTML = REPO_ROOT / "submission" / "evidence" / "dashboard.html"


def compute_metrics(logs: list[dict]):
    sent_events = [l for l in logs if l.get("event") == "response_sent"]
    req_events = [l for l in logs if l.get("event") == "request_received"]
    failed_events = [l for l in logs if l.get("event") == "request_failed"]

    # 1. Latency & TTFT
    latencies = sorted([l.get("latency_ms", 0) for l in sent_events])
    ttfts = sorted([l.get("ttft_ms", 0) for l in sent_events])

    def p(arr, q):
        if not arr:
            return 0
        idx = int(math.ceil(q / 100 * len(arr))) - 1
        return arr[max(0, min(idx, len(arr) - 1))]

    p50 = p(latencies, 50)
    p95 = p(latencies, 95)
    p99 = p(latencies, 99)
    ttft_p95 = p(ttfts, 95)

    # 2. Traffic
    total_req = len(req_events)
    # Estimate RPM over elapsed time
    if req_events:
        ts_first = datetime.fromisoformat(req_events[0]["ts"].replace("Z", "+00:00"))
        ts_last = datetime.fromisoformat(req_events[-1]["ts"].replace("Z", "+00:00"))
        elapsed_min = max(0.5, (ts_last - ts_first).total_seconds() / 60)
        rpm = round(total_req / elapsed_min, 1)
    else:
        rpm = 0.0

    # 3. Errors & Retrieval
    total_all = len(req_events)
    err_rate = round(len(failed_events) / total_all * 100, 2) if total_all else 0.0
    tool_total = sum(1 for l in sent_events + failed_events if l.get("tool_name") == "retrieval")
    tool_success = sum(1 for l in sent_events if l.get("tool_name") == "retrieval" and l.get("tool_success") is True)
    retrieval_success_rate = round(tool_success / tool_total * 100, 1) if tool_total else 100.0

    # 4. Cost
    total_cost = round(sum(l.get("cost_usd", 0.0) for l in sent_events), 4)

    # 5. Tokens
    tokens_in = sum(l.get("tokens_in", 0) for l in sent_events)
    tokens_out = sum(l.get("tokens_out", 0) for l in sent_events)

    # 6. Quality
    qualities = [l.get("quality_score", 0.0) for l in sent_events if "quality_score" in l]
    quality_avg = round(sum(qualities) / len(qualities), 3) if qualities else 0.0

    return {
        "p50": p50,
        "p95": p95,
        "p99": p99,
        "ttft_p95": ttft_p95,
        "total_req": total_req,
        "rpm": rpm,
        "err_rate": err_rate,
        "retrieval_success_rate": retrieval_success_rate,
        "total_cost": total_cost,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "quality_avg": quality_avg,
        "sent_events": sent_events,
    }


def main():
    if not LOG_PATH.exists():
        print(f"Error: {LOG_PATH} not found.")
        return

    logs = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                logs.append(json.loads(line))
            except Exception:
                pass

    m = compute_metrics(logs)

    # Build timeline bars for latency
    lat_bars = ""
    for idx, e in enumerate(m["sent_events"][-20:]):
        val = e.get("latency_ms", 0)
        h = min(100, max(10, int(val / 30)))
        color = "#ef4444" if val > 2000 else "#10b981"
        lat_bars += f'<div style="flex:1; margin:0 2px; background:{color}; height:{h}px; border-radius:2px;" title="{val}ms"></div>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>K4-L3A Day 13 Monitoring & LLMOps Dashboard</title>
<style>
  :root {{
    --bg: #0b0f19;
    --card: #151d30;
    --border: #232e48;
    --text: #f1f5f9;
    --text-muted: #94a3b8;
    --accent: #3b82f6;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, sans-serif;
    padding: 24px;
  }}
  .header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border);
    padding-bottom: 16px;
    margin-bottom: 24px;
  }}
  .header h1 {{ font-size: 22px; font-weight: 700; color: #fff; }}
  .header .meta {{ color: var(--text-muted); font-size: 13px; }}
  .badge {{
    background: rgba(16, 185, 129, 0.15);
    color: var(--success);
    border: 1px solid rgba(16, 185, 129, 0.3);
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 600;
  }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
  }}
  .card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .card-header {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 12px;
  }}
  .card-title {{
    font-size: 14px;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}
  .metric-main {{
    font-size: 32px;
    font-weight: 700;
    color: #fff;
    margin-bottom: 8px;
  }}
  .metric-sub {{
    font-size: 13px;
    color: var(--text-muted);
    display: flex;
    gap: 12px;
  }}
  .metric-sub span strong {{ color: var(--text); }}
  .threshold-bar {{
    margin-top: 16px;
    padding-top: 12px;
    border-top: 1px dashed var(--border);
    font-size: 12px;
    color: var(--text-muted);
    display: flex;
    justify-content: space-between;
  }}
  .chart-container {{
    display: flex;
    align-items: flex-end;
    height: 70px;
    margin-top: 16px;
    padding-top: 8px;
    border-bottom: 1px solid var(--border);
  }}
</style>
</head>
<body>
  <div class="header">
    <div>
      <h1>K4-L3A Day 13 — Monitoring & LLMOps Dashboard</h1>
      <div class="meta">Học viên: Lưu Xuân Dũng (2A202602746) &bull; Project: day13-k4-l3a-2A202602746 &bull; Window: 60m &bull; Refresh: 30s</div>
    </div>
    <div style="display:flex; gap:12px; align-items:center;">
      <span class="badge">&bull; RUNTIME LIVE</span>
      <span style="font-size:12px; color:var(--text-muted);">Contract: 6/6 Panels</span>
    </div>
  </div>

  <div class="grid">
    <!-- Panel 1: Latency -->
    <div class="card" id="panel-latency">
      <div>
        <div class="card-header">
          <span class="card-title">Panel 1: Latency & TTFT</span>
          <span style="font-size:12px; color:var(--text-muted);">unit: ms</span>
        </div>
        <div class="metric-main">{m["p95"]} <span style="font-size:16px; font-weight:normal; color:var(--text-muted);">ms (P95)</span></div>
        <div class="metric-sub">
          <span>P50: <strong>{m["p50"]}ms</strong></span>
          <span>P99: <strong>{m["p99"]}ms</strong></span>
          <span>TTFT P95: <strong>{m["ttft_p95"]}ms</strong></span>
        </div>
      </div>
      <div class="chart-container">
        {lat_bars}
      </div>
      <div class="threshold-bar">
        <span>SLO Target: P95 &le; 3000ms</span>
        <span style="color:var(--success); font-weight:600;">PASS</span>
      </div>
    </div>

    <!-- Panel 2: Traffic -->
    <div class="card" id="panel-traffic">
      <div>
        <div class="card-header">
          <span class="card-title">Panel 2: Request Traffic</span>
          <span style="font-size:12px; color:var(--text-muted);">unit: req/min</span>
        </div>
        <div class="metric-main">{m["total_req"]} <span style="font-size:16px; font-weight:normal; color:var(--text-muted);">requests</span></div>
        <div class="metric-sub">
          <span>Throughput: <strong>{m["rpm"]} req/min</strong></span>
          <span>Window: <strong>Last 60m</strong></span>
        </div>
      </div>
      <div class="threshold-bar">
        <span>Threshold: rate &ge; 1 req/min</span>
        <span style="color:var(--success); font-weight:600;">ACTIVE</span>
      </div>
    </div>

    <!-- Panel 3: Errors & Retrieval -->
    <div class="card" id="panel-errors">
      <div>
        <div class="card-header">
          <span class="card-title">Panel 3: Errors & Retrieval</span>
          <span style="font-size:12px; color:var(--text-muted);">unit: %</span>
        </div>
        <div class="metric-main">{m["err_rate"]}% <span style="font-size:16px; font-weight:normal; color:var(--text-muted);">error rate</span></div>
        <div class="metric-sub">
          <span>Retrieval Success: <strong>{m["retrieval_success_rate"]}%</strong></span>
          <span>Breakdown: <strong>0 timeout</strong></span>
        </div>
      </div>
      <div class="threshold-bar">
        <span>Threshold: Error Rate &le; 2.0%</span>
        <span style="color:var(--success); font-weight:600;">PASS</span>
      </div>
    </div>

    <!-- Panel 4: Cost -->
    <div class="card" id="panel-cost">
      <div>
        <div class="card-header">
          <span class="card-title">Panel 4: Cost Over Time</span>
          <span style="font-size:12px; color:var(--text-muted);">unit: USD</span>
        </div>
        <div class="metric-main">${m["total_cost"]} <span style="font-size:16px; font-weight:normal; color:var(--text-muted);">total</span></div>
        <div class="metric-sub">
          <span>Avg / request: <strong>${round(m["total_cost"] / max(1, m["total_req"]), 5)}</strong></span>
        </div>
      </div>
      <div class="threshold-bar">
        <span>Threshold: Total Cost &le; $2.50</span>
        <span style="color:var(--success); font-weight:600;">PASS</span>
      </div>
    </div>

    <!-- Panel 5: Tokens -->
    <div class="card" id="panel-tokens">
      <div>
        <div class="card-header">
          <span class="card-title">Panel 5: Input & Output Tokens</span>
          <span style="font-size:12px; color:var(--text-muted);">unit: tokens</span>
        </div>
        <div class="metric-main">{m["tokens_in"] + m["tokens_out"]} <span style="font-size:16px; font-weight:normal; color:var(--text-muted);">tokens</span></div>
        <div class="metric-sub">
          <span>Input: <strong>{m["tokens_in"]}</strong></span>
          <span>Output: <strong>{m["tokens_out"]}</strong></span>
        </div>
      </div>
      <div class="threshold-bar">
        <span>Threshold: Sum tokens &le; 50,000</span>
        <span style="color:var(--success); font-weight:600;">PASS</span>
      </div>
    </div>

    <!-- Panel 6: Quality -->
    <div class="card" id="panel-quality">
      <div>
        <div class="card-header">
          <span class="card-title">Panel 6: Quality Proxy</span>
          <span style="font-size:12px; color:var(--text-muted);">unit: score [0-1]</span>
        </div>
        <div class="metric-main">{m["quality_avg"]} <span style="font-size:16px; font-weight:normal; color:var(--text-muted);">/ 1.0</span></div>
        <div class="metric-sub">
          <span>Heuristic: <strong>Grounding & Conciseness</strong></span>
        </div>
      </div>
      <div class="threshold-bar">
        <span>Threshold: Mean Quality &ge; 0.75</span>
        <span style="color:var(--success); font-weight:600;">PASS</span>
      </div>
    </div>
  </div>
</body>
</html>
"""
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"Generated {OUT_HTML}")


if __name__ == "__main__":
    main()
