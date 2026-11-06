# 의미 매칭 v6 — 동일 60개 재채점 결과

2026-11-06. 서비스 `review_anomaly_v4`, 평가기 `event-claims-6`, Vertex `gemini-3.8-flash`.

## 결과

| 영상 상태 | 프롬프트 포함 v5 | v6 |
|---|---:|---:|
| hit | 22 | 26 |
| pending | 23 | 23 |
| no_hit | 15 | 11 |

분모 60개, 1단계 목표 51개를 유지했다. 자동 원본 라벨 대응 비율은 43.3%다.
검출 정확도·사람 확인 정밀도·독립 표본 성능으로 해석하지 않는다.
검출은 다시 호출하지 않았고, 기존 프롬프트 후보를 포함한 모든 C와 원본 R을 그대로 사용했다.
이전 v5의 한 채점 오류도 같은 입력으로 v6 평가를 새로 실행했다.

## 문제 사례

- `sid_079_seedance`: no_hit → hit. R4의 마시지 않음과 C3의 잔만 들고 마시지 않음이 대응한다.
- `sid_079_ltx2`: no_hit → pending. 출현/복제 표현 차이를 별개 사건으로 단정하지 않는다.
  다만 텍스트만으로 같은 여성의 잔인지 확정하지 않아 보류한다. 다른 남성의 잔을 설명한 C2는 불일치로 유지한다.

## 보류와 실행 한계

보류 원인은 겹치지 않도록 **채점 미완료 → 기존 검출 미완료 → 의미 불확실** 순서로 분류했다.

- 채점 미완료: 11개.
- 채점은 완료했으나 기존 검출 미완료: 6개.
- 실행·채점 완료 후 의미 불확실: 6개.

기존 검출 미완료 영상은 총 6개이며 분모에서 제외하지 않았다.
잘못된 원문 인용이나 서로 모순되는 판정 필드는 자동 수정하지 않는다.
각 단계의 형식 오류는 기존 정책에 따라 최대 1회 복구하며 실패하면 pending으로 남겼다.
결과가 원하는 판정과 다르다는 이유로 재호출하지 않았다.

| 채점 미완료 영상 | 상태 | 최종 사유 |
|---|---|---|
| sid_003_seedance | invalid_response | Entity separation requires explicitly different targets |
| sid_003_veo3 | invalid_response | Compatible description cannot assert conflict |
| sid_022_seedance | invalid_response | Reference event atoms must belong to claim |
| sid_033_ltx2 | invalid_response | Underspecified relation requires same target, evidence and uncertainty |
| sid_045_ltx2 | invalid_response | Underspecified relation requires same target, evidence and uncertainty |
| sid_122_ltx2 | invalid_response | Entity separation requires explicitly different targets |
| sid_154_ltx2 | invalid_response | Candidate event atoms must be exact source substrings |
| sid_158_ltx2 | invalid_response | Candidate event atoms must be exact source substrings |
| sid_158_seedance | invalid_response | Underspecified relation requires same target, evidence and uncertainty |
| sid_195_ltx2 | invalid_response | Candidate event atoms must be exact source substrings |
| sid_195_veo3 | invalid_response | Entity separation requires explicitly different targets |

## 재비교와 검증

첫 실행에서 인증 만료로 중단된 15개는 사용자 재인증 후 재개했다.
기존 완료 결과와 유효한 v6 단계만 재사용했으며, 형식 오류로 종료된 평가를 점수 개선 목적으로 재실행하지 않았다.
`auth_interrupted_pass/`에 중단 시점의 결과를 보존했다.

검토가 요청한 별도 재비교 단계는 0개다. 정상 완료 영상에서 재비교한 쌍은
0개이고, 초기 비긍정에서 유효한 긍정 대응으로 바뀐 쌍은 0개다.
쌍 수는 영상 수 또는 독립 사건 수가 아니다. 검토 단계만으로는 hit을 만들지 않았다.

전체 테스트 355개, Ruff, v4 독립성 검사 통과. v5 과거 점수도 보존 모듈로 재현했다.
소규모 합성 7개와 알려진 두 사례의 개발 검증을 먼저 수행했고, 정확한 같은 입력의 두 사례만
전체 실행에서 재사용했다. 따라서 이 60개 결과는 독립 홀드아웃 평가가 아니다.
원문·후보 불변, 모든 단계 입력/응답 계약·요청 해시와 집계를 재검증했다.

## 산출물

- 실행: `work/event_claims6_new60_20261106/`
- 로컬 검수: `~/TestCase/anomaly_benchmark/event_matching_v6_new60_20261106/index.html`
- 전후 비교: 같은 폴더 `summary.html`, `comparison.csv`
- 전체 근거: `evaluation.html`, `scorecard.json`, `evaluations/`, `details/`
- [구현 계약](EVENT_MATCHING_V6.md), [검증 요약](event_matching_v6_new60_validation_20261106.json)

라벨 밖 결함은 성공에 포함하지 않았다. 다음 검증에서는 남은 의미 보류와 응답 형식 실패를
분리해 검토하고, 새로운 SID의 독립 사례에서 과도한 의미 연결 여부를 확인해야 한다.
