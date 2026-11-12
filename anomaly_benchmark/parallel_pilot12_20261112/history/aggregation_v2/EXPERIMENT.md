# Gemini / Claude 8fps 12개 개발용 실험 결과

2026-11-12. 사용자 재개 지시로 SID 013/040/053/079 × LTX-2/Seedance/Veo3 **12개를 실행**했다.
Gemini `gemini-3.8-flash`, Claude `claude-opus-4-8`, 전체 8fps·긴 집중 구간 12fps·최대 3개 구간이다.
일반 JSON 요청만 사용했으며 Claude provider-native structured outputs는 비활성화했다.

## 실행과 자동 채점

- 검출 실행 12/12개. 모든 검사 완료 4개, 부분 완료 8개.
- 의미 채점 상태: {'invalid_response': 7, 'completed': 5}.
- 최종 hit **2/12**, pending **10**, no_hit **0**. 85% 목표에 필요한 hit는 11개다.
- 원본 라벨 최소 하나와 대응하고 검출·채점 모두 완료한 경우만 최종 hit다. 부분 실행은 대응 후보가 있어도 pending이다.
- 출력/근거 검증 실패는 미검출로 확정하지 않는다. 이 작은 개발용 표본의 hit 비율은 서비스 정확도 추정이 아니다.
- 원본 라벨에 없는 결함은 성공에 더하지 않았다. 시간 일치는 보조 정보다. 사람 검증은 아직 하지 않았다.

| 관찰 경로 | 완료된 검사 단계 | 요청된 검사 단계 | 유효 후보가 원본 라벨과 대응한 영상 |
|---|---:|---:|---:|
| Gemini 시각 | 45 | 48 | 4 |
| Claude 시각 | 43 | 48 | 2 |
| 별도 Gemini 프롬프트 검사 | 11 | 12 | 0 |

출처별 대응 수는 **유효 의미 채점이 있는 결과만** 센다. 채점 미완료를 미대응으로 간주하면 안 된다.
동일한 집중 구간을 공유하므로 Gemini 단독/Claude 단독 파이프라인을 각각 재실행한 성능 비교가 아니다.
별도 프롬프트 후보는 Claude 추가 효과로 계산하지 않는다. 모델 합의나 후보 수 증가는 정답 보증이 아니다.

| 영상 | Gemini 시각 후보 | Claude 시각 후보 | 프롬프트 후보 | 검출 완료 | 의미 채점 | 최종 상태 |
|---|---:|---:|---:|---|---|---|
| sid_013_ltx2 | 4 | 3 | 0 | False | invalid_response | pending |
| sid_013_seedance | 8 | 8 | 2 | False | invalid_response | pending |
| sid_013_veo3 | 6 | 7 | 0 | False | completed | pending |
| sid_040_ltx2 | 6 | 4 | 0 | True | invalid_response | pending |
| sid_040_seedance | 6 | 4 | 0 | False | invalid_response | pending |
| sid_040_veo3 | 7 | 6 | 0 | False | completed | pending |
| sid_053_ltx2 | 7 | 1 | 2 | True | completed | hit |
| sid_053_seedance | 3 | 8 | 1 | False | invalid_response | pending |
| sid_053_veo3 | 8 | 1 | 0 | True | completed | hit |
| sid_079_ltx2 | 8 | 8 | 0 | True | invalid_response | pending |
| sid_079_seedance | 4 | 0 | 0 | False | completed | pending |
| sid_079_veo3 | 6 | 5 | 0 | False | invalid_response | pending |

## 실패 기록

검출기·채점기를 실험 도중 변경하거나, 원하는 판정이 나올 때까지 재호출하지 않았다.

- `sid_013_ltx2` / claude-overview / overview: invalid_response — Claude output validation failed
- `sid_013_ltx2` / claude-focus-1 / focus-1: invalid_response — Claude output validation failed
- `sid_013_ltx2` / 의미 채점: invalid_response — Candidate event atoms must be exact source substrings
- `sid_013_seedance` / claude-focus-0 / focus-0: invalid_response — Claude output validation failed
- `sid_013_seedance` / 의미 채점: invalid_response — Pair evidence must belong to a selected claim
- `sid_013_veo3` / vertex-gemini / overview: failed — Provider transport failure/timeout
- `sid_040_ltx2` / 의미 채점: invalid_response — Candidate event atoms must be exact source substrings
- `sid_040_seedance` / vertex-gemini / overview: failed — Provider transport failure/timeout
- `sid_040_seedance` / 의미 채점: invalid_response — Pair evidence must belong to a selected claim
- `sid_040_veo3` / claude-overview / overview: invalid_response — Claude output validation failed
- `sid_053_seedance` / vertex-gemini / focus-1: failed — Provider transport failure/timeout
- `sid_053_seedance` / 의미 채점: invalid_response — Candidate event atoms must be exact source substrings
- `sid_079_ltx2` / 의미 채점: invalid_response — Candidate event atoms must be exact source substrings
- `sid_079_seedance` / vertex-gemini-prompt / None: failed — Provider transport failure/timeout
- `sid_079_veo3` / claude-focus-0 / focus-0: invalid_response — Claude output validation failed
- `sid_079_veo3` / 의미 채점: invalid_response — Entity separation requires explicitly different targets

## 사용량·지연·재현

재개부터 집계까지 약 96.3분. 로컬 전처리·대기·재시도·채점·후처리를 포함하므로 모델 호출 시간의 합과 다르다.

- gemini: 실제 요청 139회, 전송 실패 13회, 요청 지연 중앙값 10.444초. 사용량: `{'promptTokenCount': 1761947, 'candidatesTokenCount': 225010, 'totalTokenCount': 1986957}`. 성공 응답에도 로컬 검증 탈락이 포함된다.
- claude: 실제 요청 48회, 전송 실패 0회, 요청 지연 중앙값 14.560초. 사용량: `{'input_tokens': 1459320, 'output_tokens': 29781, 'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 0}`. 성공 응답에도 로컬 검증 탈락이 포함된다.

사용량은 응답에 반환된 토큰만 합산했다. 타임아웃 요청의 공급자 측 처리·과금 여부는 이 기록으로 확정할 수 없다. 요금 금액은 계산하지 않았다.
`work/parallel_pilot12_20261112/`의 `freeze.json`에 입력 SHA·설정·코드 해시·평가기 버전이 있다.
원본 라벨은 검출 후 별도 채점에만 전달했다. `call_records/`, `reports/`, `evaluations/`에 원시 근거·재시도를 보존했다.

오프라인 검수 화면: `~/TestCase/anomaly_benchmark/parallel_pilot12_20261112/index.html`.
상단 12개 matrix, 좌측 영상·시간 연동 bbox, 우측 R/C·후보 출처·실패 사유를 제공한다.
`summary.html`/`comparison.csv`에서 출처별 후보와 라벨 대응을 비교한다. 이전 사람 검수 기록은 `review_records/`에 보존한다.

## 다음 비교의 조건

먼저 출력 계약 실패·타임아웃·채점 근거 검증 실패를 별도로 분석하고, 실패 개선은 새 코드 버전과 새 실행으로 기록해야 한다.
같은 입력·관찰 예산에서 Gemini 단독과 병렬 구성을 대조하고, 4/8/12fps 비교를 별도 수행한다.
이후 미사용 독립 사례에서 검증해야 하며, 이번 12개만으로 8fps나 병렬 구성을 최종 채택하지 않는다.
신규 60개 평가와 FPS 비교는 이번 실행에 포함하지 않았다.

## 리포트 검증

12개 원본 영상의 복사 해시, 영상 재생·시점별 bbox·모바일 레이아웃·비교표·로컬 링크를 검증했다. 후보 135개 중 102개에 bbox가 있으며 33개는 좌표 없이 시간·설명만 제공한다. 최신 리포트만 남겼고 이전 사람 검수 기록 두 파일을 해시 대조해 보존했다.

첫 집계 렌더에서 과거 비교값 `previous_automatic_hit` 누락으로 실패했으나, 비교 대상 없음(`null`)을 메타데이터에 보완해 저장된 채점 결과만으로 재생성했다. 모델 재호출이나 판정 변경은 하지 않았다.
