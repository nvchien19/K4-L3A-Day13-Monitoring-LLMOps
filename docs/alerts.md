# Alert và Runbook

Mỗi alert đều dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.
Kênh thông báo chung: Slack `#day13-alerts`.

## Alert 1

- Tên: high-tail-latency-p95
- Severity: high
- Duration: 5m
- Kênh thông báo: Slack `#day13-alerts`
- SLI/SLO liên quan: `fast_successful_requests` — 99.5% request `response_sent` có `latency_ms <= 3000` trong 28 ngày.
- Điều kiện và thời gian duy trì: latency P95 > 3000ms liên tục 5 phút.
- Ảnh hưởng tới người dùng: một phần đáng kể người dùng chờ quá 3 giây mới nhận câu trả lời.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard panel Latency, xác định khoảng thời gian P95 vượt ngưỡng.
  2. Lọc `data/logs.jsonl` trong khoảng đó, lấy `correlation_id` của request chậm.
  3. Mở trace có cùng `correlation_id`, so sánh span retrieval và generation.
- Mitigation tạm thời: tắt incident đang bật (`inject_incident.py --disable`), giảm concurrency của workload, rollback prompt nếu vừa promote.
- Owner: nguyen-van-chien

## Alert 2

- Tên: elevated-error-rate
- Severity: critical
- Duration: 5m
- Kênh thông báo: Slack `#day13-alerts`
- SLI/SLO liên quan: guardrail `error_rate_pct_max: 2`.
- Điều kiện và thời gian duy trì: error rate (`request_failed` / `request_received`) > 2% liên tục 5 phút.
- Ảnh hưởng tới người dùng: request lỗi 500, người dùng không nhận được câu trả lời.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard panel Errors xem breakdown theo `error_type` và `tool_success`.
  2. Lọc log `request_failed`, lấy `correlation_id` và `error_type`.
  3. Mở trace tương ứng để xem span nào raise exception (ví dụ `Vector store timeout` ở retrieval).
- Mitigation tạm thời: disable incident `tool_fail`, kiểm tra dependency retrieval, rollback config/prompt vừa đổi.
- Owner: nguyen-van-chien

## Alert 3

- Tên: quality-proxy-drop
- Severity: warning
- Duration: 15m
- Kênh thông báo: Slack `#day13-alerts`
- SLI/SLO liên quan: guardrail `quality_score_avg_min: 0.75`.
- Điều kiện và thời gian duy trì: mean `quality_score` < 0.75 liên tục 15 phút.
- Ảnh hưởng tới người dùng: câu trả lời ngắn/cụt, ít dùng context truy xuất, trải nghiệm giảm dù chưa lỗi hẳn.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard panel Quality xem mean quality_score theo thời gian.
  2. Đối chiếu panel Tokens/Cost: output tokens bất thường hoặc cost spike gợi ý prompt/output đổi.
  3. So sánh trace của 2 prompt version/label (`baseline` vs `candidate`) nếu vừa đổi prompt.
- Mitigation tạm thời: rollback label `production` về prompt version ổn định trước đó.
- Owner: nguyen-van-chien
