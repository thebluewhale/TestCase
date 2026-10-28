"""rings.json → 스펙 수정본(draft) — 신뢰도 high 렌즈에만 back.cameras[].rings (SDP 결정 43 ①).

스펙은 minor 버전을 올리고 status=draft로 둔다. 사람이 `onboard validate --by <이름>`으로 승인해야
검수에 쓰인다(실행은 validated 스펙만). galaxy-s24-ultra는 결정 42(Tier B min_sharpness 0.3)도 함께.

    .venv/bin/python benchmarks/reports/lens-ring-structure-20261028/make_drafts.py
"""

import json
from pathlib import Path

from review_product_consistency_v3.schemas.validate import validate

HERE = Path(__file__).parent
LIB = Path("product_library")
NOTE = (
    "back.cameras[].rings: 공식 후면 렌즈 링 구조(SDP 결정 43 ①, 2026-10-28, "
    "benchmarks/reports/lens-ring-structure-20261028) — 신뢰도 high 렌즈만"
)
NOTE_42 = "Tier B min_sharpness 0.6→0.3 (SDP 결정 42)"

rings = json.loads((HERE / "rings.json").read_text(encoding="utf-8"))
for sid, res in rings.items():
    high = {c["id"]: c for c in res["cameras"] if c["confidence"] == "high"}
    p = LIB / sid / "product_spec.json"
    spec = json.loads(p.read_text(encoding="utf-8"))
    sharp = sid == "galaxy-s24-ultra" and any(
        c["verifiability"]["min_sharpness"] == 0.6
        for c in spec["checks"].values()
        if c.get("tier") == "B"
    )
    if not high and not sharp:
        print(sid, "변경 없음 (신뢰도 high 렌즈 없음)")
        continue
    notes = []
    for cam in spec["back"]["cameras"]:
        c = high.get(cam["id"])
        if c:
            cam["rings"] = {"outer": c["outer"]["d"], "inner": c["inner"]["d"]}
    if high:
        notes.append(NOTE)
    if sharp:
        for c in spec["checks"].values():
            if c.get("tier") == "B" and c["verifiability"]["min_sharpness"] == 0.6:
                c["verifiability"]["min_sharpness"] = 0.3
        notes.append(NOTE_42)
    major, minor, _ = (int(x) for x in spec["spec_version"].split("."))
    spec["spec_version"] = f"{major}.{minor + 1}.0"
    spec["status"] = "draft"
    spec["provenance"]["validated_by"] = None
    spec["provenance"]["validated_at"] = None
    spec["provenance"]["notes"] = (spec["provenance"]["notes"] or "") + "; " + "; ".join(notes)
    validate("product_spec", spec)
    p.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(sid, spec["spec_version"], "draft —", sorted(high), "선명도 0.3" if sharp else "")
