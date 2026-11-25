"""미사용 LaSOT 계보의 18개 대조를 고정하고 실제 API+보조 탐색으로 평가한다."""

import argparse
import math
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import av
import numpy as np
from PIL import Image

from review_anomaly_v3.adapters.object_seed import discover
from review_anomaly_v3.adapters.video_baseline import request_video
from review_anomaly_v3.config import Config, load_config
from review_anomaly_v3.evaluation.object_comparison import (
    CODES,
    FPS,
    FRAMES,
    HEIGHT,
    KINDS,
    PROTOCOL,
    WIDTH,
    detector_fingerprint,
    encode,
    evaluate,
    read,
    validate_plan,
)
from review_anomaly_v3.io import sha256_file, write_json
from review_anomaly_v3.pipeline import inspect_media, validate_artifacts
from review_anomaly_v3.settings import Settings

SEQUENCES = ("cup-1", "hand-2")
VARIANTS = tuple(k for k in KINDS if k != "cut")


def encode_original(source, output):
    mapping = []
    with av.open(str(output), "w") as container:
        with Image.open(source / "img/00000001.jpg") as im:
            width, height = im.size
        stream = container.add_stream("libx264", rate=FPS)
        stream.width, stream.height, stream.pix_fmt = (
            width + (width % 2),
            height + (height % 2),
            "yuv420p",
        )
        stream.options = {"crf": "18", "threads": "1"}
        for i in range(FRAMES):
            path = source / f"img/{i + 1:08d}.jpg"
            with Image.open(path) as im:
                canvas = Image.new("RGB", (stream.width, stream.height))
                canvas.paste(im.convert("RGB"), (0, 0))
            mapping.append(
                {
                    "source_frame_1based": i + 1,
                    "source_sha256": sha256_file(path),
                    "time_sec": i / FPS,
                }
            )
            for packet in stream.encode(av.VideoFrame.from_image(canvas)):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)
    with av.open(str(output)) as container:
        actual = [float(f.pts * f.time_base) for f in container.decode(video=0)]
    if len(actual) != FRAMES or any(abs(t - i / FPS) > 1e-6 for i, t in enumerate(actual)):
        raise ValueError("Source frame/time mapping changed")
    return mapping, width, height


def prepare(root, source_root, previous):
    baseline = read(previous / "plan.json")
    if sha256_file(previous / "plan.json") != (previous / "plan.sha256").read_text().strip():
        raise ValueError("Previous frozen plan changed")
    prior_lineages = {s["lineage"] for s in baseline["samples"]}
    if prior_lineages & {"lasot:" + name for name in SEQUENCES}:
        raise ValueError("Fresh set must not reuse previous lineages")
    root.mkdir(parents=True, exist_ok=False)
    (root / "videos").mkdir()
    (root / "labels").mkdir()
    (root / "maps").mkdir()
    (root / "source").mkdir()
    samples = []
    for name in SEQUENCES:
        source = source_root / name.split("-")[0] / name
        image_path = source / "img/00000001.jpg"
        gt = source / "groundtruth.txt"
        if any(
            np.loadtxt(source / f, delimiter=",").reshape(-1)[0]
            for f in ("full_occlusion.txt", "out_of_view.txt")
        ):
            raise ValueError("First frame target must be visible before evaluating")
        x, y, w, h = np.loadtxt(gt, delimiter=",")[0]
        with Image.open(image_path) as im:
            bounds = (
                max(0, math.floor(x)),
                max(0, math.floor(y)),
                min(im.width, math.ceil(x + w)),
                min(im.height, math.ceil(y + h)),
            )
            sprite = im.convert("RGB").crop(bounds)
        sprite.thumbnail((170, 130), Image.Resampling.LANCZOS)
        sprite.save(root / "source" / f"{name}-sprite.png")
        provenance = {
            "source_sequence": name,
            "source_frame_1based": 1,
            "source_image_sha256": sha256_file(image_path),
            "source_gt_sha256": sha256_file(gt),
            "crop_xyxy_px": list(bounds),
            "sprite_size": list(sprite.size),
            "method": "rectangular LaSOT crop; same renderer as old comparison",
            "limitations": "crop includes background; not segmented, not an actual AI defect",
        }
        sid = "original-" + name
        mapping, width, height = encode_original(source, root / "videos" / f"{sid}.mp4")
        write_json(root / "maps" / f"{sid}.json", mapping)
        samples.append(
            {
                "id": sid,
                "stratum": "lasot_original",
                "kind": "visible",
                "lineage": "lasot:" + name,
                "duration_sec": FRAMES / FPS,
                "width": width,
                "height": height,
                "api_reused": False,
                "events": [],
                "source_window": {
                    "start_frame": 1,
                    "end_frame": FRAMES,
                    "assigned_fps": FPS,
                    "native_fps": None,
                },
                "label_status": "no_human_ai_defect_annotation",
                "source_mapping": f"maps/{sid}.json",
                "source_mapping_sha256": sha256_file(root / "maps" / f"{sid}.json"),
            }
        )
        for kind in VARIANTS:
            sid = f"synthetic-{name}-{kind}"
            rows = encode(root / "videos" / f"{sid}.mp4", sprite, kind)
            write_json(root / "labels" / f"{sid}.json", rows)
            events = []
            if kind in CODES:
                events = [
                    {
                        "id": sid + "-event",
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
                    "id": sid,
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
                    "labels": f"labels/{sid}.json",
                    "labels_sha256": sha256_file(root / "labels" / f"{sid}.json"),
                }
            )
    for s in samples:
        s["video"] = f"videos/{s['id']}.mp4"
        s["video_sha256"] = sha256_file(root / s["video"])
    if {s["video_sha256"] for s in samples} & {s["video_sha256"] for s in baseline["samples"]}:
        raise ValueError("Fresh videos duplicate baseline")
    write_json(root / "config.json", load_config().model_dump(mode="json"))
    plan = {
        "protocol": PROTOCOL,
        "detector_files_sha256": detector_fingerprint(),
        "config_sha256": sha256_file(root / "config.json"),
        "generator_sha256": sha256_file(Path(__file__)),
        "renderer_sha256": sha256_file(Path(encode.__code__.co_filename)),
        "previous_plan_sha256": sha256_file(previous / "plan.json"),
        "samples": samples,
        "fresh_evaluation": {
            "version": "fresh-lineages-v1",
            "sequences": list(SEQUENCES),
            "excluded_previous_lineages": sorted(prior_lineages),
            "detector_frozen": True,
            "tuning_after_results": False,
            "scope": "fresh-lineage development check, not a quality gate",
            "max_vi_submissions": 18,
            "max_seed_submissions": 18,
            "video_sec": 108,
            "cut_control": "omitted to retain 18-request VI cap",
        },
    }
    write_json(root / "plan.json", plan)
    (root / "plan.sha256").write_text(sha256_file(root / "plan.json") + "\n")
    validate_plan(root)
    return plan


def run_sample(root, sample, project, region):
    name = sample["id"]
    video = root / sample["video"]
    api = root / "api" / name
    seed = root / "seeds" / name
    req = request_video(video, api, project, region)
    if req["status"] != "completed":
        return {"id": name, "api_status": req["status"]}
    config = Config.model_validate(read(root / "config.json"))
    if seed.exists():
        seed_record = read(seed / "result.json")
        if seed_record["status"] == "completed":
            discover(video, seed, config, Settings(project=project))
    else:
        seed_record = discover(video, seed, config, Settings(project=project))
    out = root / "reports" / name
    if not out.exists():
        inspect_media(
            video, out, config, profile="object_temporal", object_api=api, object_seed_api=seed
        )
    report = validate_artifacts(out)
    if report.input.sha256 != sample["video_sha256"]:
        raise ValueError("Report source changed")
    return {
        "id": name,
        "api_status": req["status"],
        "seed_status": seed_record["status"],
        "execution": report.execution.status,
        "candidates": len(report.findings),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=["prepare", "run", "evaluate"])
    p.add_argument("--run", type=Path, required=True)
    p.add_argument(
        "--source-root", type=Path, default=Path("benchmarks/object_temporal/lasot/sequences")
    )
    p.add_argument("--previous", type=Path, default=Path("work/object-type-refinement-2026-11-25"))
    p.add_argument("--project")
    p.add_argument("--region", default="asia-east1")
    args = p.parse_args()
    if args.action == "prepare":
        plan = prepare(args.run, args.source_root, args.previous)
        print({"samples": len(plan["samples"])}, flush=True)
    elif args.action == "evaluate":
        result = evaluate(args.run)
        print(
            {
                k: result[k]
                for k in (
                    "samples",
                    "detected_events",
                    "by_kind",
                    "control_candidates",
                    "original_review_candidates",
                    "scope_status_counts",
                )
            },
            flush=True,
        )
    else:
        if not args.project:
            p.error("--project is required")
        plan = validate_plan(args.run)
        with ThreadPoolExecutor(max_workers=2) as pool:
            for result in pool.map(
                lambda s: run_sample(args.run, s, args.project, args.region), plan["samples"]
            ):
                print(result, flush=True)


if __name__ == "__main__":
    main()
