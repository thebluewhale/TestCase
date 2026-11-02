"""결정 43 운영 코드 비교 — 지름비 판정을 렌즈 링 측정 켬/끔으로 기록."""
import json, os, sys, uuid, logging
from pathlib import Path
logging.basicConfig(level=logging.ERROR)
from review_product_consistency_v3.config import load_config
from review_product_consistency_v3.core.registry import get_profile
from review_product_consistency_v3.core.run_job import JobRequest, build_models, run_job
mode, spec_id, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
cfg = load_config(None); cfg.vlm.enabled = False; cfg.decision.identity.enabled = False
cfg.measure.lens_rings.enabled = mode != "off"
if mode == "gapc":
    cfg.measure.lens_rings.center_band = [0.8, 1.1]
models = build_models(cfg, get_profile("bar"), None)
res = json.load(open(out)) if out.exists() else {}
for arg in sys.argv[4:]:
    p, regions = (Path(arg.split("|")[0]), json.loads(arg.split("|")[1])) if "|" in arg else (Path(arg), None)
    key = p.name + ("|r" if regions else "")
    if key in res:
        continue
    try:
        result, _ = run_job(JobRequest(str(uuid.uuid4()), p, f"file://{p.resolve()}", spec_id, None, "image", regions=regions), cfg, models, out.parent / f"work_{mode}")
    except Exception as e:
        res[key] = {"error": repr(e)[:100]}; continue
    rows = []
    for k in result["keyframes"]:
        for o in k["objects"]:
            a = {x["id"]: x for x in o["attributes"]}
            d = a.get("camera_diameter_ratio") or {}
            rows.append({"spec": (o.get("product") or {}).get("spec_id"), "status": d.get("status"), "reason": d.get("not_verifiable_reason"), "measured": d.get("measured"), "dev": d.get("deviation"), "count": (a.get("camera_count") or {}).get("status")})
    res[key] = rows
    json.dump(res, open(out, "w"), indent=1, default=str)
