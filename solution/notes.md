# Sổ chẩn đoán (đã điền) — solo858

> Quan sát từ telemetry của `solution/wrapper.py` (`logs/` + `traces/`). Đối chiếu run **broken**
> (`config.broken.json`, wrapper observe-only, không mitigation) với run **fixed**
> (`solution/config.json`) trên bộ **public v6** (120 request, LLM thật). Bản JSON chấm điểm:
> `solution/findings.json`.

| Triệu chứng (từ telemetry) | Request | Nguyên nhân | Sửa config | Sửa prompt/wrapper |
|---|---|---|---|---|
| `status=max_steps` 21/120 (broken) → **0** (fixed) | đơn nhiều bước | loop_guard=false, max_steps=12 | loop_guard=true, max_steps=6 | — |
| latency p95/p99 **24.5s/27.4s → 10.2s/14.5s** | đuôi chậm | timeout_ms=0, no cache/retry | timeout=30s, cache on, retry x3 | wrapper: cache + retry |
| token/cost **29.4k/$0.357 → 9.9k/$0.122** | mọi đơn | verbose_system, ctx=8, max_tok=2000, no cache | verbose off, ctx=4, max_tok=512, cache, **verify=false** | — |
| answer rò email/sđt **25/120 → 0** | đơn có PII | redact_pii=false | redact_pii=true | prompt "không lặp PII" + wrapper redact (giữ số `Tong cong`) |
| tool/req **3.4 → 2.39** | mọi đơn | tool_budget=0 | tool_budget=4 | prompt "mỗi tool 1 lần" |
| MacBook luôn "hết hàng" (broken) | đơn macbook (pub-010/025) | catalog_override ép out-of-stock | catalog_override={} | — |
| thành phố có dấu ("Hà Nội") tra fail | đơn có dấu | normalize_unicode=false | normalize_unicode=true | — |
| bịa total cho hàng hết | airpods/macbook hết | prompt 1 dòng, không grounding | temperature=0.2 | prompt: grounding + refuse (no total) |
| total sai / đảo discount | đơn có mã giảm | temperature=1.6, không công thức | temperature=0.2 | prompt: công thức floor + verify |
| (PRIVATE) nghe "giá hệ thống" trong GHI CHÚ | đơn có note | prompt nghe theo note | — | prompt: note=DATA; wrapper detect + route prompt cứng |

**Kết quả fixed (public v6):** 120/120 `ok` · AirPods hết hàng → từ chối đúng 10/10 (no total) ·
0 rò PII · format `Tong cong: <integer> VND`.

**Quyết định tune đáng chú ý:** `verify=true` tốn ~2× token mà correctness không cải thiện → ship
**`verify=false`** (giảm cost ~43%). `self_consistency` để 1, chỉ lên 3 nếu thấy số học dao động.
