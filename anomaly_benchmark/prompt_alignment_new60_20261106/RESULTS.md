# 프롬프트 검사 추가 후 신규 60개 재평가 (2026-11-06)



채점 응답 상태: {'completed': 59, 'invalid_response': 1}.

구현 커밋 `94ef817`를 푸시한 후 기존 시각 관측에만 프롬프트 정합성 검사를 추가했다.
원본 라벨과 기존 C의 순서·ID·내용을 보존했다. 판정 기준은 동일한 `event-claims-5`다.

| 상태 | 기존 시각 검사 v5 | 프롬프트 추가 통합 v5 |
|---|---:|---:|
| hit | 19 | 22 |
| pending | 24 | 23 |
| no_hit | 17 | 15 |

통합 자동 라벨 대응은 22/60 (36.7%)이며,
85% 목표는 51/60이다. 이것은 검출 정확도가 아니며, 라벨 밖 후보를 정답으로 추가하지 않았다.

## 검사와 기여

- 프롬프트 검사 상태: {'completed': 60}.
- 새 프롬프트 불일치 후보: 41개.
- 프롬프트 후보와 원본 라벨 사이에 의미 대응이 있는 영상: 9개.
- 같은 통합 평가에서 기존 시각 후보와 라벨의 의미 대응이 있는 영상: 18개.
- 위 두 값은 중복 가능하며 합산하지 않는다. 또한 검출 전체 미완료인 영상의 대응도 포함하므로 통합 hit과 다를 수 있다.
- 통합 판정은 기존 v5의 전체 요청 완료 조건을 유지한다. 기존 시각 검출 미완료나 새 프롬프트 검사 실패는 pending이다.
- 보류 원인(평가 미완료 → 시각 미완료 → 프롬프트 미완료 → 의미 불확실 우선): {'semantic_uncertainty': 16, 'visual_detection_incomplete': 6, 'evaluation_incomplete': 1}.

## 실행 재현 및 한계

- 기존 60개 모두 실제 Spotlight 생성 프롬프트가 있다. 생성 프롬프트만 검출 입력에 전달하고 라벨·난이도는 전달하지 않았다.
- 전체 프롬프트 검출 후 원본 라벨로 평가했다. 프롬프트를 새로운 정답 라벨로 사용하지 않았다.
- 후보 입력 동일 영상의 평가 28개는 원본 JSON을 재사용했다.
- 독립 R 해석 110회는 입력·시스템 지시·스키마 해시를 검증하고 기존 원문 응답을 재사용했다.
- 형식 오류/인증 중단 후 제한 재실행: [{'asset_id': 'sid_117_veo3', 'before_evaluation_status': 'invalid_response', 'after_evaluation_status': 'completed', 'after_status': 'pending'}, {'asset_id': 'sid_075_veo3', 'before_evaluation_status': 'invalid_response', 'after_evaluation_status': 'invalid_response', 'after_status': 'pending'}, {'asset_id': 'sid_122_ltx2', 'before_evaluation_status': 'invalid_response', 'after_evaluation_status': 'completed', 'after_status': 'hit'}, {'asset_id': 'sid_158_seedance', 'before_evaluation_status': 'failed', 'after_evaluation_status': 'completed', 'after_status': 'pending'}, {'asset_id': 'sid_184_seedance', 'before_evaluation_status': 'not_run', 'after_evaluation_status': 'completed', 'after_status': 'pending'}, {'asset_id': 'sid_184_ltx2', 'before_evaluation_status': 'not_run', 'after_evaluation_status': 'completed', 'after_status': 'hit'}, {'asset_id': 'sid_195_seedance', 'before_evaluation_status': 'not_run', 'after_evaluation_status': 'completed', 'after_status': 'pending'}, {'asset_id': 'sid_184_veo3', 'before_evaluation_status': 'not_run', 'after_evaluation_status': 'completed', 'after_status': 'hit'}]. 성공 단계 재사용(독립 R 외): 5회. 최초 결과는 로컬 `initial_pass/`에 보존했다.
- 새 원격 호출 시도: {'evaluation': 145, 'detection': 62}. 동시 처리 2영상, 실행 31.1분.
- 후보 추가 영상은 기존 후보도 함께 다시 비교하므로 비교 단계의 변동이 가능하다. 전후 hit 증분 전체를 순수 프롬프트 검출 효과로 보지 않는다.
- 입력·코드·이전 결과 해시, 모든 C 보존, 모든 완료 평가의 단계·판정을 검증했다.
- 반복 개발 평가이며 독립 holdout 또는 사람이 확인한 정확도가 아니다. 의미 매칭은 실제 영상 관측의 진실성을 보증하지 않는다.

`index.html`은 60개 영상·프롬프트·요구사항 판정·R/C를 한 페이지에서 보여준다.
`summary.html`/`comparison.csv`는 영상별 전후 및 기여 비교, `evaluation.html`은 v5 단계별 근거다.
이전 평가의 기준 사본은 `visual_baseline_scorecard.json`, 신규 관측 원문은 `reports/`에 있다.

## 생성 모델별 통합 결과

| 모델 | 기존 hit | 통합 hit | pending | no_hit | 추가 프롬프트 C |
|---|---:|---:|---:|---:|---:|
| ltx2 | 7 | 8 | 9 | 3 | 13 |
| seedance | 6 | 7 | 8 | 5 | 17 |
| veo3 | 6 | 7 | 6 | 7 | 11 |

요구사항 판정 개수: {'matched': 204, 'mismatch': 41, 'unassessable': 5}. 요구사항 개수는 영상 hit과 별도다.

## 판정 변화의 직접 원인

| 영상 | 전 → 후 | 확인된 변화 |
|---|---|---|
| sid_033_seedance | no_hit → hit | 새 프롬프트 후보가 라벨과 대응 |
| sid_033_veo3 | no_hit → hit | 새 프롬프트 후보가 라벨과 대응 |
| sid_157_veo3 | no_hit → hit | 새 프롬프트 후보가 라벨과 대응 |
| sid_154_ltx2 | pending → hit | 기존 시각 후보를 재채점한 결과가 변함. 프롬프트 후보 자체의 대응은 없음 |
| sid_075_veo3 | hit → pending | 채점 응답 인용이 선택한 라벨 주장에 속하지 않아 검증 실패. 검출 실패로 해석하지 않음 |
| sid_079_seedance | pending → no_hit | 새 후보 포함 재채점에서 의미 대응이 확인되지 않음 |

따라서 hit 순증 3개를 단순한 검출 성능 향상치로 단정하지 않는다. 새 프롬프트 후보의 직접 기여 3개,
기존 시각 후보의 재평가 변화 1개, 평가 미완료로 보류된 기존 hit 1개가 함께 반영됐다.
`sid_075_veo3`는 기존 자동 형식 보정과 별도 제한 재실행 후에도 동일한 근거 검증 오류가 남았다.
채점 응답은 59개 완료, 1개 미완료이며 인증 때문에 미실행인 항목은 더 이상 없다.
