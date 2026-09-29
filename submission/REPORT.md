# Báo cáo cá nhân — K4-L3A Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Lưu Xuân Dũng
- **MSSV:** 2A202602746
- **Lớp:** K4-L3A
- **Repository URL:** https://github.com/luuxuandung04/K4-L3-DAY13-LuuXuanDung-2A202602746-Monitoring-LLMOps
- **Commit SHA cuối:** `eb545356bcff84c30cca9c07e0958260a045a16f`
- **Challenge ID:** `day13-k4-l3a-monitoring-llmops-v1`
- **Tên project Langfuse cá nhân:** `day13-k4-l3a-2A202602746`

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/01-pytest.png` |
| Log validator | `evidence/02-log-validator.png` |
| Dashboard validator | `evidence/03-dashboard-validator.png` |
| Structured log | `evidence/04-structured-log.png` |
| PII redaction | `evidence/05-pii-redaction.png` |
| Trace list | `evidence/06-trace-list.png` |
| Trace waterfall | `evidence/07-trace-waterfall.png` |
| Trace metadata | `evidence/08-trace-metadata.png` |
| Prompt versions | `evidence/09-prompt-versions.png` |
| Prompt rollback | `evidence/10-prompt-rollback.png` |
| Dashboard runtime | `evidence/11-dashboard-overview.png` |
| Incident metric | `evidence/12-incident-metric.png` |
| Incident log | `evidence/13-incident-log.png` |
| Incident trace | `evidence/14-incident-trace.png` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 30/100 | 100/100 | Đạt điểm tuyệt đối, vượt qua toàn bộ 4 tiêu chuẩn kiểm tra |
| `validate_dashboard.py` | HỢP LỆ: 6/6 panel | HỢP LỆ: 6/6 panel | Đầy đủ 6 panel theo đúng contract YAML và có dashboard runtime |
| `pytest` | 22 passed | 25 passed | Bổ sung test kiểm tra PII cho CCCD, thẻ thanh toán, passport |
| Số traces hợp lệ | 10 traces | 15+ traces | Traces tự sinh trên project cá nhân, có phân cấp Root -> Retrieval -> Generation |
| Số PII leak | 0 leak | 0 leak | Kiểm tra sạch các mẫu Email, SĐT VN, CCCD, Thẻ tín dụng, Passport |
| Latency P95 / TTFT P95 | 1704.0 ms / 50.0 ms | 160.6 ms / 50.0 ms (thường) / 2654 ms (challenge) | Phản ánh chính xác tail latency khi tải thường và khi inject sự cố |
| Retrieval success rate | 100% | 100% | Vector store retrieval vận hành ổn định trong suốt bài lab |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:**
  Được triển khai trong `CorrelationIdMiddleware` (`app/middleware.py`). Khi request đến, middleware thực hiện `clear_contextvars()` để xóa context cũ, ngăn ngừa rò rỉ giữa các request đồng thời. Tiếp theo, middleware trích xuất header `x-request-id` từ client; nếu không có hoặc rỗng thì sinh mã mới theo quy ước `f"req-{uuid.uuid4().hex[:8]}"`. ID này được bind vào contextvars qua `bind_contextvars(correlation_id=correlation_id)`, lưu vào `request.state.correlation_id`, và trả ngược lại cho client qua response headers `x-request-id` cùng `x-response-time-ms`.
- **Các metadata được ghi vào structured log:**
  Trong route `POST /chat` (`app/main.py`), các metadata được bind vào structlog contextvars trước khi log sự kiện `request_received`: `user_id_hash` (băm SHA256 12 ký tự để ẩn danh), `session_id`, `feature`, `model`, và `env`. Nhờ `merge_contextvars`, toàn bộ các log tiếp theo trong cùng request (`response_sent`, `request_failed`) đều tự động kế thừa các trường này cùng các số liệu vận hành: `latency_ms`, `ttft_ms`, `tokens_in`, `tokens_out`, `cost_usd`, `quality_score`, `tool_name`, `tool_success`, và `payload`.
- **Cách bảo đảm PII được scrub trước khi ghi:**
  Xây dựng processor đệ quy `scrub_event` trong `app/logging_config.py` và đăng ký vào chuỗi processors của `structlog` **TRƯỚC** `JsonlFileProcessor` và `JSONRenderer`. Hàm sử dụng bộ regex từ `app/pii.py` (Email, SĐT Việt Nam các định dạng, CCCD 12 số, Thẻ thanh toán 16 số, Passport) để thay thế thông tin nhạy cảm thành `[REDACTED_<TYPE>]`. Vì việc làm sạch diễn ra trước khi dữ liệu được serialize và ghi ra file/console, dữ liệu PII thô tuyệt đối không xuất hiện trong `data/logs.jsonl`.
- **Cách kiểm chứng kết quả:**
  Chạy `python scripts/validate_logs.py` đọc toàn bộ file `data/logs.jsonl` và đạt kết quả tối đa 100/100, xác nhận 0 rò rỉ PII, 0 thiếu trường context, và đủ correlation ID. Minh chứng tại `evidence/02-log-validator.png`, `evidence/04-structured-log.png`, và `evidence/05-pii-redaction.png`.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:**
  Cấu hình public/secret key trong `.env` trỏ về project `day13-k4-l3a-2A202602746` trên Langfuse Cloud. Toàn bộ traces sinh ra từ workload có tag `["lab", feature, self.model]`, metadata mang `correlation_id` và `user_id_hash` cá nhân. Minh chứng danh sách >= 10 traces trên Langfuse được lưu tại `evidence/06-trace-list.png`.
- **Cấu trúc root/retrieval/generation observations:**
  Sử dụng Langfuse Python SDK v4 decorator `@observe`:
  - Root observation: Gắn `@observe(name="lab-agent-run", as_type="agent")` cho hàm `LabAgent.run()`.
  - Child observation 1: Gắn `@observe(name="retrieval", as_type="retriever")` cho hàm `_retrieve()`, đo đạc thời gian truy xuất tài liệu và số lượng doc.
  - Child observation 2: Gắn `@observe(name="generation", as_type="generation")` cho hàm `_generate()`, ghi nhận model name, prompt liên kết, số `input_tokens`, `output_tokens`, `cost_usd`, và `ttft_ms`.
  Quan hệ cha - con được OpenTelemetry context propagation tự động duy trì, hiển thị rõ ràng trên Waterfall view (`evidence/07-trace-waterfall.png`).
- **Cách nối trace với log:**
  Trong root observation `lab-agent-run`, `correlation_id` từ middleware được đưa vào metadata của trace thông qua `propagate_attributes(metadata={"correlation_id": correlation_id, ...})`. Khi phát hiện log bất thường trong `data/logs.jsonl`, kỹ sư chỉ cần lấy `correlation_id` và tìm kiếm trên Langfuse để mở đúng trace tương ứng.
- **Prompt name:** `day13-chat`
- **Version/label baseline:** Version 1 (labels: `baseline`, `production`)
- **Version/label candidate:** Version 2 (label: `candidate`)
- **Trace ID của mỗi version:**
  - Trace dùng Prompt Version 1 (baseline): `a5698724ec0179e5941f7eab68572391` (correlation_id: `req-0094a95d` / `req-7747181b`)
  - Trace dùng Prompt Version 2 (promoted candidate): `b980391613e0513a8e76779f934fbe77` (correlation_id: `req-148cbb3f`)
  - Trace sau khi Rollback về Version 1: `5114d1ff1d36520932aed6b28fda2eb4` (correlation_id: `req-26dddc0f` / `req-8a9525bf`)
- **Cách promote và rollback `production`:**
  - Promote: Cập nhật nhãn `production` cho Version 2 qua SDK: `client.update_prompt(name='day13-chat', version=2, new_labels=['candidate', 'production'])`. Ứng dụng đọc nhãn `production` sẽ lập tức chuyển sang phục vụ câu trả lời của Version 2 mà không cần sửa code.
  - Rollback: Khi cần quay về bản ổn định, cập nhật nhãn `production` về lại Version 1: `client.update_prompt(name='day13-chat', version=1, new_labels=['baseline', 'production'])`. Minh chứng tại `evidence/09-prompt-versions.png` và `evidence/10-prompt-rollback.png`.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:**
  Xây dựng dashboard trực quan (`evidence/11-dashboard-overview.png`) từ nguồn `data/logs.jsonl` đáp ứng contract tại `config/dashboard.yaml`:
  1. *Panel 1 (Latency)*: P50 (153ms), P95 (2654ms khi có incident), P99 (2654ms), TTFT P95 (50ms); threshold line P95 <= 3000ms.
  2. *Panel 2 (Traffic)*: Tổng số request (18 requests), throughput (6.9 req/min), threshold >= 1 req/min.
  3. *Panel 3 (Errors & Retrieval)*: Error rate (0.0%), breakdown lỗi, retrieval success rate (100.0%), threshold error <= 2.0%.
  4. *Panel 4 (Cost)*: Tổng chi phí ($0.0397 USD), trung bình trên mỗi request ($0.00221 USD), threshold <= $2.50 USD.
  5. *Panel 5 (Tokens)*: Tổng tokens tiêu thụ (3140 tokens, gồm 615 tokens in và 2525 tokens out), threshold <= 50,000 tokens.
  6. *Panel 6 (Quality)*: Điểm chất lượng trung bình (0.856/1.0), threshold >= 0.75.
- **SLO và lý do chọn:**
  SLO chính: `fast_successful_requests` với target 99.5% trong cửa sổ 28 ngày. Điều kiện: `event == "response_sent" and latency_ms <= 3000`. Ngưỡng 3000ms được chọn dựa trên baseline latency P95 (160ms - 1700ms), đủ để hấp thụ biến động mạng nhưng lập tức vi phạm khi xảy ra sự cố nghẽn retrieval (2.5s) hoặc model chậm.
- **Cách tính error budget:**
  Với target 99.5%, Error Budget là $100\% - 99.5\% = 0.5\%$. Trong 100,000 requests của cửa sổ 28 ngày, số lượng request chậm (>3000ms) hoặc thất bại tối đa được phép là: $100,000 \times 0.5\% = 500$ requests.
- **Ba alert và runbook tương ứng:**
  Cấu hình trong `config/alert_rules.yaml` và chi tiết tại `docs/alerts.md`:
  1. `high_p95_latency`: Severity Critical, condition P95 latency > 3000ms duy trì 5 phút. Runbook: Kiểm tra panel latency, lọc correlation_id chậm trong log, mở trace tìm span nghẽn, bật fallback cache.
  2. `high_error_rate`: Severity Critical, condition error rate > 2.0% duy trì 3 phút. Runbook: Kiểm tra breakdown loại lỗi, xem `payload.detail`, kiểm tra vector store timeout, kích hoạt chế độ degraded response.
  3. `cost_budget_breach`: Severity Warning, condition tổng cost > $2.50 USD trong 10 phút. Runbook: Kiểm tra đột biến tokens input/output, rà soát prompt loop, kích hoạt rate limit hoặc giảm max_tokens.

## 7. Điều tra challenge

- **Challenge ID:** `day13-k4-l3a-monitoring-llmops-v1`
- **Khoảng thời gian điều tra:** 16:36:20 – 16:36:50 (29/09/2026, UTC 09:36:20 – 09:36:50)
- **Triệu chứng từ metrics:**
  Trên Dashboard và `/metrics`, độ trễ P95 tăng vọt từ 160ms lên 2654ms (đoạn concurrency 5 client latency lên đến 13299ms), vượt ngưỡng 2000ms quy định trong `config/challenge.json` (`evidence/12-incident-metric.png`).
- **Log line và correlation ID liên quan:**
  Lọc file `data/logs.jsonl`, phát hiện request bất thường:
  `correlation_id`: `req-8a9525bf` (session `k4-l3a-challenge-s02`, feature `monitoring`, user_id_hash `aae0b94055a9`). Log `response_sent` ghi nhận `latency_ms: 2654`, `ttft_ms: 50` (`evidence/13-incident-log.png`).
- **Trace ID và span gây ảnh hưởng:**
  Tra cứu `req-8a9525bf` trên Langfuse tìm được Trace ID: `5114d1ff1d36520932aed6b28fda2eb4`.
  Mở Waterfall span tree (`evidence/14-incident-trace.png`):
  - Span root `lab-agent-run`: 2656 ms (100%)
  - Span con `retrieval`: **2501 ms (chiếm 94.2% thời gian)**
  - Span con `generation`: **153 ms (chỉ chiếm 5.8% thời gian)**
- **Root cause:**
  Độ trễ tăng cao không xuất phát từ mô hình LLM (vẫn sinh text trong 153ms) mà hoàn toàn do bước truy xuất dữ liệu vector store (`mock_rag.retrieve`) bị nghẽn (kịch bản sự cố `rag_slow` inject độ trễ giả lập 2.5s).
- **Fix action:**
  Vô hiệu hóa kịch bản sự cố qua API control: `POST /incidents/rag_slow/disable`. Cấu hình timeout cho vector store ở mức 1.0s kèm fallback trả về kết quả tài liệu mặc định hoặc cache nếu vector store phản hồi chậm.
- **Preventive measure:**
  1. Thêm metric và alert riêng cho bước retrieval (`retrieval_latency_ms`).
  2. Bổ sung tầng bộ nhớ đệm phân tán (Redis cache) cho các embedding queries phổ biến.
  3. Áp dụng Circuit Breaker pattern: khi vector store chậm liên tiếp quá 3 lần, tự động chuyển sang fallback để bảo vệ trải nghiệm người dùng.

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:**
  Quyết định đặt PII scrubber (`scrub_event`) ở tầng structlog processor trước khi serialize JSON và ghi file. Lý do: Bảo vệ quyền riêng tư dữ liệu là yêu cầu tối thượng trong LLMOps. Nếu scrub ở tầng controller hay sau khi log, dữ liệu nhạy cảm có thể bị lọt vào console, memory buffer hoặc audit log khi xảy ra unhandled exception. Việc xử lý ở middleware/processor của logger bảo đảm 100% dữ liệu đi qua logger đều được thanh lọc triệt để.
- **Một lỗi/blocker đã gặp:**
  Khi kiểm tra Langfuse SDK v4, việc cập nhật child observation `generation` không hiển thị ngay `usage` nếu process kết thúc quá nhanh trước khi OpenTelemetry batch exporter kịp đẩy dữ liệu qua HTTP.
- **Cách tìm nguyên nhân và xử lý:**
  Tìm ra nguyên nhân nhờ kiểm tra mã nguồn `langfuse._client.span` và log exporter: SDK v4 sử dụng OpenTelemetry background worker để batch spans. Để xử lý triệt để, trong server dài hạn (Uvicorn), worker tự động flush định kỳ; đồng thời chúng tôi bổ sung các thuộc tính token và cost vào `metadata` của generation observation để đảm bảo dữ liệu luôn hiển thị trực tiếp trên giao diện span inspector.
- **Cách hiểu luồng Metrics → Logs → Traces:**
  - *Metrics* là radar cảnh báo đầu tiên: cho ta biết **hệ thống có chuyện gì và khi nào xảy ra** (ví dụ: P95 latency tăng vọt, Error rate vượt ngưỡng).
  - *Logs* là kính lúp: giúp ta **khoanh vùng request cụ thể bị ảnh hưởng** bằng cách lọc theo thời gian sự cố và lấy mã định danh duy nhất `correlation_id`.
  - *Traces* là bản chụp X-quang: bằng cách tra cứu `correlation_id` trên công cụ tracing (Langfuse), ta mở được Waterfall span tree của đúng request đó, so sánh từng span con (API -> Retrieval -> LLM Generation) để tìm chính xác **bước nào là nguyên nhân gốc rễ (Root Cause)**.
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:**
  - Quản lý prompt bằng version và nhãn (`baseline`, `candidate`, `production`) cho phép tách rời vòng đời prompt khỏi mã nguồn code, giúp thử nghiệm nhanh và rollback tức thì trong vài giây khi prompt mới gây ảo giác (hallucination) hoặc tăng chi phí đột biến.
  - Giám sát Token & Cost ngăn ngừa tình trạng cạn kiệt ngân sách API (cost spike) do prompt loop hoặc người dùng spam câu hỏi quá dài.
  - SLO & Error Budget đóng vai trò là "khế ước chất lượng": định lượng rõ mức độ sẵn sàng và độ trễ chấp nhận được, làm căn cứ để đưa ra quyết định kỹ thuật giữa tốc độ phát triển tính năng và tính ổn định của hệ thống.
- **Điều quan trọng nhất đã học:**
  Kỹ năng xây dựng hệ thống Observability toàn diện cho ứng dụng AI/LLM: không coi LLM là một "hộp đen" bí ẩn mà có thể định lượng, kiểm soát và điều tra từng mili-giây của luồng xử lý từ Client -> API Gateway -> Vector Database -> LLM Inference.
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:**
  Bài lab hiện mô phỏng với FakeLLM và Vector store local. Trong môi trường production thực tế, cần tích hợp thêm distributed tracing xuyên service (W3C traceparent context qua gRPC/HTTP), semantic caching với Redis, và các bộ lọc PII nâng cao dựa trên mô hình NLP (như Presidio).

## 9. Checklist trước khi nộp

- [x] Kết quả và evidence thuộc commit SHA cuối.
- [x] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [x] Incident evidence nối đúng metric → log → trace.
- [x] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [x] Repository chạy lại được theo README.
- [x] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [x] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
