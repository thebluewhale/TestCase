"""객체 대조 개발셋: 통제 렌더링과 실제 추적/검수, 사후 채점을 분리한다."""

import json
import math
import shutil
import time
from collections import Counter
from pathlib import Path

import av
import numpy as np
from PIL import Image, ImageDraw

from review_anomaly_v3.config import Config, load_config
from review_anomaly_v3.evaluation.tracking import box_iou as tracking_iou
from review_anomaly_v3.io import contained_path, sha256_file, write_json

FPS, FRAMES, WIDTH, HEIGHT = 30, 180, 640, 360
KINDS = ("steady", "occlusion", "exit", "cut", "camera", "disappear", "position", "area", "aspect")
CODES = {
    "disappear": ["OBJECT_TRACK_END"],
    "position": ["OBJECT_POSITION_JUMP", "OBJECT_IOU_DROP"],
    "area": ["OBJECT_AREA_JUMP"],
    "aspect": ["OBJECT_ASPECT_JUMP"],
}
PROTOCOL = {
    "version": "object-comparison-v1",
    "split": "development",
    "time_tolerance_sec": 0.25,
    "minimum_roi_iou": 0.2,
    "matching": "one event per clip; one displayed candidate per event; extra candidates retained",
    "primary": "end-to-end displayed candidate recall, regardless of candidate code",
    "secondary": "matching candidate with expected code; partial/failed/unrun stay in denominator",
    "max_new_requests": 18,
    "max_new_video_sec": 108,
    "normal_scope": "controlled transitions only; LaSOT originals are unlabeled review burden",
    "native_lasot_fps": None,
    "actual_ai_defects": 0,
}


def box_iou(first, second):
    return tracking_iou(np.asarray(first, dtype=float), np.asarray(second, dtype=float))


def read(path):
    return json.loads(Path(path).read_text())


def background():
    y, x = np.mgrid[:HEIGHT, :WIDTH]
    # 결정론적 질감: 소실 맥락 검사가 저텍스처만으로 판단 불가가 되지 않도록 한다.
    a = 110 + 22 * np.sin(x / 12) + 18 * np.cos(y / 9) + 12 * ((x // 24 + y // 24) % 2)
    return Image.fromarray(np.stack([a, a + 12, a + 24], axis=-1).clip(0, 255).astype("uint8"))


def render(sprite, kind, index):
    """픽셀과 평가 전용 객체 박스를 함께 반환. 추적 API에는 영상만 전달한다."""
    if kind not in KINDS or not 0 <= index < FRAMES:
        raise ValueError("Unknown variant or frame")
    t = index / FPS
    scene = background()
    cx, cy, w, h = 240, 180, sprite.width, sprite.height
    visible = True
    if t >= 3:
        if kind == "disappear":
            visible = False
        elif kind == "position":
            cx = 465
        elif kind == "area":
            w, h = round(w * 1.4), round(h * 1.4)
        elif kind == "aspect":
            w, h = round(w * 1.6), round(h / 1.6)
        elif kind == "cut":
            scene = Image.fromarray(255 - np.asarray(scene))
            cx = 465
    if kind == "exit":
        cx -= round(max(0, t - 2) * 220)
    x, y = round(cx - w / 2), round(cy - h / 2)
    if visible:
        scene.paste(sprite.resize((w, h), Image.Resampling.LANCZOS), (x, y))
    if kind == "occlusion":
        # 가림막이 연속 이동하며 객체 밖 배경까지 덮는 정상 대조다.
        edge = round(420 - min(1, max(0, (t - 2) / 1.5)) * 320)
        ImageDraw.Draw(scene).rectangle((edge, 70, 530, 290), fill=(56, 82, 105))
        visible = edge >= x + w
    if kind == "camera":
        shift = round(max(0, t - 1) * 12)
        scene = Image.fromarray(np.roll(np.asarray(scene), shift, axis=1))
        x += shift
    visible = visible and x >= 0 and x + w <= WIDTH and y >= 0 and y + h <= HEIGHT
    return scene, {"time_sec": t, "bbox_xywh": [x, y, w, h], "fully_visible": visible}


def encode(path, sprite, kind):
    rows = []
    with av.open(str(path), "w") as container:
        stream = container.add_stream("libx264", rate=FPS)
        stream.width, stream.height, stream.pix_fmt = WIDTH, HEIGHT, "yuv420p"
        stream.options = {"crf": "18", "threads": "1"}
        for i in range(FRAMES):
            image, row = render(sprite, kind, i)
            rows.append(row)
            frame = av.VideoFrame.from_image(image)
            for packet in stream.encode(frame):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)
    with av.open(str(path)) as container:
        times = [float(f.pts * f.time_base) for f in container.decode(video=0)]
    if len(times) != FRAMES or any(abs(t - i / FPS) > 1e-6 for i, t in enumerate(times)):
        raise ValueError("Encoded frame/time mapping differs")
    return rows


def detector_fingerprint():
    package = Path(__file__).resolve().parents[1]
    return {
        str(p.relative_to(package)): sha256_file(p)
        for p in sorted(package.rglob("*.py"))
        if "evaluation" not in p.parts
    }


def prepare(parent: Path, root: Path):
    parent_plan = read(parent / "plan.json")
    root.mkdir(parents=True, exist_ok=False)
    (root / "videos").mkdir()
    (root / "labels").mkdir()
    samples = []
    for clip in parent_plan["clips"]:
        name = "original-" + clip["sequence_id"]
        media = contained_path(parent, clip["video"])
        if sha256_file(media) != clip["video_sha256"]:
            raise ValueError("Parent video changed")
        shutil.copyfile(media, root / f"videos/{name}.mp4")
        request_dir = parent / "api" / clip["sequence_id"]
        req = read(request_dir / "request.json")
        if req["status"] != "completed" or req["source_sha256"] != clip["video_sha256"]:
            raise ValueError("A completed hash-bound original API response is required")
        if sha256_file(request_dir / "raw_response.json") != req["response_sha256"]:
            raise ValueError("Original response changed")
        (root / "api" / name).mkdir(parents=True)
        for file in ("request.json", "raw_response.json"):
            shutil.copyfile(request_dir / file, root / "api" / name / file)
        samples.append(
            {
                "id": name,
                "stratum": "lasot_original",
                "kind": clip["selection_kind"],
                "lineage": "lasot:" + clip["sequence_id"],
                "duration_sec": clip["duration_sec"],
                "source_window": {
                    k: clip[k] for k in ("start_frame", "end_frame", "assigned_fps", "native_fps")
                },
                "api_reused": True,
                "events": [],
                "label_status": "no_ai_defect_annotation",
            }
        )
    # 평가 전 고정한 두 대상. 사각형 크롭이며 정밀 분할은 아니다.
    for name, number in (("book-3", 1), ("bottle-1", 270)):
        source = parent / "dataset/sequences" / name
        image_path = source / f"img/{number:08d}.jpg"
        gt = source / "groundtruth.txt"
        box = np.loadtxt(gt, delimiter=",")[number - 1]
        for flag in ("full_occlusion.txt", "out_of_view.txt"):
            if np.loadtxt(source / flag, delimiter=",").reshape(-1)[number - 1]:
                raise ValueError("Selected source crop must be visible")
        x, y, w, h = box
        with Image.open(image_path) as im:
            bounds = (
                max(0, math.floor(x)),
                max(0, math.floor(y)),
                min(im.width, math.ceil(x + w)),
                min(im.height, math.ceil(y + h)),
            )
            sprite = im.convert("RGB").crop(bounds)
        sprite.thumbnail((170, 130), Image.Resampling.LANCZOS)
        provenance = {
            "source_frame_local_1based": number,
            "source_image_sha256": sha256_file(image_path),
            "source_gt_sha256": sha256_file(gt),
            "crop_xyxy_px": list(bounds),
            "sprite_size": list(sprite.size),
            "method": "rectangular LaSOT crop on deterministic synthetic background",
            "limitations": (
                "crop contains background/possibly hand; no segmentation; "
                "static sprite; not an AI-generated defect"
            ),
        }
        for kind in KINDS:
            sample_id = f"synthetic-{name}-{kind}"
            rows = encode(root / f"videos/{sample_id}.mp4", sprite, kind)
            write_json(root / f"labels/{sample_id}.json", rows)
            events = []
            if kind in CODES:
                events = [
                    {
                        "id": sample_id + "-event",
                        "kind": kind,
                        "start_sec": 3.0,
                        "end_sec": 3 + 1 / FPS,
                        "affected_until_sec": FRAMES / FPS,
                        "boxes_xywh": [rows[89]["bbox_xywh"], rows[90]["bbox_xywh"]],
                        "expected_codes": CODES[kind],
                    }
                ]
            samples.append(
                {
                    "id": sample_id,
                    "stratum": "controlled_synthetic",
                    "kind": kind,
                    "lineage": "lasot:" + name,
                    "duration_sec": FRAMES / FPS,
                    "pair_id": f"synthetic-{name}-steady",
                    "width": WIDTH,
                    "height": HEIGHT,
                    "assigned_fps": FPS,
                    "frame_count": FRAMES,
                    "provenance": provenance,
                    "api_reused": False,
                    "events": events,
                    "label_status": "construction_known_transition",
                    "labels": f"labels/{sample_id}.json",
                    "labels_sha256": sha256_file(root / f"labels/{sample_id}.json"),
                }
            )
    for sample in samples:
        sample["video"] = f"videos/{sample['id']}.mp4"
        sample["video_sha256"] = sha256_file(root / sample["video"])
    write_json(root / "config.json", load_config().model_dump(mode="json"))
    plan = {
        "protocol": PROTOCOL,
        "parent_plan_sha256": sha256_file(parent / "plan.json"),
        "generator_sha256": sha256_file(Path(__file__)),
        "detector_files_sha256": detector_fingerprint(),
        "config_sha256": sha256_file(root / "config.json"),
        "samples": samples,
    }
    write_json(root / "plan.json", plan)
    # 평가 전 계획과 라벨 고정. API/검출기에는 GT를 전달하지 않는다.
    (root / "plan.sha256").write_text(sha256_file(root / "plan.json") + "\n")
    return plan


def validate_plan(root):
    if sha256_file(root / "plan.json") != (root / "plan.sha256").read_text().strip():
        raise ValueError("Frozen plan changed")
    plan = read(root / "plan.json")
    if plan["protocol"] != PROTOCOL or sha256_file(root / "config.json") != plan["config_sha256"]:
        raise ValueError("Protocol/config changed")
    samples = plan["samples"]
    if plan["detector_files_sha256"] != detector_fingerprint():
        raise ValueError("Frozen detector code changed")
    if len({s["id"] for s in samples}) != len(samples):
        raise ValueError("Duplicate samples")
    new = [s for s in samples if not s["api_reused"]]
    if (
        len(new) > PROTOCOL["max_new_requests"]
        or sum(s["duration_sec"] for s in new) > PROTOCOL["max_new_video_sec"]
    ):
        raise ValueError("Request budget exceeded")
    for s in samples:
        contained_path(root, s["id"])
        if sha256_file(contained_path(root, s["video"])) != s["video_sha256"]:
            raise ValueError("Video changed")
        if s.get("labels") and sha256_file(contained_path(root, s["labels"])) != s["labels_sha256"]:
            raise ValueError("Labels changed")
    return plan


def run_one(root, sample, project, region):
    from review_anomaly_v3.adapters.video_baseline import request_video
    from review_anomaly_v3.pipeline import inspect_media, validate_artifacts

    name = sample["id"]
    api = root / "api" / name
    record = request_video(root / sample["video"], api, project, region)
    result = {"id": name, "api_status": record["status"]}
    if record["status"] != "completed":
        return result
    out = root / "reports" / name
    if not out.exists():
        start = time.perf_counter()
        inspect_media(
            root / sample["video"],
            out,
            Config.model_validate(read(root / "config.json")),
            profile="object_temporal",
            object_api=api,
        )
        write_json(
            root / "timings" / f"{name}.json", {"local_wall_sec": time.perf_counter() - start}
        )
    report = validate_artifacts(out)
    if report.input is None or report.input.sha256 != sample["video_sha256"]:
        raise ValueError("Report source mismatch")
    result["execution"] = report.execution.status
    result["candidates"] = len(report.findings)
    return result


def overlap(event, candidate):
    temporal = (
        candidate["start_sec"] <= event["end_sec"] + PROTOCOL["time_tolerance_sec"]
        and candidate["end_sec"] >= event["start_sec"] - PROTOCOL["time_tolerance_sec"]
    )
    roi = max(box_iou(candidate["bbox_xywh"], b) for b in event["boxes_xywh"])
    return temporal and roi >= PROTOCOL["minimum_roi_iou"], roi


def score_events(events, candidates):
    # v1: 샘플별 사건 하나. 한 후보로 여러 사건을 맞추거나 중복 후보를 TP로 더하지 않는다.
    if len(events) > 1:
        raise ValueError("v1 supports at most one event per clip")
    matched = []
    for event in events:
        hits = [(c, overlap(event, c)[1]) for c in candidates if overlap(event, c)[0]]
        hits.sort(key=lambda p: (-p[1], abs(p[0]["start_sec"] - event["start_sec"]), p[0]["id"]))
        best = hits[0] if hits else None
        matched.append(
            {
                "event_id": event["id"],
                "detected": best is not None,
                "code_detected": any(
                    set(c["codes"]) & set(event["expected_codes"]) for c, _ in hits
                ),
                "candidate_id": best[0]["id"] if best else None,
                "roi_iou": best[1] if best else None,
                "onset_error_sec": best[0]["start_sec"] - event["start_sec"] if best else None,
            }
        )
    return matched


def evaluate(root):
    from review_anomaly_v3.pipeline import validate_artifacts

    plan = validate_plan(root)
    results = []
    for sample in plan["samples"]:
        name = sample["id"]
        out = root / "reports" / name
        api_path = root / "api" / name / "request.json"
        req = read(api_path) if api_path.exists() else {}
        row = {k: sample[k] for k in ("id", "stratum", "kind", "lineage", "api_reused")}
        row.update(
            api_status=req.get("status", "unrun"),
            execution="unrun",
            displayed_candidates=0,
            candidate_events=[],
            raw_status_counts={},
            target_pre_event_observed_fraction=None,
            coverage=None,
            api_total_session_sec=req.get("total_session_sec"),
            logical_requests=req.get("logical_requests", 0),
            actual_cost_usd=req.get("actual_cost_usd"),
        )
        candidates = []
        raw_events = []
        if (out / "report.json").exists():
            report = validate_artifacts(out)
            if report.input is None or report.input.sha256 != sample["video_sha256"]:
                raise ValueError("Scored report source mismatch")
            if read(out / "config_snapshot.json") != read(root / "config.json"):
                raise ValueError("Scored report config mismatch")
            row.update(
                execution=report.execution.status,
                report_sha256=sha256_file(out / "report.json"),
                coverage=next(
                    c.model_dump(mode="json")
                    for c in report.coverage
                    if c.check_id == "object_temporal"
                ),
                local_timings_sec=report.execution.timings_sec,
            )
            if (out / "object_candidates.json").exists():
                raw = read(out / "object_candidates.json")
                displayed = {f.id for f in report.findings}
                candidates = [e for e in raw["events"] if e["id"] in displayed]
                raw_events = raw["raw_events"]
                row.update(
                    displayed_candidates=len(candidates),
                    candidate_events=candidates,
                    raw_status_counts=dict(Counter(e["status"] for e in raw_events)),
                )
            if (out / "object_observations.json").exists():
                observations = read(out / "object_observations.json")
                row["track_count"] = len(observations["tracks"])
                if sample.get("labels"):
                    labels = read(root / sample["labels"])
                    probe = [
                        label
                        for label in labels
                        if 2.5 <= label["time_sec"] < 3 and label["fully_visible"]
                    ]
                    observed = sum(
                        any(
                            abs(o["time_sec"] - label["time_sec"]) <= 0.06
                            and box_iou(o["bbox_xywh"], label["bbox_xywh"]) >= 0.2
                            for tr in observations["tracks"]
                            if tr["confidence"] >= 0.5
                            for o in tr["observations"]
                        )
                        for label in probe
                    )
                    row["target_pre_event_observed_fraction"] = (
                        observed / len(probe) if probe else None
                    )
        row["events"] = score_events(sample["events"], candidates)
        row["unmatched_displayed_candidates"] = len(candidates) - sum(
            e["detected"] for e in row["events"]
        )
        row["event_nearby_raw_statuses"] = [
            dict(Counter(e["status"] for e in raw_events if overlap(label, e)[0]))
            for label in sample["events"]
        ]
        results.append(row)
    synthetic = [r for r in results if r["stratum"] == "controlled_synthetic"]
    positives = [r for r in synthetic if r["events"]]
    controls = [r for r in synthetic if not r["events"]]
    originals = [r for r in results if r["stratum"] == "lasot_original"]
    events = [e for r in positives for e in r["events"]]
    by_kind = {}
    for kind in CODES:
        rows = [r for r in positives if r["kind"] == kind]
        by_kind[kind] = {
            "events": len(rows),
            "detected": sum(r["events"][0]["detected"] for r in rows),
            "code_detected": sum(r["events"][0]["code_detected"] for r in rows),
        }
    summary = {
        "protocol": PROTOCOL,
        "plan_sha256": sha256_file(root / "plan.json"),
        "config_sha256": plan["config_sha256"],
        "samples": len(results),
        "synthetic_events": len(events),
        "detected_events": sum(e["detected"] for e in events),
        "event_recall_end_to_end": sum(e["detected"] for e in events) / len(events)
        if events
        else None,
        "by_kind": by_kind,
        "synthetic_controls": len(controls),
        "control_candidates": sum(r["displayed_candidates"] for r in controls),
        "control_clips_with_candidates": sum(r["displayed_candidates"] > 0 for r in controls),
        "control_candidates_per_clip": sum(r["displayed_candidates"] for r in controls)
        / len(controls)
        if controls
        else None,
        "original_review_candidates": sum(r["displayed_candidates"] for r in originals),
        "execution_counts": dict(Counter(r["execution"] for r in results)),
        "api_status_counts": dict(Counter(r["api_status"] for r in results)),
        "new_logical_requests": sum(r["logical_requests"] for r in results if not r["api_reused"]),
        "reused_original_requests": sum(r["api_reused"] for r in results),
        "results": results,
    }
    write_json(root / "summary.json", summary)
    return summary
