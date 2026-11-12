# Gemini / Claude 8fps 개발용 테스트

- 계획 12개, 실제 실행 12개. SID 013/040/053/079 × LTX-2/Seedance/Veo3.
- hit 2, pending 10, no_hit 0. 원본 라벨에 대응한 영상 기준이며 일반 정확도가 아니다.
- 유효 후보 출처별 라벨 대응 영상: {'gemini_visual': 4, 'claude_visual': 2, 'prompt': 0}.
- Claude structured outputs는 조직 정책상 사용하지 않았다. 일반 JSON을 로컬 검증했다.
- 전 단계 계약 점검의 좌표/정책 실패 기록은 diagnostics에 보존했다.
- 본 실험은 코드·자료·평가기 버전을 freeze.json에 동결했다. 정답 라벨은 검출 이후 채점에만 제공했다.
- 후보 합집합에서 완전히 같은 후보만 병합했다. 의미상 중복은 남아 있다.
- Gemini와 Claude가 공통 집중 구간을 공유하므로 모델별 후보 집계는 단독 파이프라인 성능이 아니다.
- 프롬프트 불일치는 별도 Gemini 검사이며 Claude 추가 효과와 구분한다.
- 일부 검사 미완료 시 라벨 대응 후보가 있어도 기존 채점 규칙은 최종 pending으로 집계한다. 출처별 대응 영상 수와 전체 hit 수가 다를 수 있다.
- 라벨 밖 실제 결함은 성공률에 더하지 않았다. 자동 미대응을 오검출로 단정하지 않는다.
- 4/12fps 비교 및 신규 60개 독립 평가는 아직 수행하지 않았다.
- 게이트 상태: {'passed': True, 'completed': 24, 'requested': 27}. 호출 수: {'gemini_detection': 70, 'claude_detection': 48, 'gemini_evaluation': 69}.
- 정상 완료가 아닌 모듈: {('claude-overview', 'invalid_response'): 2, ('claude', 'invalid_response'): 3, ('vertex-gemini', 'failed'): 3, ('vertex-gemini-prompt', 'failed'): 1}.

index.html은 상단 영상 matrix, 좌측 영상·bbox, 우측 R/C 텍스트를 제공한다.
summary.html은 출처별 비교표, comparison.csv는 같은 표의 다운로드용이다.
이전 사람이 작성한 검수 기록은 review_records에 보존했다.

요청·완료 단계 수, 토큰 사용량, 개별 실패 사유: [상세 실험 기록](EXPERIMENT.md).
12개 영상·bbox·모바일·링크 검증 완료. 이전 리포트는 삭제했고 사람 검수 기록은 해시 대조 후 보존했다.
