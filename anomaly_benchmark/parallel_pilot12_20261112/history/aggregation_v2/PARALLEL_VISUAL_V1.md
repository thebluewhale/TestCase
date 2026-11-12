# Gemini / Claude 병렬 시각 관찰 v1

2026-11-12. 코드·로컬 모의 응답 검증 완료. Claude 일반 JSON 호출은 한 영상에서 응답 형식까지 점검했다. 기존 12개 영상의 8fps 병렬 벤치마크와 의미 채점을 실행했다. 전체 검사 완료 4개, 부분 완료 8개; 최종 hit 2 / pending 10 / no_hit 0다. 실패·미채점을 포함하므로 정확도 추정으로 사용하지 않는다. [실험 결과](PARALLEL_PILOT12_RESULTS_20261112.md).
모든 구현은 v4 내부에 있으며 다른 anomaly 버전을 가져오지 않는다.

## 실행

`backend/review_anomaly_v4`에서 실행한다. 새 출력 디렉토리를 사용한다.

```bash
.venv/bin/anomaly-v4 poc /path/to/video.mp4 \
  --output work/parallel-example \
  --profile combined --vertex-project YOUR_PROJECT \
  --vlm-mode gemini-claude --claude-fps 8 --focus-fps 12
```

- Gemini: 기존 Vertex `gemini-3.8-flash` 영상 입력. `gemini-4-argon` 금지 정책 유지.
- Claude: Vertex `publishers/anthropic/models/claude-opus-4-8:rawPredict`, 모델 fallback 없음.
  `--claude-project` 미지정 시 Gemini 프로젝트를 사용한다. `--claude-location global` 기본,
  `us`/`eu`도 명시할 수 있다. 기존 gcloud 로그인 토큰 경로를 사용하며 키/토큰은 저장하지 않는다.
  동일 프로젝트에서 Gemini가 된다고 Claude 이용 권한도 확인된 것은 아니다.
- `--vlm-mode gemini`는 기존 Gemini 단독 경로다. 단독 모드의 `--focus-review`는 기존 구간당 네 시점 검토다.
- `gemini-claude` 모드는 전체 탐색과 집중 검토를 모두 실행한다. `--focus-review`를 추가할 필요가 없다.
  `--profile vlm`이면 로컬 측정 없이 두 모델을 관찰하며, `vbench` 단독에서는 병렬 모드를 사용할 수 없다.
- 생성 프롬프트 검사는 기존 `--generation-prompt-file`로 별도 수행한다. 이번 병렬화에 포함되지 않는다.
- `benchmark-run --scope temporal_poc --vlm-mode gemini-claude --profiles combined ...`에도 연결했다.
  개발 split·명시적 asset ID 제한을 유지한다. 여러 profile에 `vbench`가 있으면 해당 실행에서는 VLM을 호출하지 않는다.
  CLI 연결을 검증했다. 현재 데이터셋 실험은 동결 기록을 남기는 별도 `work/parallel_pilot12_20261112/run.py`에서 실행한다.

## 사내 조직 정책과 실행 이력

Claude의 provider-native structured outputs는 `constraints/vertexai.allowedPartnerModelFeatures`에 의해
HTTP 400으로 거절되었다. 사용자도 해당 기능을 사용할 수 없음을 확인했다.
`structured_output` 설정은 제거했으며, `output_config`/`output_format`/`response_format` 및
`tools`/`tool_choice`를 전송 함수에 넣으면 HTTP 호출 전에 거부한다. 자동 활성화/fallback은 없다.

일반 이미지 분석 요청에 JSON 형식을 텍스트로 안내하고, 반환 텍스트를 파싱해 로컬 후보 계약으로 검증한다.
텍스트에 적힌 JSON 스키마는 모델에 대한 형식 지시이며 API의 structured outputs 기능이 아니다.
bbox는 0~1 원본 화면 비율이라는 예시·범위를 이미지 전후 지시에 넣는다. 출력 좌표를 픽셀이나 0~1000으로
반환하면 자동 나눗셈 없이 거부하며, 기존 bbox 재시도는 최대 1회만 허용한다.

실행 이력은 `work/parallel_pilot12_20261112/`에 보존했다.
- `claude_probe`: 첫 계약 점검. 일반 JSON 응답의 bbox가 픽셀값이어서 두 시도 모두 거부됨.
- `claude_probe_schema2`: 구조화 출력 기능 점검 1회가 조직 정책으로 거절됨.
- `claude_probe_json2`: 금지 기능 없이 지시를 보강한 일반 JSON 호출 1회에서 후보 2개의 형식 검증 통과.
  후보가 실제 결함이거나 정답 라벨과 일치한다는 성능 검증은 아니다.
- `previous_stop_record.json`: 이전 사용자 중단 기록을 보존했다. `resume_record.json`에 새 재개 지시와 시점을 기록했다. 실행기는 `STOPPED_BY_USER.json`이 존재하면 시작하지 않는다.

SID 013/040/053/079 × LTX-2/Seedance/Veo3, 총 12개를 실행했다. 3개 점검에서 요청 모듈 27개 중 24개 완료로 사전 확대 기준(80% 이상, 접근/정책 차단 없음)을 통과했다. 이는 응답 안정성 기준이며 검출 성능 목표가 아니다. 검출 이후 원본 라벨로 별도 의미 채점을 실행했다. 신규 60개나 FPS 비교는 이번 실행에 포함하지 않는다.
새 결과 내보내기와 12개 영상·bbox·모바일 화면·로컬 링크 검증을 마친 뒤 이전 리포트를 삭제했다. 최신 `parallel_pilot12_20261112` 폴더만 남겼으며, 기존 사람 검수 기록 두 파일은 해시 대조 후 보존했다.
실제 거절된 범위는 Claude 파트너 모델의 구조화 출력 기능이다. 기존 Gemini 요청 계약은 이번 변경 범위에서 유지한다.

## 프레임과 집중 검토

`visual_frames.Config`에 설정을 보존한다. 전체 추출은 **8fps**, 긴 집중 구간은 **12fps**가 초기값이다.
4·8·12fps를 비교해 최적값을 결정해야 하며, Gemini 단독/병렬 채택 여부도 성과·비용으로 재결정한다.
15초 영상의 8fps 입력은 약 **120장**이다. 마지막 원본 프레임을 포함하면서 121장이 될 수 있다.
원본 PTS에서 표본을 선택하고 중복된 프레임 ID를 제거한다. 프레임을 보간·복제하지 않는다.
추출 이미지의 원본 ID·PTS/time_base·실제 시각·해시·크롭 영역·입력 해상도를 기록한다.

1. 로컬 측정 → Gemini → Claude 순으로 각 출처의 후보를 하나씩 번갈아 고려한다.
   대상이 중복되는 시간/공간 구간은 추가 검토에서 제외하고, 최대 3개 구간을 선정한다.
   남는 자리는 측정 trace와 균등 시점으로 보완한다. 모델의 숫자 신뢰도로 출처 간 우열을 정하지 않는다.
   원본 후보는 삭제하지 않으며, 미선정 사유/원본 구간을 `selection.json`에 남긴다.
2. 원래 후보 구간이 2초보다 길면 중앙 2초를 집중 구간으로 삼고 `interval_trimmed`를 남긴다.
   사건의 모든 순간을 재검토한 것으로 해석하지 않는다. 이 선택 정책도 후속 비교 대상이다.
3. 집중 구간이 1초 이하면 그 안의 **모든 원본 프레임**, 그보다 길면 12fps를 사용한다.
   전후 0.5초 맥락은 4fps로 보완한다. 원본 fps가 높아 예산을 넘으면 미완료로 기록한다.
4. 전체 화면과 고정 영역/배율 크롭을 두 모델에 동일하게 제공한다. 각 이미지의 긴 변은 최대 1024px,
   JPEG quality 95이며 확대·합성하지 않는다. 입력 압축/축소는 세밀한 깜빡임 판정에 한계가 있다.
   Gemini에는 전체 영상도 추가되므로 두 모델의 전체 관측 조건이 동일한 것은 아니다.
5. 두 모델에 상대 응답 설명·원본 정답 라벨을 전달하지 않는다. 구간과 영역 선정 자체는 앞 단계 관찰에
   의존하므로 재검토 결과를 통계적으로 독립된 증거로 취급하지 않는다.

## 예산과 실패

- 전체 탐색 2개 호출을 병렬로 실행한다. 집중 구간은 순차 처리하며 각 구간에서 2개 모델을 병렬 호출한다.
  최초 요청은 영상당 최대 8개(전체 2 + 집중 3×2), 프롬프트 검사와 재시도는 별도다.
- 전체 프레임 최대 361장, 집중 구간 최대 90개 원본 시점/180개 이미지. 초과 시 조용히 누락하지 않고
  `budget_exceeded`와 부분 실행을 기록한다. `visual_frames.Config`로 더 낮은 예산도 설정할 수 있다.
- Gemini 기존 단독 집중 입력은 최대 24장 그대로다. 병렬 집중 경로에서만 최대 180장으로 명시 확장하며
  기존 16MiB 이미지 바이트 제한을 유지한다. Claude는 자체 요청 본문 20MiB/개별 base64 이미지 5MiB 예산을 둔다.
  이 값은 API가 항상 수락한다는 보장이 아니며 실제 공급자 제한도 실호출에서 확인한다.
- Claude HTTP 429/5xx·전송 실패는 최대 3회 시도(15/30초 대기), 401/403/404·거절·일반 형식 오류는 자동 재시도하지 않는다.
  bbox 오류는 기존 정책과 같이 **1회만** 동일 요청으로 재시도하고 그 요청이 다시 실패하면 종료한다.
  좌표를 /1000으로 자동 보정하지 않는다. 시간 경계 0.33초 허용과 원본/보정 이력도 공통 후보 계약을 사용한다.
- 한 모델 실패 시 다른 모델 결과를 유지하고 `execution_complete=false`로 남긴다. 빈 정상 응답과 실패는 다르다.
  인증 실패·권한 거부를 다른 모델로 대체하지 않는다. 원본 근거 훼손은 입력 오류로 중단한다.

## 후보와 리포트

- 유효 후보의 합집합을 유지한다. 설명·대상·시간·좌표 등 후보 필드가 **완전히 같은 경우만** 묶으며,
  원본 모델·단계별 기록은 `source_records`에 보존한다. 의미가 유사한 후보 자동 통합은 아직 하지 않는다.
- 모델 동의를 결함 확정으로 사용하지 않는다. 설명·좌표를 평균 내거나 근거 없는 통합 서술을 만들지 않는다.
- 측정 제안은 계속 `measurement_proposal`이며 원본 라벨 hit 대상이 아니다. `manual_review`에 시간·bbox와
  `not_selected`/`completed_review`/`review_incomplete`를 남기고 HTML에서도 상태를 표시한다.
  `completed_review`는 두 모델 요청 완료를 뜻하며 증상 확인을 뜻하지 않는다. 근처에 모델 후보가 생겨도
  같은 결함임을 자동 확정하지 않는다. 구체적 후보는 별도 C로 남긴다.
- Claude 이미지 자료는 `frame_submission`, 기존 영상 자료는 `submission`으로 구분해 영상 재생·평가 호환성을 유지한다.
- 모델별/시도별 원시 응답·사용량·지연·요청 해시와 근거를 보존한다. 전체 지연은 병렬 호출 시간의 합이 아닌
  벽시계 시간이다. 비용 금액은 요율 미설정으로 null이며 토큰 수로 추후 산출한다.

## 검증과 다음 실험

`tests/test_parallel_visual.py`는 실제 네트워크 대신 모의 응답으로 다음을 확인한다:
8fps/가변 PTS/저fps 중복 방지, 짧은 구간 원본 연속 프레임, 고정 크롭, 구간 예산/미선정 이력,
두 호출의 동시 실행, 집중 입력 이미지의 byte 일치, 상대 모델 설명 미전달, 후보 합집합,
인증·HTTP·거절·출력 오류와 bbox 1회 재시도, 한 모델 실패 시 리포트 생성, 수동 확인 상태, CLI 설정.
모의 응답 검증은 실제 Claude의 영상 이해 성능을 입증하지 않는다. 별도 일반 JSON 계약 점검의 범위는 위 실행 이력과 같다.

현재 12개 실험에서는 입력 SHA·코드 해시·설정·평가기 버전을 동결하고, 유효 후보의 출처별 원본 라벨 대응을 집계한다. 이는 공통 집중 구간에서의 기여도이며 Gemini 단독 경로를 다시 실행한 대조군이 아니다.
4·8·12fps 비교와 모델 구성 비교를 분리하고, 라벨 대응 영상 H/N·사람 확인 후보 타당성/오검출·중복·실패율·
비용·전체 시간을 비교한다. 기존 단독 경로와 병렬 경로는 집중 관찰 밀도도 다르므로 단순 결과 차이를
Claude 추가만의 효과로 해석하지 않는다. 같은 공통 근거에서의 모델별 원시 결과 비교와 전체 경로 비교를 구분한다.

참고: [Claude Google Cloud 호출 계약](https://platform.claude.com/docs/en/build-with-claude/claude-models-on-google-cloud/google-managed),
[Claude 이미지 입력](https://platform.claude.com/docs/en/build-with-claude/vision).
