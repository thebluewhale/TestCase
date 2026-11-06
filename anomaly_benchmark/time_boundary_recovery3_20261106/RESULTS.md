# 시간 경계 오류 3개 복구 후 60개 결과 갱신 (2026-11-06)

동일한 신규 60개 표본에서 시간 경계 오류가 있던 seedance 3개만 복구했다.
의미 매칭 기준은 `event-claims-5`로 유지하고, 나머지 57개 채점 JSON은 바이트 단위로 재사용했다.
원본 보고서와 기존 평가 결과는 보존했다.

| 상태 | 복구 전 v5 | 복구 후 v5 |
|---|---:|---:|
| hit | 17 | 19 |
| pending | 26 | 24 |
| no_hit | 17 | 17 |

라벨 대응 hit은 19/60 (31.7%)이다.
이는 검출 정확도가 아니다. 1단계 85% 목표는 51/60이며, 라벨에 없는 결함을 정답으로 추가하지 않았다.

## 복구 대상

| 영상 | 기본 관측 처리 | 기본/집중 관측 상태 | 후보 수 전→후 | 재채점 |
|---|---|---|---|---|
| sid_022_seedance | stored_response_revalidated | completed / completed | 1 → 3 | pending → hit |
| sid_045_seedance | stored_response_revalidated | completed / completed | 0 → 3 | pending → hit |
| sid_195_seedance | new_vertex_call | invalid_response / not_run | 0 → 0 | pending → pending |

## 실행과 해석

- 허용오차 0.330초 내 시간 경계만 실제 영상 범위로 보정했다. 원문과 보정 이력은 JSON에 남겼다.
- sid_022/045_seedance 기본 관측은 기존 모델 원문 재검증을 재사용했다.
- sid_195_seedance는 기존 응답에 좌표 오류도 있어 기본 관측을 새로 호출했다.
- 기본 관측이 완료된 sid_022/045_seedance에서 이전에 생략된 집중 관측을 실행했다. sid_195_seedance는 새 응답과 1회 재시도 모두 정규화 bbox에 수백 단위 좌표를 반환해 거부했고, 집중 관측은 실행하지 않았다. 따라서 결과 변화는 시간 보정뿐 아니라 추가 관측의 영향도 포함한다.
- 검출 단계에 정답 라벨·생성 프롬프트를 전달하지 않았다. 정답은 검출 종료 후 평가 단계에서만 사용했다.
- 원격 호출 시도 수: {'evaluation': 15, 'focused': 4, 'baseline': 2}. 모델은 Vertex AI gemini-3.8-flash만 사용했다.
- 실행 시간 7.4분. 기존 로컬 측정과 57개 평가를 재사용한 증분 실행이다.
- pending 원인: {'semantic_uncertainty': 18, 'detection_incomplete': 6}. 실패·미완료 영상도 분모 60에 포함했다.
- 독립 신규 표본 검증이 아니며, 사람 최종 검수 전 자동 평가다.
- 시간 표시는 소수점 세 자리, 원본 JSON의 정밀도는 유지한다.

검수: `index.html` / 전후 비교: `summary.html`, `comparison.csv` / 평가 상세: `evaluation.html`.
`recovery.json`은 세 영상의 원본·갱신 경로와 상태, `validation.json`은 검증 기록이다.
