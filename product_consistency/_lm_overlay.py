"""제품별 옆면·하단 랜드마크 확인 이미지 (사용자 육안 확인용, 저장소 코드 변경 없음).

운영 추출 함수(landmarks._extract_face)를 제품별 재질 역할 대응으로 부른다.
- S 계열: 재질 이름 정규화(대소문자·밑줄 무시)로 S26U 설정과 맞춘다.
- A 시리즈: 재질 역할을 그림으로 정한 대응(제안) + 재질로 안 나뉘는 구멍·홈은 정사영 깊이로.
GLB 정사영 렌더(온보딩 산출물) 위에 뽑은 특징을 반투명하게 칠하고 윤곽·이름을 적는다.
사용: lm_overlay.py <out 폴더> [spec_id ...]"""
import json
import re
import sys
from dataclasses import replace
from pathlib import Path

import cv2
import numpy as np

ROOT = Path("/home/jh_marc.kim/aic-creative-assurance/backend/review_product_consistency_v3")
sys.path.insert(0, str(ROOT))
from review_product_consistency_v3.config import load_config  # noqa: E402
from review_product_consistency_v3.core.ortho import load_ortho  # noqa: E402
from review_product_consistency_v3.formfactors.bar import landmarks as L  # noqa: E402

FACES = ("bottom", "top", "right", "left")
_MP = Path.home() / "TestCase/product_consistency/manual_sim/manual_sim.json"
MANUAL = json.loads(_MP.read_text())["items"] if _MP.exists() else {}
ROLES = ("hole", "usb", "seam", "button", "anchor")
# A 시리즈 — 재질 역할(그림으로 확인한 제안). depth: 정사영 깊이로 구멍·홈을 hole에 더한다
A_MAP = {
    "galaxy-a27-5g": {"hole": ["black_"], "usb": ["usb", "c_noise"], "depth": True},
    "galaxy-a37": {"seam": ["A37_260316:color:225:244:255.003"],
                   "button": ["A37_260316:color:225:244:255.002", "A37_260316:color:225:244:255"],
                   "depth": True},
    "galaxy-a57": {"seam": ["A57_260130:color:153:153:153.005"],
                   "button": ["A57_260130:color:153:153:153.004", "A57_260130:color:153:153:153.003"],
                   "anchor": ["A57_260130:color:102:102:102", "A57_260130:color:102:102:102.001",
                              "A57_260130:color:102:102:102.003", "A57_260130:color:102:102:102.004",
                              "A57_260130:color:102:102:102.005", "A57_260130:color:102:102:102.006"],
                   "depth": True},
}
COLORS = {  # BGR
    "usb_c": (0, 140, 255), "speaker": (255, 80, 0), "microphone": (255, 0, 200),
    "sim_tray": (0, 200, 0), "s_pen_slot": (0, 220, 220), "power": (0, 0, 255),
    "volume_rocker": (200, 0, 255), "button": (0, 0, 160), "antenna": (150, 150, 150),
}


def norm(n: str) -> str:
    return re.sub(r"[^a-z0-9]", "", n.lower())


def roles_for(spec_id: str, names: list[str], lc) -> dict[str, list[str]]:
    if spec_id in A_MAP:
        m = A_MAP[spec_id]
        return {r: [n for n in m.get(r, []) if n in names] for r in ROLES}
    want = {"hole": lc.hole_materials, "usb": lc.usb_materials, "seam": lc.seam_materials,
            "button": [], "anchor": lc.anchor_materials}
    return {r: [n for n in names if norm(n) in {norm(w) for w in ws}] for r, ws in want.items()}


def depth_recess(of, fid) -> np.ndarray:
    """면 평평한 부분보다 움푹한 곳(구멍·홈) — 면 끝 둥근 띠는 뺀다."""
    d = of.depth.astype(np.float32)
    a = (of.alpha > 0.5) & np.isfinite(d)
    d = np.where(np.isfinite(d), d, 0.0)
    med = float(np.median(d[a]))
    flat = a & (np.abs(d - med) < 0.0015)
    # 평평한 영역의 행·열 범위 안쪽만 (둥근 모서리·두께 방향 끝 제외)
    rows = np.nonzero(flat.mean(1) > 0.3)[0]
    cols = np.nonzero(flat.mean(0) > 0.3)[0]
    box = np.zeros_like(a)
    if len(rows) and len(cols):
        box[rows.min() + 2: rows.max() - 1, cols.min() + 2: cols.max() - 1] = True
    # 렌더의 가는 어두운 윤곽선(재질·깊이로 안 나뉜 테두리) — 블랙햇
    g = cv2.cvtColor(of.rgb, cv2.COLOR_BGR2GRAY)
    bh = cv2.morphologyEx(g, cv2.MORPH_BLACKHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    line = bh > 25
    rec = (box & a & ((d > med + 0.0008) | line)).astype(np.uint8)
    # 평평한 영역 가장자리(면 끝 경사·둥근 모서리)에 닿는 조각은 뺀다
    n, lab, st, _ = cv2.connectedComponentsWithStats(rec, 8)
    out = np.zeros_like(a)
    if len(rows) and len(cols):
        r0, r1, c0, c1 = rows.min() + 2, rows.max() - 1, cols.min() + 2, cols.max() - 1
        for i in range(1, n):
            x, y, w, h, area = st[i]
            if x <= c0 + 3 or y <= r0 + 3 or x + w >= c1 - 3 or y + h >= r1 - 3 or area < 15:
                continue
            out |= lab == i
    return out


def extract_product(spec_id: str, cfg):
    pdir = ROOT / "product_library" / spec_id
    spec = json.loads((pdir / "product_spec.json").read_text())
    ortho = load_ortho(pdir / "ortho", FACES)
    lc = cfg.landmarks
    out = {}
    for fid in FACES:
        of = ortho.get(fid)
        if of is None:
            continue
        names = list(of.material_names)
        r = roles_for(spec_id, names, lc)
        matid = of.matid.copy()
        extra = []
        if A_MAP.get(spec_id, {}).get("depth", True):  # 모든 제품 — 재질로 안 나뉜 테두리·윤곽 홈 보충
            # 깊이 구멍·홈을 새 재질 "_DEPTH_HOLE"로 (본체 재질 자리에만 — 다른 역할 재질은 그대로)
            role_ids = [names.index(n) for k in ("hole", "usb", "seam", "button") for n in r[k]]
            rec = depth_recess(of, fid) & ~np.isin(matid, role_ids)
            names = names + ["_DEPTH_HOLE"]
            matid[rec] = len(names) - 1
            extra = ["_DEPTH_HOLE"]
        # 버튼 역할 재질은 hole로 넘기되 아래에서 옆면 버튼으로 바꾼다
        btn = r["button"] if fid in ("left", "right") else []  # 버튼 재질은 옆면에서만
        lcp = lc.model_copy(update={
            "hole_materials": r["hole"] + extra + btn, "usb_materials": r["usb"],
            "seam_materials": r["seam"], "anchor_materials": r["anchor"]})
        of2 = replace(of, matid=matid, material_names=names)
        feats, anchors = L._extract_face(of2, fid, spec, lcp)
        if btn and fid in ("left", "right"):
            # 버튼 재질 영역은 꽉 찬 영역이라 마이크·스피커로 분류된다 — 옆면에서는 버튼으로, 이름은 스펙 span
            for f in feats:
                if f["type"] in ("speaker", "microphone"):
                    f["type"] = "button"
            side = fid
            for b in (f for f in feats if f["type"] == "button"):
                lo = b["body_center"][1] - b["size"][1] / 2
                hi = b["body_center"][1] + b["size"][1] / 2
                best = max(((min(hi, s["span"][1]) - max(lo, s["span"][0]), s["type"])
                            for s in spec["sides"]["buttons"] if s["side"] == side), default=(0, None))
                if best[0] > 0:
                    b["type"] = best[1]
        if fid in ("bottom", "top"):
            # 테두리만 있는 영역 안에 핀 구멍이 있으면 SIM 트레이 (S펜 슬롯에는 핀 구멍이 없다)
            for f in feats:
                if f["type"] in ("s_pen_slot", "microphone", "speaker") and f.get("children")                         and max(f["size"]) > 0.08:
                    f["type"] = "sim_tray"
        if extra and fid in ("bottom", "top") and not r["usb"]:
            # USB 재질이 없는 제품(깊이 구멍) — 스펙 USB-C 위치에 가장 가까운 길쭉한 구멍을 usb_c로
            for port in (p for p in spec["sides"].get("ports", []) if p.get("type") == "usb_c"
                         and p.get("side") == fid):
                cand = [f for f in feats if f["type"] == "speaker"]
                if cand:
                    best = min(cand, key=lambda f: abs(f["center"][0] - port["position"]))
                    if abs(best["center"][0] - port["position"]) < 0.05:
                        best["type"] = "usb_c"
        man = MANUAL.get(spec_id)
        if man and man["face"] == fid:
            # 사람이 준 SIM 트레이 상자 — 상자 안 자동 조각(테두리 조각·핀 구멍을 마이크로 본 것)을 SIM 하나로
            Hh, Ww = of.matid.shape
            ppw = of.px_per_w
            x0, y0, x1, y1 = man["box_px"]
            fx = lambda c: (c - Ww / 2) / ppw
            fy = lambda rr: (Hh / 2 - rr) / ppw
            bx0, bx1, by0, by1 = fx(x0), fx(x1), fy(y1), fy(y0)
            inside = [f for f in feats if bx0 <= f["center"][0] <= bx1 and by0 <= f["center"][1] <= by1]
            feats = [f for f in feats if f not in inside]
            pins = [f for f in inside if max(f["size"]) < 0.02]
            rad = min(bx1 - bx0, by1 - by0) / 2
            t = np.linspace(0, np.pi / 2, 8)
            cx0, cx1, cy0, cy1 = bx0 + rad, bx1 - rad, by0 + rad, by1 - rad
            outline = ([[cx1 + rad * np.cos(a), cy1 + rad * np.sin(a)] for a in t]
                       + [[cx0 - rad * np.sin(a), cy1 + rad * np.cos(a)] for a in t]
                       + [[cx0 - rad * np.cos(a), cy0 - rad * np.sin(a)] for a in t]
                       + [[cx1 + rad * np.sin(a), cy0 - rad * np.cos(a)] for a in t])
            feats.append({"face": fid, "type": "sim_tray", "manual": True,
                          "center": [round((bx0 + bx1) / 2, 5), round((by0 + by1) / 2, 5)],
                          "size": [round(bx1 - bx0, 5), round(by1 - by0, 5)],
                          "outline": [[round(float(x), 5), round(float(y), 5)] for x, y in outline],
                          "children": [{"type": "pin_hole", "center": p["center"]} for p in pins]})
            feats.sort(key=lambda f: tuple(f["center"]))
        out[fid] = (of.rgb, of.px_per_w, feats, anchors, r)
    return spec, out


def draw(rgb, ppw, feats, anchors, fid):
    img = rgb.copy()
    H, W = img.shape[:2]
    over = img.copy()

    def px(x, y):
        return [x * ppw + W / 2 - 0.5, H / 2 - y * ppw - 0.5]

    for a in anchors:
        (cx, cy), (w, h) = a["center"], a["size"]
        p0, p1 = px(cx - w / 2, cy + h / 2), px(cx + w / 2, cy - h / 2)
        cv2.rectangle(over, tuple(map(int, p0)), tuple(map(int, p1)), COLORS["antenna"], -1)
    for f in feats:
        pts = np.array([px(x, y) for x, y in f["outline"]], np.int32)
        cv2.fillPoly(over, [pts], COLORS.get(f["type"], (0, 0, 255)))
    img = cv2.addWeighted(over, 0.45, img, 0.55, 0)
    for f in feats:
        pts = np.array([px(x, y) for x, y in f["outline"]], np.int32)
        cv2.polylines(img, [pts], True, COLORS.get(f["type"], (0, 0, 255)), 2)
        for ch in f.get("children", []):
            cv2.circle(img, tuple(map(int, px(*ch["center"]))), 6, (0, 255, 255), 2)
    if fid in ("left", "right"):
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return img


def render_face(rgb, ppw, feats, anchors, fid, title):
    img = draw(rgb, ppw, feats, anchors, fid)
    Hh, Ww = rgb.shape[:2]
    # 이름표 띠: 특징 중심의 길이 방향 위치에 종류를 적는다
    band = np.full((60, img.shape[1], 3), 255, np.uint8)
    for f in sorted(feats, key=lambda f: f["center"]):
        cx, cy = f["center"]
        if fid in ("left", "right"):
            # 반시계 회전: 원래 (u, v) → (v, W-1-u). 길이 방향 = 원래 v(행) → 새 x
            x = int(Hh / 2 - cy * ppw)
        else:
            x = int(cx * ppw + Ww / 2)
        col = COLORS.get(f["type"], (0, 0, 255))
        cv2.line(band, (x, 40), (x, 60), col, 3)
        cv2.putText(band, f["type"], (max(0, x - 60), 30), 0, 0.9, col, 2)
    head = np.full((50, img.shape[1], 3), 255, np.uint8)
    cv2.putText(head, title, (10, 35), 0, 1.1, (0, 0, 0), 2)
    return np.vstack([head, band, img])


def main():
    out = Path(sys.argv[1])
    specs = sys.argv[2:] or sorted(p.name for p in (ROOT / "product_library").iterdir()
                                   if (p / "ortho" / "bottom.npz").exists())
    cfg = load_config(None)
    summary = []
    for sid in specs:
        spec, faces = extract_product(sid, cfg)
        d = out / sid
        d.mkdir(parents=True, exist_ok=True)
        panels = []
        line = {"spec": sid}
        for fid, (rgb, ppw, feats, anchors, r) in faces.items():
            types = [f["type"] for f in feats]
            title = f"{spec.get('display_name', sid)} - {fid}: " + (", ".join(types) or "(none)")
            panel = render_face(rgb, ppw, feats, anchors, fid, title)
            cv2.imwrite(str(d / f"{fid}.png"), panel)
            panels.append(panel)
            line[fid] = types
        # 한눈에: 네 면을 폭 2400으로 맞춰 세로로
        sc = [cv2.resize(p, None, fx=2400 / p.shape[1], fy=2400 / p.shape[1]) for p in panels]
        cv2.imwrite(str(d / "overview.png"), np.vstack(sc))
        exp = {
            "buttons": [(b["side"], b["type"]) for b in spec["sides"].get("buttons", [])],
            "ports": [p.get("type") for p in spec["sides"].get("ports", [])],
            "s_pen_slot": bool((spec["sides"].get("s_pen_slot") or {}).get("present")),
            "sim_tray": (spec["sides"].get("sim_tray") or {}).get("side"),
        }
        line["spec_expected"] = exp
        summary.append(line)
        print(json.dumps(line, ensure_ascii=False), flush=True)
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
