"""렌즈 링 측정 켬/끔 — 지름비 판정 전이와 라벨별 요약."""
import collections, json, sys
D = sys.argv[1]
MODE_A = sys.argv[2] if len(sys.argv) > 2 else "off"
MODE_B = sys.argv[3] if len(sys.argv) > 3 else "on"
B = "/home/jh_marc.kim/aic-creative-assurance/backend/review_product_consistency_v3/benchmarks/real/"
LAB = {"a27": "galaxy-a27-5g", "s26": "galaxy-s26", "s25": "galaxy-s25"}
ab = {"match": "일치", "mismatch_review": "검토", "mismatch_reject": "거부", "not_verifiable": "불가", "uncertain": "불확실", "not_applicable": "해당없음", None: "-"}
tot = collections.Counter()
for key in ("a57", "s26", "a27", "s25", "s25u"):
    on = json.load(open(f"{D}/cmp_{key}_{MODE_B}.json")); off = json.load(open(f"{D}/cmp_{key}_{MODE_A}.json"))
    lab = json.load(open(B + LAB[key] + "/labels.json")) if key in LAB else {}
    trans = collections.Counter(); lines = []
    for name in sorted(on):
        a, b = off.get(name), on.get(name)
        if not isinstance(a, list) or not isinstance(b, list):
            continue
        for ra, rb in zip(a, b):
            if key == "s25u":
                good = not name.startswith("S25U_defect")
            elif key == "a57":
                good = True
            else:
                good = lab.get(name.split("|")[0]) == "pass"
            t = (ab[ra["status"]], ab[rb["status"]])
            trans[(good, t)] += 1
            if t[0] != t[1]:
                lines.append(f"   {'정상' if good else '음성'} {name[:42]:42s} {rb.get('spec') or '':18s} {t[0]}({ra.get('reason') or ra.get('dev')}) → {t[1]}({rb.get('reason') or rb.get('dev')}) {rb.get('measured')}")
    print(f"== {key}")
    for (good, t), n in sorted(trans.items(), key=lambda x: (not x[0][0], x[0][1])):
        print(f"   {'정상' if good else '음성'} {t[0]}→{t[1]}: {n}")
        tot[(good, t)] += n
    print("\n".join(lines))
print("== 합계")
for (good, t), n in sorted(tot.items(), key=lambda x: (not x[0][0], x[0][1])):
    print(f"   {'정상' if good else '음성'} {t[0]}→{t[1]}: {n}")
