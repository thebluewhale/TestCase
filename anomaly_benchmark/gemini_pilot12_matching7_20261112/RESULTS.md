# 기존 Gemini 단독 12개 · 의미 v7 비교 결과

- 이전 hit 8 / pending 4 → 현재 hit 10 / pending 2 / no_hit 0.
- 같은 v7 응답에서 새 허용을 끄면 hit 8개, 켜면 10개. 새 허용 규칙 의존 쌍 11개, 그 쌍에만 의존한 hit 영상 2개.
- 검출 호출 0회, 원본 R/C·후보 순서·bbox 고정.
- 채점 유효성: {'valid': 10, 'partial': 2}
- 새 규칙 의존 대응은 별도로 사람이 확인할 비교 결과이며 최종 정답이 아니다.
- 이전 v6 대비 변화는 새로운 모델 응답의 차이도 포함하며, 동일 v7 응답에서 허용을 끈 비교와 다르다.

| 영상 | 이전 v6 | 현재 v7 비교 | 채점 유효성 | 대응 쌍 | 새 허용 규칙 의존 쌍 | 새 허용 없이도 hit | 직전 결과 대비 새 대응 수 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| sid_013_ltx2 | pending | pending | 유효 |  | 없음 | False | 0 |
| sid_013_seedance | hit | hit | 유효 | R1–C5, R2–C1, R2–C3, R2–C4 | R2–C1, R2–C3, R2–C4 | True | 1 |
| sid_013_veo3 | hit | hit | 유효 | R2–C1, R2–C2, R2–C4, R3–C1, R3–C2, R3–C4 | 없음 | True | 3 |
| sid_040_ltx2 | hit | hit | 일부 유효 | R2–C2, R2–C3 | 없음 | True | 0 |
| sid_040_seedance | pending | hit | 유효 | R1–C1, R1–C3 | R1–C1, R1–C3 | False | 2 |
| sid_040_veo3 | hit | hit | 유효 | R3–C1, R3–C2, R3–C3, R4–C1, R4–C2 | R3–C1, R3–C2, R3–C3 | True | 0 |
| sid_053_ltx2 | hit | hit | 일부 유효 | R1–C3 | 없음 | True | 0 |
| sid_053_seedance | hit | hit | 유효 | R1–C3, R2–C3, R3–C3 | R2–C3 | True | 1 |
| sid_053_veo3 | hit | pending | 유효 |  | 없음 | False | 0 |
| sid_079_ltx2 | pending | hit | 유효 | R1–C1, R1–C3, R2–C1, R2–C3 | 없음 | True | 4 |
| sid_079_seedance | hit | hit | 유효 | R4–C3 | 없음 | True | 0 |
| sid_079_veo3 | pending | hit | 유효 | R1–C1, R1–C2 | R1–C1, R1–C2 | False | 2 |

실제 모델 대조 6/6 통과. 명시적 모순·다른 대상·별개 사건·근거 부족·대체 물체 부재를 명시한 반례 5개에서 hit 0. 일반 오탐률이나 독립 성능을 보장하지 않는다.

[영상 검수](index.html) · [결과표](summary.html) · [새 허용 규칙 의존 쌍](scope_extension_pairs.csv) · [평가 계약](EVENT_MATCHING_V7.md).

남은 pending: sid_013_ltx2, sid_053_veo3. sid_053_veo3는 동일 후보에 대한 새 채점 판단이 달라져 이전 hit에서 pending으로 바뀌었다. sid_079_ltx2는 새 응답의 검증 통과로 hit이 됐으며 새 허용 규칙 의존 영상이 아니다.

85% 목표에는 11/12가 필요하며 현재 비교 결과는 10/12(83.3%)다.

새 허용 규칙 의존 11쌍을 먼저 확인할 수 있다. CSV의 review_decision에 match/no_match/uncertain, review_note에 근거를 적을 수 있으며, 작성만으로 자동 판정을 바꾸지는 않는다.
