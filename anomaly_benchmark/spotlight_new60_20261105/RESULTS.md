# 신규 60개 영상 평가 결과

자동 라벨 대응 hit **20/60 (33.3%)**, pending 20, no_hit 20.
이 비율은 검출 정확도가 아니다. 프롬프트 준수·의도 모호성·검출 범위 차이·실행 실패·라벨 누락을 모두 설명하는 지표가 아니며, 사람 검증 전 자동 평가다.
목표는 51/60(85%)이며 자동 수치 기준 미달이다.

| 생성 모델 | 영상 | hit | pending | no_hit |
|---|---:|---:|---:|---:|
| ltx2 | 20 | 10 | 7 | 3 |
| seedance | 20 | 4 | 8 | 8 |
| veo3 | 20 | 6 | 5 | 9 |

## 표본과 평가 조건

- 기존 개발 60개와 SID·영상·파일 해시가 겹치지 않는 20개 신규 그룹. 생성 모델별 20개. 고정 해시 순서와 출처별 층화로 선정했다.
- 제작 프롬프트·정답 라벨 없이 combined + focused 영상 검출을 실행한 후 원본 라벨과 대조했다. 모델은 gemini-3.8-flash 단독이다.
- 기존과 같은 event-claims-3 기준: 원본 라벨의 이상 증상 하나 이상에 의미 대응하면 hit. 시간은 보조 표시이며 라벨 밖 관측을 성공에 추가하지 않는다.
- 결과를 보고 사례를 교체하거나 임계값/프롬프트를 조정하지 않았다. 기존 60개는 개발 보정, 이번 60개는 새 SID 그룹의 고정 설정 첫 평가이며 서로 다른 표본이다.
- 이번 SID 그룹은 이후 미사용 holdout으로 취급하지 않는다. 사용자 검토 후 튜닝에 사용하면 개발 자료로 표시한다.
- 검출 상태: {'baseline_completed': 53, 'focused_completed': 52, 'baseline_invalid_response': 7, 'focused_not_run': 7, 'focused_failed': 1}
- 채점 상태: {'completed': 60}
- 검출 호출 시도 116회, 채점 호출 시도 62회. 모든 미완료/보류는 분모 60개에 남긴다.

## 기존 60개와 비교

| 표본 | hit | pending | no_hit |
|---|---:|---:|---:|
| 기존 개발 60개 | 30 | 15 | 15 |
| 신규 60개 | 20 | 20 | 20 |

같은 영상의 전후 비교가 아니므로 이 차이를 검출 성능 향상/악화의 인과 증거로 해석하지 않는다.

## 보류 사유

| 영상 | 사유 |
|---|---|
| sid_003_seedance | 의미 대응 불확실 |
| sid_007_ltx2 | 의미 대응 불확실 |
| sid_007_seedance | 의미 대응 불확실 |
| sid_022_seedance | 검출 미완료: baseline: invalid_response Candidate interval outside source timeline / focused: not_run baseline_incomplete |
| sid_033_ltx2 | 의미 대응 불확실 |
| sid_045_ltx2 | 의미 대응 불확실 |
| sid_045_seedance | 검출 미완료: baseline: invalid_response Candidate interval outside source timeline / focused: not_run baseline_incomplete |
| sid_045_veo3 | 검출 미완료: baseline: invalid_response bbox must be normalized display xyxy; never silently clipped / focused: not_run baseline_incomplete |
| sid_053_veo3 | 검출 미완료: baseline: invalid_response bbox must be normalized display xyxy; never silently clipped / focused: not_run baseline_incomplete |
| sid_091_ltx2 | 의미 대응 불확실 |
| sid_117_veo3 | 의미 대응 불확실 |
| sid_153_veo3 | 검출 미완료: baseline: invalid_response bbox must be normalized display xyxy; never silently clipped / focused: not_run baseline_incomplete |
| sid_157_ltx2 | 의미 대응 불확실 |
| sid_157_seedance | 검출 미완료: baseline: invalid_response bbox must be normalized display xyxy; never silently clipped / focused: not_run baseline_incomplete |
| sid_158_ltx2 | 의미 대응 불확실 |
| sid_158_seedance | 의미 대응 불확실 |
| sid_158_veo3 | 의미 대응 불확실 |
| sid_184_seedance | 검출 미완료: focused: failed Provider HTTP 429 |
| sid_195_ltx2 | 의미 대응 불확실 |
| sid_195_seedance | 검출 미완료: baseline: invalid_response Candidate interval outside source timeline / focused: not_run baseline_incomplete |
