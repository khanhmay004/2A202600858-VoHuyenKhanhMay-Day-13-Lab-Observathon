# Findings — Team solo858-team-name

> Bản đọc cho người; bản chấm điểm là `solution/findings.json`. Bằng chứng lấy từ telemetry của
> `solution/wrapper.py` trên bộ **public v6** (120 request, LLM thật), đối chiếu **broken**
> (`config.broken.json`, không mitigation) vs **fixed** (`solution/config.json`).

| fault_class | bằng chứng (số đo quan sát) | nguyên nhân gốc | cách sửa (config / wrapper / prompt) |
|---|---|---|---|
| error_spike | broken (no retry): 21/120 → `max_steps` do tool fail; fixed: 120/120 ok, 4 lỗi API thoáng qua được retry cứu | tool_error_rate=0.18 + không retry | config: tool_error_rate=0, retry x3; wrapper: retry |
| latency_spike | broken p95/p99 = **24494/27400 ms**; fixed = **12716/14561 ms** | timeout_ms=0, no cache | config: timeout=30000, cache; wrapper: cache |
| cost_blowup | broken **29364 tok/$0.357**; fixed **9916 tok/$0.122** | verbose_system, ctx=8, max_tok=2000, no cache | config: verbose off, ctx=4, max_tok=512, cache, verify off |
| quality_drift | drift inject + temp 1.6 (public chủ yếu single-turn nên ảnh hưởng nhỏ) | session_drift_rate=0.06, temperature=1.6 | config: drift=0, temperature=0.2 |
| infinite_loop | broken **21/120** `status=max_steps`; fixed **0/120** | loop_guard=false, max_steps=12 | config: loop_guard=true, max_steps=6 |
| tool_failure | broken refuse mọi MacBook (pub-010/025 "het hang"); fixed trả total thật | catalog_override ép out-of-stock; normalize_unicode=false | config: catalog_override={}, normalize_unicode=true |
| pii_leak | broken **25/120** answer rò email/sđt; fixed **0/120** | redact_pii=false + prompt lặp PII | config: redact_pii=true; prompt: no-PII; wrapper: redact (giữ số total) |
| fabrication | fixed refuse đúng AirPods hết hàng (pub-001/002, no total) | prompt 1 dòng không grounding | prompt: grounding, refuse no-total |
| arithmetic_error | temp 1.6 → total không ổn định; fixed temp 0.2 + công thức floor | thiếu công thức + temperature cao | prompt: floor formula + verify; config: temperature=0.2 |
| tool_overuse | broken **3.4** tool/req; fixed **2.39** | tool_budget=0 | config: tool_budget=4; prompt: mỗi tool 1 lần |
| prompt_injection | public không có (injected_note=0); phòng thủ sẵn cho private | prompt nghe theo order note | prompt: note=DATA, giá chỉ từ check_stock; wrapper: detect + route prompt cứng |
