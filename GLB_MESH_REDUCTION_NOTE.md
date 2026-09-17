# product_consistency v3 — GLB 메쉬 경량화 검토 노트 (2026-09-17)

## 배경

v3 자세 정합(`backend/review_product_consistency_v3/core/pose.py`)은 정규화 GLB
(`product_library/galaxy-s25/model_canonical.glb`, 6.9만 면)를 PyTorch3D로 반복 렌더한다.
L4 GPU에서 이미지 1장 검증에 4분 이상 걸리는 문제가 있어, 외형(모서리·사이드 버튼·카메라·
카메라 섬의 모양과 높낮이)을 유지하면서 면 수를 줄일 방법을 검토했다.

이 VM(CPU 4코어)에서는 실루엣 IoU 검증이 너무 느려 중단했다. **면 수 실측은 완료, 실루엣
정확도 검증은 미완료** — GPU VM에서 `measure2.py`로 마저 확인해야 한다.

## 결론 요약

1. 메쉬는 부품별 처리로 **1/4~1/6**까지 줄일 수 있다 (형상 손실 없는 단계만으로 57% 감소).
2. 그보다 먼저 **래스터 설정(`bin_size=0`)** 이 더 큰 원인일 가능성이 높다 (코드 확인, 미측정).
3. "prt 변환"이라는 경량화 방법은 찾지 못했다. `.prt`는 Creo·NX의 CAD 파트 포맷으로 오히려
   더 무거운 파라메트릭 데이터다. 프록시(proxy)·LOD 메쉬를 뜻한 것으로 보인다.

## 1. 메쉬 구성 (실측)

- 부품(geometry) 46개, 정점 103,927, 면 69,159. 모든 부품이 non-watertight.
- 전·후면 유리판 3장(두께 0.005의 평판 — `galaxy_s25`, `galaxy_s25_1`, `galaxy_s25_4`)이
  31,512면으로 **전체의 46%**. 평평한 판이 잘게 쪼개져 있을 뿐이라 형상 정보가 없다.
- 프레임 부품(`_18`, `_21`, `_19`, `_24`, `_23`, `_16`) 약 2.3만 면.
- 카메라 링·버튼 등 작은 부품은 각 100~1,300면.

## 2. 경량화 실측 (bpy, 부품별)

`decimate_v2.py`로 Blender bpy 데시메이션을 **부품 단위**로 적용했다. 부품 경계를 넘어
합치지 않으므로 버튼·카메라 링 같은 작은 부품은 독립적으로 보존된다.

| 방법 | 면 수 | 비고 |
|---|---|---|
| 원본 | 69,159 | |
| 정점 병합 + 평면 병합(각도 1°) | 29,657 | **형상 손실 없음**. 평평한 판만 합쳐짐 |
| 위 + 부품별 collapse 50% (바닥 300면) | 17,027 | 곡면 모서리 약간 거칠어짐 |
| 위 + 부품별 collapse 25% (바닥 200면) | 10,450 | 실루엣 검증 필요 |

부품별 결과 (평면 병합만):

```
 11834 ->  3352  galaxy_s25      (전면 유리)
 11834 ->  3348  galaxy_s25_1    (후면 유리)
  8330 ->  2120  galaxy_s25_18   (프레임)
  7844 ->  1856  galaxy_s25_4    (디스플레이)
  3396 ->    68  galaxy_s25_21   (측면 평판)
  2822 ->   416  galaxy_s25_19
  1284 ->  1284  galaxy_s25_43   (카메라 링 — 변화 없음)
```

핵심 포인트:

- **정점 병합이 선행돼야 한다.** GLB 임포트 시 UV·노멀 경계에서 정점이 끊겨 있어, 병합 없이
  평면 병합만 하면 38,989면에서 멈춘다 (`remove_doubles` 후 29,657).
- **collapse는 부품별 + 최소 면 수 바닥.** 기존 `pose.mesh_max_faces`의 `fast_simplification`은
  전체 메쉬를 한 번에 줄여 얇은 부품에 구멍이 났다 (pose.py 주석). 부품 단위로 하고 작은
  부품에 바닥(200~300면)을 두면 이 문제를 피한다.
- 추가 여지: **어느 방향에서도 보이지 않는 면 삭제**(내부 유리면·안쪽 셸). 다중 뷰에서
  hard 래스터로 보인 면 ID를 모아 한 번도 안 보인 면을 지우면 실루엣은 정확히 같은 채로 더
  줄어든다. 미구현.

## 3. 래스터 설정 (코드 확인, 미측정)

`core/models/renderer.py`의 `SilhouetteRenderer`:

- `bin_size=0` (naive 래스터화) — 픽셀마다 전체 면을 훑으므로 비용이 면 수에 정비례.
  주석은 coarse 비닝의 빈당 면 수 초과를 우려하는데, 해법은 비닝을 끄는 것이 아니라
  `max_faces_per_bin`을 명시하는 것. 메쉬가 1만 면대로 줄면 오버플로 자체가 사라진다.
- 반복마다 soft·hard **두 번** 래스터한다.
- `image` 프로파일: 가설 8개 × `refine_iters` 200 = 1,600회 반복, 각각 2회 래스터 + backward.

메쉬 경량화와 비닝을 합치면 4분이 수십 초 단위로 내려갈 여지가 크다.

## 4. GPU VM에서 검증하는 절차

```bash
cd backend/review_product_consistency_v3
P=.venv/bin/python
S=../..   # 이 노트와 스크립트가 있는 레포 루트

# 1) 데시메이션 (angle_deg, collapse_ratio, min_faces) — ratio 1이면 평면 병합만
$P $S/decimate_v2.py -- $PWD/product_library/galaxy-s25/model_canonical.glb /tmp/planar.glb 1.0 1 0
$P $S/decimate_v2.py -- $PWD/product_library/galaxy-s25/model_canonical.glb /tmp/c50.glb  1.0 0.5 300
$P $S/decimate_v2.py -- $PWD/product_library/galaxy-s25/model_canonical.glb /tmp/c25.glb  1.0 0.25 200

# 2) 원본 대비 16개 무작위 뷰 실루엣 IoU (512px, hard 래스터). CPU에서는 수십 분 — GPU 권장
$P -u $S/measure2.py product_library/galaxy-s25/model_canonical.glb /tmp/planar.glb /tmp/c50.glb /tmp/c25.glb
```

채택 기준 제안: 16뷰 IoU 최솟값 ≥ 0.995, xor 픽셀 최대 ≤ 수백 (512² 기준). 평면 병합 단계는
정의상 실루엣이 같아야 하므로 IoU ≈ 1.0이 나와야 하고, 아니면 스크립트 문제다.

`measure2.py`는 CUDA를 자동 선택하지 않는다 — GPU에서 돌리려면 `torch.tensor(...)`에
`device="cuda"`를 주고 `Meshes`·카메라도 같은 디바이스로 옮겨야 한다.

## 5. 적용 시 코드 변경 지점 (미적용)

- `onboard/normalize.py` 뒤에 자세 정합용 프록시 메쉬(`model_pose.glb`) 생성 단계 추가.
  Blender 합성·결함 생성은 원본 `model_canonical.glb`를 그대로 쓴다 (EEVEE는 6.9만 면 문제 없음).
- `core/run_job.py`의 `build_pose_model`이 프록시를 우선 로드. `pose.mesh_max_faces`의
  `fast_simplification` 경로는 제거하거나 디버그 전용으로 유지.
- `renderer.py`: `bin_size=0` → 비닝 + `max_faces_per_bin` 명시. 변경 후 실루엣 IoU 회귀 확인.
- `docs/SDP/REVIEW_PRODUCT_CONSISTENCY_V3.md` G1-6(30초·1080p ≤ 10분) 실측 시 함께 기록.

## 첨부

- `decimate_v2.py` — bpy 부품별 데시메이션 (정점 병합 → 평면 병합 → 삼각화 → collapse)
- `measure2.py` — 원본 대비 다중 뷰 실루엣 IoU 측정 (PyTorch3D)
