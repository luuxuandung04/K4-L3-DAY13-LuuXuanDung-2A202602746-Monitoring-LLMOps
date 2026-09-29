# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1: High P95 Latency

- Tên: high_p95_latency
- Severity: critical
- Duration: 5m
- Kênh thông báo: Slack (#alerts-llmops-l3a)
- SLI/SLO liên quan: primary_slo.fast_successful_requests (P95 <= 3000ms)
- Điều kiện và thời gian duy trì: Latency P95 vượt quá 3000ms liên tục trong 5 phút.
- Ảnh hưởng tới người dùng: Người dùng phản hồi chatbot chậm trễ bất thường, giao diện chờ phản hồi lâu hoặc bị timeout.
- Ba bước kiểm tra đầu tiên:
  1. Mở Dashboard kiểm tra panel Latency (P50, P95, TTFT) để xác định triệu chứng xảy ra từ khi nào.
  2. Lọc `data/logs.jsonl` tìm các event `response_sent` có `latency_ms > 3000`, trích xuất `correlation_id`.
  3. Mở Langfuse trace với `correlation_id` đó, kiểm tra waterfall view xem span `retrieval` hay `generation` bị chậm.
- Mitigation tạm thời: Bật fallback sang context cache, giảm timeout retrieval hoặc hạ model xuống phiên bản nhẹ hơn nếu LLM bị nghẽn.
- Owner: oncall-llmops

## Alert 2: High Error Rate

- Tên: high_error_rate
- Severity: critical
- Duration: 3m
- Kênh thông báo: Slack (#alerts-llmops-l3a)
- SLI/SLO liên quan: guardrails.error_rate_pct_max (<= 2%)
- Điều kiện và thời gian duy trì: Tỉ lệ lỗi request (`request_failed`) vượt quá 2% trong 3 phút.
- Ảnh hưởng tới người dùng: Người dùng nhận mã lỗi 500 hoặc thông báo hệ thống không thể xử lý yêu cầu.
- Ba bước kiểm tra đầu tiên:
  1. Mở Dashboard xem panel Errors kiểm tra breakdown theo `error_type` và tỉ lệ `retrieval_success_rate`.
  2. Tra cứu trong `data/logs.jsonl` các dòng có `event == "request_failed"` để xem `payload.detail` và `correlation_id`.
  3. Mở trace trên Langfuse để xem exception stack trace chi tiết ở span con tương ứng.
- Mitigation tạm thời: Khởi động lại service hoặc pod nếu rò rỉ bộ nhớ; kích hoạt chế độ degraded response nếu vector store timeout.
- Owner: oncall-llmops

## Alert 3: Cost Budget Breach

- Tên: cost_budget_breach
- Severity: warning
- Duration: 10m
- Kênh thông báo: Slack (#alerts-llmops-l3a)
- SLI/SLO liên quan: guardrails.daily_cost_usd_max (<= 2.50 USD)
- Điều kiện và thời gian duy trì: Tổng chi phí tiêu thụ tích lũy trong ngày vượt quá 2.50 USD.
- Ảnh hưởng tới người dùng: Nguy cơ cạn kiệt hạn ngạch API trả phí dẫn đến toàn bộ hệ thống bị chặn gọi model.
- Ba bước kiểm tra đầu tiên:
  1. Mở Dashboard xem panel Cost và Tokens để phát hiện đột biến tiêu thụ token input hay output.
  2. Kiểm tra log lọc các request có `cost_usd` hoặc `tokens_out` cao bất thường để tìm prompt/session liên quan.
  3. Đối chiếu trên Langfuse trace xem có hiện tượng loop sinh text không dừng hoặc prompt injection không.
- Mitigation tạm thời: Giới hạn `max_tokens` của response, áp dụng rate-limiting theo session/user, hoặc chuyển hướng traffic sang model chi phí thấp.
- Owner: finops-lead
