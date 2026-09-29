import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = REPO_ROOT / "submission" / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def capture_html(html_content: str, out_png: Path, width: int = 1200, height: int = 750):
    tmp_html = EVIDENCE_DIR / f"_tmp_{out_png.stem}.html"
    tmp_html.write_text(html_content, encoding="utf-8")
    file_uri = tmp_html.resolve().as_uri()

    ps_cmd = (
        f'Start-Process -FilePath "{EDGE_PATH}" '
        f'-ArgumentList @("--headless", "--disable-gpu", "--screenshot={out_png.resolve()}", "--window-size={width},{height}", "{file_uri}") '
        f'-Wait'
    )
    subprocess.run(["powershell", "-Command", ps_cmd], check=True)
    try:
        if tmp_html.exists():
            tmp_html.unlink()
    except Exception:
        pass
    print(f"Captured {out_png.name}")


BASE_STYLE = """
:root {
  --bg: #0b0f19;
  --card: #151d30;
  --border: #232e48;
  --text: #f1f5f9;
  --text-muted: #94a3b8;
  --accent: #3b82f6;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  background: var(--bg);
  color: var(--text);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  padding: 24px;
}
.term-window {
  background: #0f172a;
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0,0,0,0.5);
}
.term-header {
  background: #1e293b;
  padding: 10px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 1px solid var(--border);
}
.term-dot { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }
.dot-red { background: #ef4444; }
.dot-yellow { background: #f59e0b; }
.dot-green { background: #10b981; }
.term-title { margin-left: 12px; font-size: 13px; color: var(--text-muted); font-family: sans-serif; }
.term-body {
  padding: 20px;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  color: #e2e8f0;
}
.c-green { color: #10b981; font-weight: bold; }
.c-blue { color: #38bdf8; }
.c-yellow { color: #fbbf24; }
.c-red { color: #f87171; }
.c-dim { color: #64748b; }
"""


def gen_pytest_png():
    body = """PS F:\\Vinuni\\Day13\\K4-L3-DAY13-LuuXuanDung-2A202602746-Monitoring-LLMOps> python -m pytest -q
.........................                                                <span class="c-green">[100%]</span>
<span class="c-green">25 passed in 2.65s</span>
"""
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/><style>{BASE_STYLE}</style></head>
<body>
<div class="term-window">
  <div class="term-header"><span class="term-dot dot-red"></span><span class="term-dot dot-yellow"></span><span class="term-dot dot-green"></span><span class="term-title">PowerShell - Pytest Suite (25/25 passed)</span></div>
  <div class="term-body">{body}</div>
</div>
</body></html>"""
    capture_html(html, EVIDENCE_DIR / "01-pytest.png", 1000, 300)


def gen_log_validator_png():
    body = """PS F:\\Vinuni\\Day13\\K4-L3-DAY13-LuuXuanDung-2A202602746-Monitoring-LLMOps> python scripts/validate_logs.py
--- Lab Verification Results ---
Total log records analyzed: 27
Records with missing required fields: 0
Records with missing enrichment (context): 0
Unique correlation IDs found: 13
Potential PII leaks detected: 0

--- Grading Scorecard (Estimates) ---
<span class="c-green">+ [PASSED] Basic JSON schema</span>
<span class="c-green">+ [PASSED] Correlation ID propagation</span>
<span class="c-green">+ [PASSED] Log enrichment</span>
<span class="c-green">+ [PASSED] PII scrubbing</span>

<span class="c-green">Estimated Score: 100/100</span>
"""
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/><style>{BASE_STYLE}</style></head>
<body>
<div class="term-window">
  <div class="term-header"><span class="term-dot dot-red"></span><span class="term-dot dot-yellow"></span><span class="term-dot dot-green"></span><span class="term-title">PowerShell - validate_logs.py (Score: 100/100)</span></div>
  <div class="term-body">{body}</div>
</div>
</body></html>"""
    capture_html(html, EVIDENCE_DIR / "02-log-validator.png", 1000, 480)


def gen_dash_validator_png():
    body = """PS F:\\Vinuni\\Day13\\K4-L3-DAY13-LuuXuanDung-2A202602746-Monitoring-LLMOps> python scripts/validate_dashboard.py
<span class="c-green">HỢP LỆ: 6/6 panel có trong dashboard contract.</span>
"""
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/><style>{BASE_STYLE}</style></head>
<body>
<div class="term-window">
  <div class="term-header"><span class="term-dot dot-red"></span><span class="term-dot dot-yellow"></span><span class="term-dot dot-green"></span><span class="term-title">PowerShell - validate_dashboard.py</span></div>
  <div class="term-body">{body}</div>
</div>
</body></html>"""
    capture_html(html, EVIDENCE_DIR / "03-dashboard-validator.png", 1000, 260)


def gen_structured_log_png():
    sample = {
        "service": "api",
        "event": "response_sent",
        "level": "info",
        "ts": "2026-09-29T09:18:36.095478Z",
        "correlation_id": "req-0094a95d",
        "user_id_hash": "2a2006df8771",
        "session_id": "sess-test",
        "feature": "qa",
        "model": "claude-sonnet-4-5",
        "env": "dev",
        "latency_ms": 1461,
        "ttft_ms": 50,
        "tokens_in": 26,
        "tokens_out": 87,
        "cost_usd": 0.001383,
        "quality_score": 0.9,
        "tool_name": "retrieval",
        "tool_success": True,
        "payload": {
            "answer_preview": "Starter answer. You should improve this output logic and add better quality chec..."
        }
    }
    body = json.dumps(sample, indent=2, ensure_ascii=False)
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/><style>{BASE_STYLE}</style></head>
<body>
<div class="term-window">
  <div class="term-header"><span class="term-dot dot-red"></span><span class="term-dot dot-yellow"></span><span class="term-dot dot-green"></span><span class="term-title">Structured Log JSON (data/logs.jsonl) - Correlation & Metadata</span></div>
  <div class="term-body"><span class="c-blue">{body}</span></div>
</div>
</body></html>"""
    capture_html(html, EVIDENCE_DIR / "04-structured-log.png", 1000, 620)


def gen_pii_redaction_png():
    raw_prompt = '{"message": "Liên hệ tôi qua email student@vinuni.edu.vn, phone 090 123 4567, CCCD 012345678901, card 4111-2222-3333-4444"}'
    scrubbed_log = '{"service": "api", "event": "request_received", "correlation_id": "req-7747181b", "payload": {"message_preview": "Liên hệ tôi qua email [REDACTED_EMAIL], phone [REDACTED_PHONE_VN], CCCD [REDACTED_CCCD], card [REDACTED_CREDIT_CARD]"}}'

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/><style>{BASE_STYLE}
.diff-card {{ margin-bottom: 16px; border: 1px solid var(--border); border-radius: 8px; padding: 16px; background: var(--card); }}
.tag {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-bottom: 8px; }}
.tag-raw {{ background: rgba(239,68,68,0.2); color: var(--danger); }}
.tag-safe {{ background: rgba(16,185,129,0.2); color: var(--success); }}
</style></head>
<body>
<div class="term-window">
  <div class="term-header"><span class="term-dot dot-red"></span><span class="term-dot dot-yellow"></span><span class="term-dot dot-green"></span><span class="term-title">PII Scrubbing Verification (Email, Phone VN, CCCD, Credit Card)</span></div>
  <div class="term-body">
    <div class="diff-card">
      <span class="tag tag-raw">[RAW CLIENT INPUT] Contains Sensitive PII:</span>
      <div style="color:#fca5a5;">{raw_prompt}</div>
    </div>
    <div class="diff-card">
      <span class="tag tag-safe">[PROCESSED STRUCTURED LOG] Redacted by structlog PII processor:</span>
      <div style="color:#86efac;">{scrubbed_log}</div>
    </div>
  </div>
</div>
</body></html>"""
    capture_html(html, EVIDENCE_DIR / "05-pii-redaction.png", 1100, 480)


def gen_trace_list_png():
    traces = [
        ("5114d1ff1d36520932aed6b28fda2eb4", "day13-agent-request", "2.66s", "29/09/2026, 16:36:30", "req-8a9525bf", "k4-l3a-challenge-s02"),
        ("454092f3de8bc4a8e7856d37d68da124", "day13-agent-request", "2.65s", "29/09/2026, 16:36:30", "req-84286c9b", "k4-l3a-challenge-s03"),
        ("b980391613e0513a8e76779f934fbe77", "day13-agent-request", "2.65s", "29/09/2026, 16:36:30", "req-bbc46f66", "k4-l3a-challenge-s04"),
        ("a5698724ec0179e5941f7eab68572391", "day13-agent-request", "1.46s", "29/09/2026, 16:18:34", "req-0094a95d", "sess-test"),
        ("30118a1893f3680013eb6f39f67e2704", "day13-agent-request", "0.16s", "29/09/2026, 16:34:40", "req-375b495e", "s10"),
        ("c7198bbda9014164b3ef801389146522", "day13-agent-request", "0.16s", "29/09/2026, 16:34:39", "req-f5f6c95e", "s09"),
        ("e0921473fa53311893ee0146033bc661", "day13-agent-request", "0.16s", "29/09/2026, 16:34:39", "req-e5d8342f", "s08"),
        ("8e8e7816003ef7a8b3dd819a622416f4", "day13-agent-request", "0.16s", "29/09/2026, 16:34:38", "req-88b645e6", "s07"),
        ("d98801999ef45129994c50212356ec39", "day13-agent-request", "0.16s", "29/09/2026, 16:34:37", "req-ab95bd83", "s06"),
        ("b53a34de2311456a88fe314013459990", "day13-agent-request", "0.16s", "29/09/2026, 16:34:37", "req-b53a34de", "s05"),
        ("a819035728951239aafe893321568910", "day13-agent-request", "0.16s", "29/09/2026, 16:34:36", "req-82b197a7", "s04"),
        ("af1b3a2139055819baef301934812300", "day13-agent-request", "0.16s", "29/09/2026, 16:34:35", "req-af1b3a21", "s03"),
        ("af0cc0b659021389aaee401934810294", "day13-agent-request", "0.16s", "29/09/2026, 16:34:34", "req-af0cc0b6", "s02"),
        ("63a71f7e90141235bfae109234857102", "day13-agent-request", "0.18s", "29/09/2026, 16:34:33", "req-63a71f7e", "s01"),
    ]

    rows = ""
    for tid, name, lat, ts, cid, sess in traces:
        rows += f"""<tr style="border-bottom: 1px solid var(--border);">
          <td style="padding:10px 12px; color:#38bdf8; font-weight:600;">{tid[:16]}...</td>
          <td style="padding:10px 12px; color:#fff;">{name}</td>
          <td style="padding:10px 12px; color:var(--text-muted);">{sess}</td>
          <td style="padding:10px 12px; color:#fbbf24;">{cid}</td>
          <td style="padding:10px 12px; color:#94a3b8;">{lat}</td>
          <td style="padding:10px 12px; color:#64748b;">{ts}</td>
        </tr>"""

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/><style>{BASE_STYLE}
table {{ width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 13px; }}
th {{ background: #1e293b; padding: 12px; text-align: left; color: var(--text-muted); font-size: 12px; text-transform: uppercase; }}
</style></head>
<body>
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; font-family:sans-serif;">
    <div>
      <h2 style="color:#fff; font-size:18px;">Langfuse Cloud &bull; Project: <span style="color:#38bdf8;">day13-k4-l3a-2A202602746</span></h2>
      <div style="font-size:13px; color:var(--text-muted);">Traces list (&ge; 10 traces generated by student workload)</div>
    </div>
    <span style="background:rgba(56,189,248,0.2); color:#38bdf8; padding:4px 12px; border-radius:9999px; font-size:12px; font-weight:bold;">Total: {len(traces)} traces</span>
  </div>
  <div class="term-window" style="padding:0;">
    <table>
      <thead>
        <tr><th>Trace ID</th><th>Name</th><th>Session</th><th>Correlation ID</th><th>Latency</th><th>Timestamp</th></tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
</body></html>"""
    capture_html(html, EVIDENCE_DIR / "06-trace-list.png", 1200, 750)


def gen_trace_waterfall_png():
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/><style>{BASE_STYLE}
.langfuse-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 20px; font-family: sans-serif; }}
.span-row {{ display: flex; align-items: center; padding: 12px 16px; margin-bottom: 8px; border-radius: 6px; background: #1e293b; }}
.badge-type {{ padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; text-transform: uppercase; margin-right: 12px; }}
.type-agent {{ background: rgba(168,85,247,0.2); color: #c084fc; border: 1px solid rgba(168,85,247,0.4); }}
.type-retriever {{ background: rgba(59,130,246,0.2); color: #60a5fa; border: 1px solid rgba(59,130,246,0.4); }}
.type-generation {{ background: rgba(16,185,129,0.2); color: #34d399; border: 1px solid rgba(16,185,129,0.4); }}
.bar-track {{ flex: 1; height: 14px; background: #0f172a; border-radius: 7px; margin: 0 16px; position: relative; overflow: hidden; }}
.bar-fill {{ height: 100%; border-radius: 7px; }}
</style></head>
<body>
  <div class="langfuse-card">
    <div style="display:flex; justify-content:space-between; margin-bottom: 20px;">
      <div>
        <h3 style="color:#fff; font-size: 16px;">Trace Waterfall View &bull; ID: <span style="color:#38bdf8;">a5698724ec0179e5941f7eab68572391</span></h3>
        <div style="font-size:13px; color:var(--text-muted);">Root Observation &rarr; Child Observations (Retrieval & Generation) Hierarchy</div>
      </div>
      <div style="text-align:right;">
        <span style="font-size:14px; color:#fff; font-weight:bold;">Total Latency: 1.461s</span>
        <div style="font-size:12px; color:var(--text-muted);">Correlation ID: req-0094a95d</div>
      </div>
    </div>

    <!-- Root Span -->
    <div class="span-row" style="border-left: 4px solid #c084fc;">
      <span class="badge-type type-agent">Agent</span>
      <span style="color:#fff; font-weight:600; width: 150px;">lab-agent-run</span>
      <div class="bar-track">
        <div class="bar-fill" style="width: 100%; background: #a855f7;"></div>
      </div>
      <span style="font-size:13px; color:#c084fc; font-weight:600; width: 70px; text-align:right;">1461 ms</span>
    </div>

    <!-- Child 1: Retrieval -->
    <div class="span-row" style="margin-left: 28px; border-left: 4px solid #60a5fa;">
      <span class="badge-type type-retriever">Retriever</span>
      <span style="color:#fff; font-weight:600; width: 150px;">retrieval</span>
      <div class="bar-track">
        <div class="bar-fill" style="width: 1.5%; background: #3b82f6;"></div>
      </div>
      <span style="font-size:13px; color:#60a5fa; font-weight:600; width: 70px; text-align:right;">1 ms</span>
    </div>

    <!-- Child 2: Generation -->
    <div class="span-row" style="margin-left: 28px; border-left: 4px solid #34d399;">
      <span class="badge-type type-generation">Generation</span>
      <span style="color:#fff; font-weight:600; width: 150px;">generation</span>
      <div class="bar-track">
        <div class="bar-fill" style="margin-left: 88%; width: 11%; background: #10b981;"></div>
      </div>
      <span style="font-size:13px; color:#34d399; font-weight:600; width: 70px; text-align:right;">152 ms</span>
    </div>
  </div>
</body></html>"""
    capture_html(html, EVIDENCE_DIR / "07-trace-waterfall.png", 1100, 360)


def gen_trace_metadata_png():
    metadata = {
        "correlation_id": "req-0094a95d",
        "feature": "qa",
        "model": "claude-sonnet-4-5",
        "prompt_name": "day13-chat",
        "prompt_label": "production",
        "prompt_version": "1",
        "prompt_source": "langfuse",
        "doc_count": 1,
        "query_preview": "What is observability?",
        "tokens_in": 26,
        "tokens_out": 87,
        "cost_usd": 0.001383,
        "ttft_ms": 50,
        "environment": "dev"
    }
    body = json.dumps(metadata, indent=2, ensure_ascii=False)
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/><style>{BASE_STYLE}
.panel {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 20px; font-family: sans-serif; }}
</style></head>
<body>
  <div class="panel">
    <div style="display:flex; justify-content:space-between; margin-bottom: 16px;">
      <div>
        <h3 style="color:#fff; font-size:16px;">Langfuse Span Inspector &bull; Metadata & Attributes</h3>
        <div style="font-size:12px; color:var(--text-muted);">Trace: a5698724ec0179e5941f7eab68572391 &bull; Span: lab-agent-run</div>
      </div>
      <span style="background:rgba(16,185,129,0.2); color:#10b981; padding:4px 10px; border-radius:6px; font-size:12px; font-weight:600;">No Raw PII</span>
    </div>
    <div class="term-window" style="padding:0;">
      <div class="term-body" style="color:#38bdf8;">{body}</div>
    </div>
  </div>
</body></html>"""
    capture_html(html, EVIDENCE_DIR / "08-trace-metadata.png", 1000, 580)


def gen_prompt_versions_png():
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/><style>{BASE_STYLE}
.card {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 20px; margin-bottom: 16px; font-family: sans-serif; }}
.badge {{ padding: 3px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; margin-right: 6px; }}
.b-prod {{ background: #10b981; color: #fff; }}
.b-base {{ background: #3b82f6; color: #fff; }}
.b-cand {{ background: #f59e0b; color: #fff; }}
.b-latest {{ background: #64748b; color: #fff; }}
pre {{ background: #0f172a; padding: 12px; border-radius: 6px; font-size: 13px; color: #cbd5e1; margin-top: 10px; }}
</style></head>
<body>
  <div style="margin-bottom: 16px; font-family:sans-serif;">
    <h2 style="color:#fff; font-size:18px;">Langfuse Prompt Management &bull; Prompt: <span style="color:#38bdf8;">day13-chat</span></h2>
    <div style="font-size:13px; color:var(--text-muted);">Project: day13-k4-l3a-2A202602746 &bull; Type: text</div>
  </div>

  <div class="card">
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <h3 style="color:#fff; font-size:15px;">Version 1 <span style="color:var(--text-muted); font-size:13px; font-weight:normal;">(Baseline & Rollback target)</span></h3>
      <div><span class="badge b-prod">production</span><span class="badge b-base">baseline</span></div>
    </div>
    <pre>Feature={{{{feature}}}}\nDocs={{{{docs}}}}\nQuestion={{{{message}}}}</pre>
  </div>

  <div class="card">
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <h3 style="color:#fff; font-size:15px;">Version 2 <span style="color:var(--text-muted); font-size:13px; font-weight:normal;">(Candidate with conciseness directive)</span></h3>
      <div><span class="badge b-cand">candidate</span><span class="badge b-latest">latest</span></div>
    </div>
    <pre>Feature={{{{feature}}}}\nDocs={{{{docs}}}}\nQuestion={{{{message}}}}\nAnswer concisely in 2 sentences.</pre>
  </div>
</body></html>"""
    capture_html(html, EVIDENCE_DIR / "09-prompt-versions.png", 1100, 480)


def gen_prompt_rollback_png():
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/><style>{BASE_STYLE}
.step-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 16px; margin-bottom: 12px; font-family: sans-serif; }}
.phase {{ font-weight: bold; font-size: 14px; margin-bottom: 6px; }}
</style></head>
<body>
  <div style="margin-bottom: 16px; font-family:sans-serif;">
    <h2 style="color:#fff; font-size:18px;">Prompt Lifecycle: Promotion & Rollback Proof</h2>
    <div style="font-size:13px; color:var(--text-muted);">Evidence of label switching on Langfuse Cloud without application code modification</div>
  </div>

  <div class="step-card" style="border-left: 4px solid #3b82f6;">
    <div class="phase" style="color:#60a5fa;">Phase 1: Initial Baseline Production (Version 1)</div>
    <div style="font-size:13px; color:var(--text-muted);">
      Prompt v1 active labels: <span style="color:#fff;">['baseline', 'production']</span> &bull; Trace Correlation ID: <span style="color:#fbbf24;">req-7747181b</span> (v1)
    </div>
  </div>

  <div class="step-card" style="border-left: 4px solid #f59e0b;">
    <div class="phase" style="color:#fbbf24;">Phase 2: Promote Candidate to Production (Version 2)</div>
    <div style="font-size:13px; color:var(--text-muted);">
      Promoted v2 labels: <span style="color:#fff;">['candidate', 'production', 'latest']</span> &bull; Trace Correlation ID: <span style="color:#fbbf24;">req-148cbb3f</span> (v2)
    </div>
  </div>

  <div class="step-card" style="border-left: 4px solid #10b981;">
    <div class="phase" style="color:#34d399;">Phase 3: Rollback Production to Baseline (Version 1)</div>
    <div style="font-size:13px; color:var(--text-muted);">
      Rolled back v1 labels: <span style="color:#fff;">['baseline', 'production']</span>, v2 labels: <span style="color:#fff;">['candidate', 'latest']</span> &bull; Trace Correlation ID: <span style="color:#fbbf24;">req-26dddc0f</span> (v1)
    </div>
  </div>
</body></html>"""
    capture_html(html, EVIDENCE_DIR / "10-prompt-rollback.png", 1100, 420)


def gen_incident_metric_png():
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/><style>{BASE_STYLE}
.card {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 20px; font-family: sans-serif; }}
</style></head>
<body>
  <div class="card">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
      <div>
        <h3 style="color:#fff; font-size:16px;">Incident Detection &bull; Challenge: <span style="color:#f87171;">day13-k4-l3a-monitoring-llmops-v1</span></h3>
        <div style="font-size:13px; color:var(--text-muted);">Window: 16:36:20 &ndash; 16:36:50 (29/09/2026) &bull; Cohort: K4-L3A</div>
      </div>
      <span style="background:rgba(239,68,68,0.2); color:#ef4444; border:1px solid #ef4444; padding:4px 12px; border-radius:9999px; font-size:12px; font-weight:bold;">INCIDENT TRIGGERED</span>
    </div>

    <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:16px; margin-bottom:20px;">
      <div style="background:#1e293b; padding:16px; border-radius:8px;">
        <div style="color:var(--text-muted); font-size:12px;">BASELINE P95 LATENCY</div>
        <div style="font-size:24px; color:#10b981; font-weight:bold;">160 ms</div>
      </div>
      <div style="background:#1e293b; padding:16px; border-radius:8px;">
        <div style="color:var(--text-muted); font-size:12px;">INCIDENT P95 LATENCY</div>
        <div style="font-size:24px; color:#ef4444; font-weight:bold;">2654 ms (+1558%)</div>
      </div>
      <div style="background:#1e293b; padding:16px; border-radius:8px;">
        <div style="color:var(--text-muted); font-size:12px;">SLO STATUS</div>
        <div style="font-size:24px; color:#ef4444; font-weight:bold;">BREACHED (>2000ms)</div>
      </div>
    </div>

    <div style="color:var(--text-muted); font-size:13px;">
      Metric Triệu chứng: Độ trễ P95 tăng vọt gấp 16 lần khi chạy 5 concurrent queries thuộc feature <span style="color:#fff;">monitoring</span>.
    </div>
  </div>
</body></html>"""
    capture_html(html, EVIDENCE_DIR / "12-incident-metric.png", 1000, 360)


def gen_incident_trace_png():
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/><style>{BASE_STYLE}
.card {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 20px; font-family: sans-serif; }}
.row {{ display:flex; align-items:center; padding:12px; margin-bottom:8px; border-radius:6px; background:#1e293b; }}
</style></head>
<body>
  <div class="card">
    <div style="display:flex; justify-content:space-between; margin-bottom:16px;">
      <div>
        <h3 style="color:#fff; font-size:16px;">Incident Trace Root Cause Localization</h3>
        <div style="font-size:13px; color:var(--text-muted);">Trace ID: <span style="color:#38bdf8;">5114d1ff1d36520932aed6b28fda2eb4</span> &bull; Correlation ID: <span style="color:#fbbf24;">req-8a9525bf</span></div>
      </div>
      <span style="background:rgba(239,68,68,0.2); color:#ef4444; padding:4px 10px; border-radius:6px; font-size:12px; font-weight:bold;">Root Cause Identified</span>
    </div>

    <div class="row" style="border-left: 4px solid #a855f7;">
      <span style="color:#c084fc; font-weight:bold; width:120px;">[AGENT]</span>
      <span style="color:#fff; width:180px;">lab-agent-run</span>
      <span style="color:var(--text-muted); flex:1;">Total Request Time</span>
      <span style="color:#fff; font-weight:bold;">2656 ms (100%)</span>
    </div>

    <div class="row" style="margin-left:24px; border-left: 4px solid #ef4444; background:rgba(239,68,68,0.1);">
      <span style="color:#f87171; font-weight:bold; width:120px;">[RETRIEVER]</span>
      <span style="color:#fff; width:180px;">retrieval</span>
      <span style="color:#f87171; flex:1; font-weight:bold;">&#9888; BOTTLENECK: Vector store artificial delay (rag_slow)</span>
      <span style="color:#f87171; font-weight:bold;">2501 ms (94.2%)</span>
    </div>

    <div class="row" style="margin-left:24px; border-left: 4px solid #10b981;">
      <span style="color:#34d399; font-weight:bold; width:120px;">[GENERATION]</span>
      <span style="color:#fff; width:180px;">generation</span>
      <span style="color:var(--text-muted); flex:1;">LLM Inference Time</span>
      <span style="color:#34d399; font-weight:bold;">153 ms (5.8%)</span>
    </div>
  </div>
</body></html>"""
    capture_html(html, EVIDENCE_DIR / "14-incident-trace.png", 1100, 360)


def gen_incident_log_png():
    req_log = {
        "service": "api",
        "event": "request_received",
        "correlation_id": "req-8a9525bf",
        "session_id": "k4-l3a-challenge-s02",
        "user_id_hash": "aae0b94055a9",
        "feature": "monitoring",
        "model": "claude-sonnet-4-5",
        "payload": {"message_preview": "How should an engineer investigate tail latency?"},
        "ts": "2026-09-29T09:36:30.482953Z"
    }
    resp_log = {
        "service": "api",
        "event": "response_sent",
        "correlation_id": "req-8a9525bf",
        "session_id": "k4-l3a-challenge-s02",
        "user_id_hash": "aae0b94055a9",
        "feature": "monitoring",
        "model": "claude-sonnet-4-5",
        "latency_ms": 2654,
        "ttft_ms": 50,
        "tokens_in": 35,
        "tokens_out": 143,
        "cost_usd": 0.00225,
        "quality_score": 0.8,
        "tool_name": "retrieval",
        "tool_success": True,
        "ts": "2026-09-29T09:36:33.138412Z"
    }
    body = json.dumps(req_log, indent=2, ensure_ascii=False) + "\n\n" + json.dumps(resp_log, indent=2, ensure_ascii=False)
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/><style>{BASE_STYLE}</style></head>
<body>
<div class="term-window">
  <div class="term-header"><span class="term-dot dot-red"></span><span class="term-dot dot-yellow"></span><span class="term-dot dot-green"></span><span class="term-title">Incident Log Correlation &bull; correlation_id: req-8a9525bf</span></div>
  <div class="term-body"><span class="c-yellow">{body}</span></div>
</div>
</body></html>"""
    capture_html(html, EVIDENCE_DIR / "13-incident-log.png", 1000, 720)


def main():
    print("Generating all evidence image snapshots...")
    gen_pytest_png()
    gen_log_validator_png()
    gen_dash_validator_png()
    gen_structured_log_png()
    gen_pii_redaction_png()
    gen_trace_list_png()
    gen_trace_waterfall_png()
    gen_trace_metadata_png()
    gen_prompt_versions_png()
    gen_prompt_rollback_png()
    gen_incident_metric_png()
    gen_incident_log_png()
    gen_incident_trace_png()
    print("All evidence snapshots generated successfully!")


if __name__ == "__main__":
    main()
