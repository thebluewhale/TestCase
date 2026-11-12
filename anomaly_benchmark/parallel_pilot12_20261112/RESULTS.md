# 기존 12개 결과의 집계 v2 적용

- hit 2→4, pending 10→8, no_hit 0. 모델 호출 없이 저장된 결과만 재집계했다.
- sid_013_veo3, sid_040_veo3: 의미 대응 있음 / 검출 부분 완료 / 채점 유효 / hit.
- 의미 기준과 R/C·시간·bbox를 바꾸지 않았다. 무효인 기본 비교 7개는 보류를 유지했다.
- 전체 검사 완료 4개·부분 완료 8개. 유효 채점 5개·무효 7개.
- 기존 기록은 history/aggregation_v1에, 기존 원시 응답은 evaluations/diagnostics에 보존했다.
- 이 영상들은 Claude 제거 전 병렬 실험이다. Gemini 단독 성능이나 일반 정확도로 해석하지 않는다.

[현재 집계 규칙](AGGREGATION_V2.md) · [당시 검출 실험 기록](EXPERIMENT.md) · [영상 검수](index.html).
