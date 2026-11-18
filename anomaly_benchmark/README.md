# 객체 소실·급변 기준선 리포트

이번 평가의 결과·영상·라벨·API 응답·검수 근거를 모은 사본입니다. 기존 데이터는 이번 자료로 교체했습니다.

- **먼저 보기:** [index.html](index.html) — 21개 영상과 각 검수 리포트. 같은 대상의 정상 대조로 이동할 수 있습니다.
- [결과 보고서](benchmarks/reports/OBJECT_COMPARISON_2026-11-18.md)
- [평가셋 설명](benchmarks/object_temporal/comparison_v1/README.md)
- [실측 요약 JSON](summary.json), [고정 계획](plan.json), [설정](config.json)
- `videos/`: LaSOT 원본 3개와 합성 정상 10개·결함 8개
- `labels/`: 합성 영상의 프레임별 시각·영역·가시성
- `reports/`: 영상별 HTML/JSON·원본 근거·무결성 manifest
- `api/`: 실제 추적 API 응답과 요청 기록
- `benchmarks/`: 저장소에 보관한 평가셋 메타데이터·보고서·검증 기록

합성 결함의 후보 검출은 4/8, 기대 유형까지 일치는 3/8입니다. 정상 대조 10개에는 후보가 없었지만
3개는 판단 불가입니다. 실제 AI 생성 결함 성능 또는 정상 인증을 의미하지 않습니다.

문서에 기재된 `work/object-comparison-2026-11-18/`은 개발 저장소의 원래 경로입니다.
이 사본에서는 이 디렉터리 자체가 실행 자료의 루트입니다. HTML의 상대 경로를 유지하려면 전체를 함께 옮기세요.
