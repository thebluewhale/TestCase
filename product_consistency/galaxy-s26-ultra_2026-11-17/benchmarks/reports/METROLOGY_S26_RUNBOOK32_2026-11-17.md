# 수정된 references 재적용 및 S26 전체 평가 — 2026-11-17

## 변경 이유와 범위

2026-11-16에 14장을 완료한 뒤 실행이 중단됐고, 2026-11-17에 코드·기준·입력 해시가 동일함을 확인하고 남은 18장을 재개했다. 저장된 이미지별 처리 시간만 집계하며 중단 대기 시간은 포함하지 않는다.

수정된 runbook은 자동 제품 검출기가 아니라 사람이거나 AI가 원본 좌표 격자로 박스를 정하고, GrabCut 마스크를 눈으로 검토하는 절차임을 명시한다. 이전 자동 평가에는 이 위치 입력이 없었다. 이번에는 같은 good 21장·ng 11장 전체에 검토한 박스/뷰 정보를 제공했다. 새 자동 분할 모델이나 VLM 호출은 추가하지 않았다.

- 분할: 긴 변 1100px, 8회 GrabCut, 최대 연결 성분, 5×5 닫힘, 축소 영상에서 피부 제거·열림·성분 재선택, 원본 크기의 부드러운 알파. `--foreground-box`, `--no-deskin` 지원.
- 근거: 격자와 분할 미리보기 도구, 원본 마스크·UNKNOWN 마스크·면적비·볼록도·박스 접촉 기록. 후속 기하 오류에도 분할 근거 보존.
- 입력 연결: 이미지 해시와 제품 ID로 박스 파일 검증. box/foreground_box/deskin/view만 검사기에 전달하며 파일명·결함 설명은 전달하지 않음.
- 아일랜드: handover §6.13의 crop `[0,0,50,72]`mm와 배경 `[30,44,48,60]`mm 사용. 가시성은 경계 주변에서 검사하며 멀리 떨어진 손만으로 보류하지 않음.
- 사선 종횡비: handover §6.11에 따라 편차가 5%와 4σ를 각각 넘을 때 NG. 두 값을 더한 임계값을 사용하던 이식 차이 수정. 불확실한 결과는 UNKNOWN 유지.
- S25의 검증되지 않은 임시 팩은 적용하지 않음. S26의 기존 치수·원 위치·돌출 높이·R 값은 그대로 유지.
- 전체 정상 판정 계약, 가림·해상도·부품 역할 구분 등 v4의 검증 조건은 유지. 원본 PoC의 모든 판단을 그대로 승인하는 모드는 아님.

## 분할 검증

32장 모두 사전 분할 마스크를 생성하고 제품 중심 확대 미리보기로 확인했다. 공식 10장은 입력 알파를 사용했고, 나머지 22장은 검토한 박스를 사용했다. Good_01/02/Test_16/17의 박스는 공급 문서·코드에서 가져와 시각 확인했다. 나머지는 원본 좌표 격자에서 지정했다. 분홍색 본체 Failed_01은 피부 제거를 해제했다. 모든 전경 seed는 비워 두었다.

Good_01/02의 원본 `segment.py`를 임시 폴더에서 수정 없이 실행했다. v4와 비교한 이진 마스크 IoU=1.0, 알파 픽셀 일치율=1.0, 최대 차이=0으로 두 이미지 모두 완전 일치했다. 면적/볼록 껍질 비율의 진단은 v4에서 원본 크기 마스크로 계산하므로 원본 코드의 축소 마스크 진단과 약간 다르다.

[원본 분할 대조 기록](RUNBOOK_SEGMENTATION_PARITY_2026-11-16.json), [독립 설치 76개 테스트](RUNBOOK_ISOLATION_2026-11-16.json).

## 이미지 수준 결과

good은 전체 MATCH, ng는 하나 이상의 MISMATCH다. 미구현 로고·버튼 및 기타 판단 불가를 good으로 바꾸지 않았다. 따라서 good 검출 0은 정상 판별 정확도가 높거나 낮다는 단순 이진 지표로 해석할 수 없다.

| 구분 | 이전 자동 모드 | 이번 박스 제공 모드 |
|---|---:|---:|
| good → good | 0/21 | 0/21 |
| ng → ng | 2/11 | 4/11 |
| good → ng | 0/21 | 0/21 |
| ng → good | 0/11 | 0/11 |
| good → 판단 불가 | 21/21 | 21/21 |
| ng → 판단 불가 | 9/11 | 7/11 |

기하 분석 완료: 이전 12/32 → 이번 28/32. 이번 실제 검사 실행의 분할 완료는 29/32이며, 전면·측면 3장은 관측한 뷰 힌트에 따라 후면 검사를 시작하지 않았다.
공식 Front/Back과 동일한 2장을 제외한 30장(정상 19·결함 11)의 별도 집계는 JSON에 있다. 모두 개발 데이터이며 독립 holdout이 아니다. 입력 보조와 코드가 함께 바뀌었으므로 변화 전체를 자동 검출 성능 향상으로 주장하지 않는다.

NG 경보 4장은 이미지 수준 집계다. Failed_04/05는 C01(렌즈 누락), Failed_09는 C02(아일랜드 경계 이상)에서 경보가 발생했다. Failed_06의 정답은 렌즈 크기 증가지만 검출 항목은 C02(아일랜드 경계 이상)이므로, 정답 결함을 정확히 검출한 사례로 계산하지 않는다. 따라서 4/11을 항목별 결함 검출률로 해석하면 안 된다.

## 처리 시간

- 평균: **23.733초/장** (이전 11.378초/장).
- 최단: **1.525초**, `Official_S26U_RightSide.png` (unknown, back_face_engine_does_not_assess_requested_view).
- 최장: **73.871초**, `Good_02.png` (unknown, None).
시간은 엔진의 이미지 입력→분할→기하→JSON/HTML/이미지 저장이다. 박스 지정과 사전 마스크 검토 시간은 제외했다. 실제 엔진에서는 분할을 다시 수행했으며 그 시간은 포함했다. 미지원/실패 사례도 평균에 포함했다. CPU 순차 실행, BLAS/OMP 각 1스레드, 작업 제한 120초.

## 남은 한계와 데이터 주의점

`Failed_01.png`는 분할 이후 기하 처리에서 IndexError가 발생해 UNKNOWN으로 기록했다. 오류 사례를 제외하거나 정상으로 처리하지 않았다.

박스 제공은 제품 검출 자동화의 대체가 아니다. 실제 서비스에서 박스를 누가 제공할지 또는 어떤 검출기를 연결할지는 별도 작업이다. 마스크가 있어도 원 매칭·자세·가시성·해상도 때문에 판정이 보류될 수 있다. 로고/버튼·독립 두께 검증은 여전히 미구현이다.
사용자 데이터 분류를 우선했다. 예를 들어 references는 Test_06을 아일랜드 이상으로 서술하지만 입고 good/에 있으므로 정상 라벨로 집계한다. label.json의 Failed_15/Test_15 파일명 불일치는 원본을 수정하지 않고 상세 결함 미연결 상태로 유지한다.

| 기하 분석 미완료 사유 | 장수 |
|---|---:|
| back_face_engine_does_not_assess_requested_view | 3 |
| IndexError | 1 |

## 파일별 결과

| 파일 | 정답 | 판정 | 결함 항목 | 판단 가능 | 시간(초) |
|---|---|---|---|---:|---:|
| [Good_01.png](../../outputs/metrology_s26_runbook32_2026-11-16/Good_01/report.html) | good | unknown | — | 6/12 | 29.696 |
| [Good_02.png](../../outputs/metrology_s26_runbook32_2026-11-16/Good_02/report.html) | good | unknown | — | 5/12 | 73.871 |
| [Official_S26U_Back.png](../../outputs/metrology_s26_runbook32_2026-11-16/Official_S26U_Back/report.html) | good | unknown | — | 7/12 | 24.068 |
| [Official_S26U_BackLeft30.png](../../outputs/metrology_s26_runbook32_2026-11-16/Official_S26U_BackLeft30/report.html) | good | unknown | — | 5/12 | 21.135 |
| [Official_S26U_BackLeft30_Black.png](../../outputs/metrology_s26_runbook32_2026-11-16/Official_S26U_BackLeft30_Black/report.html) | good | unknown | — | 5/12 | 21.920 |
| [Official_S26U_BackLeft30_White.png](../../outputs/metrology_s26_runbook32_2026-11-16/Official_S26U_BackLeft30_White/report.html) | good | unknown | — | 5/12 | 20.373 |
| [Official_S26U_BackRight30.png](../../outputs/metrology_s26_runbook32_2026-11-16/Official_S26U_BackRight30/report.html) | good | unknown | — | 5/12 | 18.835 |
| [Official_S26U_Back_Black.png](../../outputs/metrology_s26_runbook32_2026-11-16/Official_S26U_Back_Black/report.html) | good | unknown | — | 7/12 | 26.578 |
| [Official_S26U_Back_White.png](../../outputs/metrology_s26_runbook32_2026-11-16/Official_S26U_Back_White/report.html) | good | unknown | — | 7/12 | 25.601 |
| [Official_S26U_Front.png](../../outputs/metrology_s26_runbook32_2026-11-16/Official_S26U_Front/report.html) | good | unknown | — | 0/12 | 2.071 |
| [Official_S26U_LeftSide.png](../../outputs/metrology_s26_runbook32_2026-11-16/Official_S26U_LeftSide/report.html) | good | unknown | — | 0/12 | 1.529 |
| [Official_S26U_RightSide.png](../../outputs/metrology_s26_runbook32_2026-11-16/Official_S26U_RightSide/report.html) | good | unknown | — | 0/12 | 1.525 |
| [Test_01.jpg](../../outputs/metrology_s26_runbook32_2026-11-16/Test_01/report.html) | good | unknown | — | 1/12 | 22.791 |
| [Test_02.jpg](../../outputs/metrology_s26_runbook32_2026-11-16/Test_02/report.html) | good | unknown | — | 4/12 | 22.461 |
| [Test_03.png](../../outputs/metrology_s26_runbook32_2026-11-16/Test_03/report.html) | good | unknown | — | 1/12 | 28.415 |
| [Test_04.jpg](../../outputs/metrology_s26_runbook32_2026-11-16/Test_04/report.html) | good | unknown | — | 0/12 | 24.982 |
| [Test_06.png](../../outputs/metrology_s26_runbook32_2026-11-16/Test_06/report.html) | good | unknown | — | 0/12 | 27.845 |
| [Test_16.png](../../outputs/metrology_s26_runbook32_2026-11-16/Test_16/report.html) | good | unknown | — | 4/12 | 23.578 |
| [Test_17.png](../../outputs/metrology_s26_runbook32_2026-11-16/Test_17/report.html) | good | unknown | — | 5/12 | 21.588 |
| [final.png.1280 (1).jpg](../../outputs/metrology_s26_runbook32_2026-11-16/final.png.1280 (1)/report.html) | good | unknown | — | 0/12 | 25.536 |
| [final.png.1280.jpg](../../outputs/metrology_s26_runbook32_2026-11-16/final.png.1280/report.html) | good | unknown | — | 0/12 | 18.579 |
| [Failed_01.png](../../outputs/metrology_s26_runbook32_2026-11-16/Failed_01/report.html) | ng | unknown | — | 0/12 | 6.417 |
| [Failed_02.png](../../outputs/metrology_s26_runbook32_2026-11-16/Failed_02/report.html) | ng | unknown | — | 0/12 | 38.047 |
| [Failed_03.png](../../outputs/metrology_s26_runbook32_2026-11-16/Failed_03/report.html) | ng | unknown | — | 0/12 | 21.356 |
| [Failed_04.png](../../outputs/metrology_s26_runbook32_2026-11-16/Failed_04/report.html) | ng | ng | C01 | 7/12 | 23.157 |
| [Failed_05.png](../../outputs/metrology_s26_runbook32_2026-11-16/Failed_05/report.html) | ng | ng | C01 | 7/12 | 23.117 |
| [Failed_06.png](../../outputs/metrology_s26_runbook32_2026-11-16/Failed_06/report.html) | ng | ng | C02 | 4/12 | 17.204 |
| [Failed_07.png](../../outputs/metrology_s26_runbook32_2026-11-16/Failed_07/report.html) | ng | unknown | — | 0/12 | 27.885 |
| [Failed_08.png](../../outputs/metrology_s26_runbook32_2026-11-16/Failed_08/report.html) | ng | unknown | — | 0/12 | 27.346 |
| [Failed_09.png](../../outputs/metrology_s26_runbook32_2026-11-16/Failed_09/report.html) | ng | ng | C02 | 4/12 | 51.939 |
| [Test_08.png](../../outputs/metrology_s26_runbook32_2026-11-16/Test_08/report.html) | ng | unknown | — | 1/12 | 17.940 |
| [Test_15.png](../../outputs/metrology_s26_runbook32_2026-11-16/Test_15/report.html) | ng | unknown | — | 0/12 | 22.071 |

## 재현 및 무결성

v4 디렉토리에서 `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python scripts/evaluate_metrology.py --product-id galaxy-s26-ultra --include-excluded --regions-file benchmarks/datasets/s26_ultra_regions.json --output outputs/NEW_RUN --timeout 120`.
코드 지문: `4b09d9fcccb92f8362ce79fde478d41acd24b9b78da9c8668c744033acbf7b78`.
32개 스키마·원본 사본, 근거 크롭 272개, 마스크 쌍 29개, HTML 로컬 링크 540개 검증. 원본 이미지·정답·references 56개 파일의 해시 보존 확인.
- [JSON](METROLOGY_S26_RUNBOOK32_2026-11-17.json) · [CSV](METROLOGY_S26_RUNBOOK32_2026-11-17.csv).
