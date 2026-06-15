import sys, json, re, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
rows = [json.loads(l) for l in open("dump.jsonl", encoding="utf-8") if l.strip()]
print("rows:", len(rows))

# 1) all distinct tool names + how often
tools = collections.Counter()
shapes = collections.defaultdict(set)
for r in rows:
    for st in r.get("trace") or []:
        t = st.get("tool")
        tools[t] += 1
        o = st.get("observation") or {}
        shapes[t].add(tuple(sorted(o.keys())))
print("\n== tool call counts ==")
for t, c in tools.most_common():
    print(" ", t, c, "| obs keys:", [list(k) for k in shapes[t]])

# 2) every NON-standard tool (not the 3 we handle) -- full sample observations
known = {"check_stock", "get_discount", "calc_shipping"}
extra = [t for t in tools if t not in known]
print("\n== EXTRA tools beyond our 3 ==", extra)
for r in rows:
    for st in r.get("trace") or []:
        if st.get("tool") in extra:
            print(" ", r["qid"], st.get("tool"), "ACTION:", st.get("action"), "OBS:", json.dumps(st.get("observation"), ensure_ascii=False))
            break

# 3) get_discount: coupon name in question vs percent returned
print("\n== get_discount: coupon -> percent (does it vary? loyalty stacking?) ==")
seen = collections.defaultdict(collections.Counter)
for r in rows:
    for st in r.get("trace") or []:
        if st.get("tool") == "get_discount":
            o = st.get("observation") or {}
            code = o.get("code")
            seen[code][(o.get("valid"), o.get("percent"))] += 1
for code, cnt in seen.items():
    print("  coupon", code, "->", dict(cnt))

# 4) sample full traces (2 with discount, look for loyalty step)
print("\n== 2 full sample traces ==")
shown = 0
for r in rows:
    if any(s.get("tool") == "get_discount" for s in r.get("trace") or []):
        print("---", r["qid"], "::", r["q"][:80], "=> answer:", (r.get("answer") or "")[:40])
        for st in r.get("trace") or []:
            print("   ", st.get("tool"), json.dumps(st.get("observation"), ensure_ascii=False))
        shown += 1
        if shown >= 3:
            break
