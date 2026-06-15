import sys, json, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
rows = [json.loads(l) for l in open("dump.jsonl", encoding="utf-8") if l.strip()]


def discounts(trace):
    return [s.get("observation") or {} for s in (trace or []) if s.get("tool") == "get_discount"]


multi = err = err_recovered = err_final = 0
print("== get_discount ERROR observations (shape + percent when error) ==")
for r in rows:
    ds = discounts(r.get("trace"))
    errs = [d for d in ds if d.get("error")]
    if errs:
        err += 1
        last = ds[-1]
        recovered = not last.get("error")
        if recovered: err_recovered += 1
        else: err_final += 1
        print("  %s | %d get_discount step(s): %s | LAST recovered=%s last=%s"
              % (r["qid"], len(ds), [(d.get("percent"), "ERR" if d.get("error") else "ok", "stk" if d.get("_stacked") else "") for d in ds], recovered, json.dumps(last, ensure_ascii=False)))
    if len(ds) > 1:
        multi += 1

print("\nrequests with a get_discount error: %d | recovered by last step: %d | error still last: %d"
      % (err, err_recovered, err_final))
print("requests with >1 get_discount call: %d" % multi)

# does percent stay consistent for a coupon WITHIN a single request's multiple calls?
print("\n== per-request get_discount percent sequences (only multi-call) ==")
for r in rows:
    ds = discounts(r.get("trace"))
    if len(ds) > 1:
        print("  %s %s -> %s" % (r["qid"], (ds[0].get("code")), [(d.get("percent"), bool(d.get("error"))) for d in ds]))

# how many stacked vs not, and is _stacked only on the higher tier?
print("\n== stacked flag vs percent ==")
st = collections.Counter()
for r in rows:
    for d in discounts(r.get("trace")):
        if not d.get("error"):
            st[(d.get("code"), d.get("percent"), bool(d.get("_stacked")))] += 1
for k, c in sorted(st.items()):
    print("  ", k, c)
