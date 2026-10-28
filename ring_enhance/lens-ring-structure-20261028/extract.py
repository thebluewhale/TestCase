"""공식 후면에서 렌즈 링 구조 추출 (SDP 결정 43 ①) — 운영 링 탐색기(lens_rings.find_rings) 그대로.

렌즈마다 같은 중심의 링을 모두 찾고, 섬 테두리(렌즈와 같은 중심의 스펙 섬 윤곽까지 여유 < 스펙 렌즈
여유의 50%)를 뺀 뒤:
- 바깥 링(outer): 스펙 지름과 3% 안인 링 가운데 스펙 지름에 가장 가까운 것 — 스펙 지름이 가리키는
  링. 둘레 ≥ 0.7인 링이 그 안에 둘 이상이면 어느 링인지 정할 수 없어 low (S24 계열: 3% 간격 두 링)
- 안쪽 링(inner): 바깥 링보다 5% 넘게 작고 둘레 ≥ 0.7인 링 가운데 둘레가 가장 잘 보이는 것(같으면
  큰 쪽) — 사진에서 바깥 링이 약할 때 대신 잡히는 링
신뢰도 high: 바깥·안쪽 둘레 모두 ≥ 0.7. 같은 크기 렌즈끼리 간격이 2% 넘게 다르면 low.

출력: rings.json(제품별 렌즈 링 구조·신뢰도), images/<제품>.png(공식 후면 카메라 부분에 링 표시).

    .venv/bin/python benchmarks/reports/lens-ring-structure-20261028/extract.py
"""

import json
import math
from pathlib import Path

import cv2
import numpy as np

from review_product_consistency_v3.config import load_config
from review_product_consistency_v3.core import geometry as geo
from review_product_consistency_v3.formfactors.bar import lens_rings

HERE = Path(__file__).parent
LIB = Path("product_library")
cfg = load_config(None).measure
lc, edge_ratio = cfg.lens_rings, cfg.island_outline.edge_clearance_ratio


def clearance(poly, c, d):
    pts = (np.asarray(poly, np.float64) * 1e4).astype(np.float32)
    return cv2.pointPolygonTest(pts, (float(c[0] * 1e4), float(c[1] * 1e4)), True) / 1e4 - d / 2


def load_back(pdir):
    im = cv2.imread(str(pdir / "official" / "Back.png"), cv2.IMREAD_UNCHANGED)
    if im.shape[2] == 4:
        a = im[..., 3:].astype(np.float64) / 255
        alpha = (im[..., 3] > 127).astype(np.uint8)
        im = (im[..., :3] * a + 255 * (1 - a)).astype(np.uint8)
    else:
        alpha = np.ones(im.shape[:2], np.uint8)
    rect = geo.fit_rounded_rect(geo.largest_contour(alpha * 255))
    return im, alpha, rect


def extract(sid):
    pdir = LIB / sid
    spec = json.loads((pdir / "product_spec.json").read_text(encoding="utf-8"))
    cams = spec["back"]["cameras"]
    isl = spec["back"]["camera_island"]
    outline = np.asarray(isl.get("outline") or [], np.float64)
    im, alpha, rect = load_back(pdir)
    W = rect.w
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    def to_px(x, y):
        return rect.cx + x * W, rect.cy - y * W

    out = []
    for cam in cams:
        c = to_px(*cam["center"])
        others = [(*to_px(*o["center"]), o["diameter_ratio"] / 2 * W) for o in cams if o is not cam]
        expected = (
            clearance(outline, cam["center"], cam["diameter_ratio"])
            if isl["present"] and len(outline)
            else None
        )

        def rows_of(rings, expected=expected, cam=cam):
            rows = []
            for g in rings:
                d = 2 * g.r / W
                q = clearance(outline, cam["center"], d) / expected if expected else math.inf
                rows.append(
                    {
                        "d": round(d, 4),
                        "cover": g.cover,
                        "q": None if math.isinf(q) else round(q, 2),
                        "island": q < edge_ratio,
                        "px": [round(g.cx, 1), round(g.cy, 1), round(g.r, 1)],
                    }
                )
            return rows

        r_exp = cam["diameter_ratio"] / 2 * W
        rows_blocked = rows_of(lens_rings.find_rings(gray, c, r_exp, lc, alpha, others))
        # 이웃이 여럿인 가운데 렌즈는 이웃 방향 구간을 빼면 보이는 둘레가 절반 아래다 — 공식 후면은
        # 깨끗해 이웃 테두리와 헷갈리지 않으므로 구간을 빼지 않고도 찾는다
        rows_all = rows_of(lens_rings.find_rings(gray, c, r_exp, lc, alpha, None))
        rows, blocked = (rows_blocked, True) if rows_blocked else (rows_all, False)
        lens = [r for r in rows if not r["island"]]
        near = [r for r in lens if abs(r["d"] / cam["diameter_ratio"] - 1) <= 0.03]
        outer = min(near, key=lambda r: abs(r["d"] / cam["diameter_ratio"] - 1)) if near else None
        inner = None
        if outer:
            cand = [r for r in lens if r["d"] < outer["d"] * 0.95 and r["cover"] >= lc.min_cover]
            inner = max(cand, key=lambda r: (r["cover"], r["d"])) if cand else None
        strong_near = [r for r in near if r["cover"] >= lc.min_cover]
        out.append(
            {
                "id": cam["id"],
                "spec_diameter": cam["diameter_ratio"],
                "outer": outer,
                "inner": inner,
                "ratio": round(outer["d"] / inner["d"], 4) if outer and inner else None,
                "neighbor_sectors_blocked": blocked,
                "strong_near_spec": [r["d"] for r in strong_near],
                "rings": rows,
                "rings_unblocked": rows_all,
            }
        )
    # 신뢰도 — 바깥·안쪽 둘레, 같은 크기 렌즈끼리 간격 일관성 (strict 결과끼리만 비교)
    strict_ratio = {cam["id"]: cam["ratio"] for cam in out}
    island_raised = all(c.get("ring_style") == "island_raised" for c in cams)
    for cam in out:
        o, i = cam["outer"], cam["inner"]
        why = []
        if o is None:
            why.append("스펙 지름과 3% 안인 링 없음")
        elif o["cover"] < lc.min_cover:
            why.append(f"바깥 링 둘레 {o['cover']:.2f} < {lc.min_cover}")
        if o is not None and i is None:
            why.append("안쪽 링 없음")
        if len(cam["strong_near_spec"]) > 1:
            why.append(f"스펙 지름 3% 안에 뚜렷한 링이 둘 이상 {cam['strong_near_spec']}")
        same = [
            strict_ratio[x["id"]]
            for x in out
            if strict_ratio[x["id"]] and abs(x["spec_diameter"] / cam["spec_diameter"] - 1) < 0.05
        ]
        if cam["ratio"] and len(same) > 1 and (max(same) / min(same) - 1) > 0.02:
            why.append(f"같은 크기 렌즈 간격 불일치 {min(same):.3f}~{max(same):.3f}")
        cam["confidence"] = "low" if why else "high"
        cam["low_reason"] = why
        # 하이라이트 경로는 검은 섬 위 렌즈(island_raised — A37·A57)에만. 렌즈마다 안쪽 링이 실제로
        # 다를 수 있어(A37 cam1 0.1609 · cam2·3 0.1662, 두 실행 모두 같은 값) 간격 불일치는 막지 않는다
        weak = ("바깥 링 둘레", "스펙 지름과 3% 안인 링 없음", "안쪽 링 없음")
        only_weak_outer = (
            why
            and island_raised
            and any(w.startswith(weak) for w in why)
            and all(w.startswith((*weak, "같은 크기 렌즈 간격 불일치")) for w in why)
        )
        if only_weak_outer:
            rim = _rim_path(cam)
            if rim:
                cam.update(rim)
                cam["confidence"] = "medium"
    return {"spec_id": sid, "body_px_per_w": round(W, 1), "cameras": out}, im, rect


def _rim_path(cam: dict) -> dict | None:
    """바깥 테두리가 하이라이트로만 보이는 렌즈(검은 섬 위 검은 렌즈 — A37·A57) — 스펙 지름 ±4% 안에
    둘레 ≥ 0.3인 링(하이라이트)이 있으면 outer = 스펙 지름, inner = 스펙보다 4~12% 작고 둘레 ≥ 0.7인
    링 가운데 가장 잘 보이는 것. 하이라이트 띠의 두 가장자리가 렌즈마다 번갈아 잡혀 그 값은 흔들리지만
    스펙 지름은 하이라이트 위치와 맞는다(확대 그림 확인). 이웃 구간을 뺀 결과로 먼저, 안 되면 전체로."""
    d0 = cam["spec_diameter"]
    for rows, blocked in (
        (cam["rings"], cam["neighbor_sectors_blocked"]),
        (cam["rings_unblocked"], False),
    ):
        lens = [r for r in rows if not r["island"]]
        rims = [r for r in lens if abs(r["d"] / d0 - 1) <= 0.04 and r["cover"] >= 0.3]
        inner = [r for r in lens if d0 * 0.88 <= r["d"] <= d0 * 0.96 and r["cover"] >= lc.min_cover]
        if rims and inner:
            rim = max(rims, key=lambda r: r["cover"])
            i = max(inner, key=lambda r: (r["cover"], r["d"]))
            return {
                "outer": {"d": d0, "cover": rim["cover"], "px": rim["px"], "rim_ring": rim["d"]},
                "inner": i,
                "ratio": round(d0 / i["d"], 4),
                "neighbor_sectors_blocked": blocked,
                "medium_reason": [
                    f"바깥 테두리가 하이라이트로만 보임 (링 {rim['d']}, 둘레 {rim['cover']:.2f}) — "
                    "outer는 스펙 지름(하이라이트 위치와 일치)"
                ],
            }
    return None


def draw(sid, res, im, rect):
    W = rect.w
    pts = [c["outer"]["px"] for c in res["cameras"] if c["outer"]]
    spec = json.loads((LIB / sid / "product_spec.json").read_text(encoding="utf-8"))
    xs = [rect.cx + c["center"][0] * W for c in spec["back"]["cameras"]]
    ys = [rect.cy - c["center"][1] * W for c in spec["back"]["cameras"]]
    pad = 0.22 * W
    x0, x1 = int(max(0, min(xs) - pad)), int(min(im.shape[1], max(xs) + pad))
    y0, y1 = int(max(0, min(ys) - pad)), int(min(im.shape[0], max(ys) + pad))
    img = im.copy()
    for cam, sc in zip(res["cameras"], spec["back"]["cameras"], strict=True):
        # 실제로 쓴 실행(이웃 구간 뺌/안 뺌)의 링을 그린다
        for r in cam["rings"] if cam["neighbor_sectors_blocked"] else cam["rings_unblocked"]:
            col = (170, 170, 170) if r["island"] else (200, 200, 200)
            cv2.circle(
                img, (int(r["px"][0]), int(r["px"][1])), int(r["px"][2]), col, 1, cv2.LINE_AA
            )
        for key, col in (("outer", (40, 170, 40)), ("inner", (200, 90, 0))):
            r = cam[key]
            if r:
                c = (int(round(r["px"][0])), int(round(r["px"][1])))
                # medium(하이라이트 경로)의 outer는 스펙 지름 — 그 크기로 그린다
                rad = r["d"] / 2 * W if "rim_ring" in r else r["px"][2]
                cv2.circle(img, c, int(round(rad)), col, 3, cv2.LINE_AA)
    crop = img[y0:y1, x0:x1]
    s = 900 / max(crop.shape[:2])
    crop = cv2.resize(crop, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    # 오른쪽에 범례·값
    panel = np.full((crop.shape[0], 560, 3), 255, np.uint8)
    lines = [
        f"{sid}",
        "green = outer (spec ring)",
        "blue = inner",
        "gray = other / island rings",
        "",
    ]
    for cam in res["cameras"]:
        o, i = cam["outer"], cam["inner"]
        lines.append(f"{cam['id']}: spec {cam['spec_diameter']:.4f}  {cam['confidence'].upper()}")
        rim = f" = spec, rim {o['rim_ring']:.4f}" if o and "rim_ring" in o else ""
        lines.append(f"   outer {o['d']:.4f} ({o['cover']:.2f}){rim}" if o else "   outer -")
        lines.append(
            f"   inner {i['d']:.4f} ({i['cover']:.2f})  ratio {cam['ratio']}" if i else "   inner -"
        )
    for k, t in enumerate(lines):
        cv2.putText(
            panel,
            t,
            (12, 32 + 30 * k),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            (20, 20, 20),
            1,
            cv2.LINE_AA,
        )
    out = np.hstack([crop, panel]) if panel.shape[0] == crop.shape[0] else crop
    cv2.imwrite(str(HERE / "images" / f"{sid}.png"), out)


if __name__ == "__main__":
    (HERE / "images").mkdir(exist_ok=True)
    allres = {}
    for pdir in sorted(LIB.iterdir()):
        if not (pdir / "official" / "Back.png").exists():
            continue
        res, im, rect = extract(pdir.name)
        draw(pdir.name, res, im, rect)
        allres[pdir.name] = res
        print(
            pdir.name,
            [
                (
                    c["id"],
                    c["outer"] and c["outer"]["d"],
                    c["inner"] and c["inner"]["d"],
                    c["ratio"],
                    c["confidence"],
                )
                for c in res["cameras"]
            ],
        )
    (HERE / "rings.json").write_text(json.dumps(allres, ensure_ascii=False, indent=1))
