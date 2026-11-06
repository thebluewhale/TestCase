# 기존 60개 사건 의미 매칭 v3 재채점 결과

동결된 동일 60개 영상의 기존 검출 결과를 `event-claims-3`로 재채점했다. 자동 성공은 **30/60 (50.0%)**, 보류 15개, 미대응 15개다.
1단계 85% 목표에는 51개 성공이 필요하다. 목표 미달이다. 전체 분모는 실패·보류를 포함해 60개로 유지했다.

## 이전 평가와 비교

| 기준 | 성공 영상 |
|---|---|
| 기존 v1 자동 대응 | 17/60 |
| v2 의미 + 시간 조건 | 26/60 |
| v2 의미 대응 진단 | 30/60 |
| v3 의미 대응, 시간은 보조 | 30/60 |

영상 탐지 결과는 바꾸지 않았다. 따라서 증가/감소는 검출 성능 향상 자체가 아니라 평가 방식 변경에 따른 결과다. 라벨 밖 관측을 새 정답으로 추가하지 않았다. 원본 R의 이상 증상 의미 대응만 집계한다.

| 생성 모델 | 영상 | v2 hit | v3 hit | 보류 | 미대응 |
|---|---:|---:|---:|---:|---:|
| ltx2 | 20 | 9 | 9 | 8 | 3 |
| seedance | 20 | 8 | 12 | 3 | 5 |
| veo3 | 20 | 9 | 9 | 4 | 7 |

## 변화한 영상

- v2 성공 기준 대비 새 hit 8개: sid_013_seedance, sid_013_veo3, sid_040_seedance, sid_072_ltx2, sid_090_ltx2, sid_141_veo3, sid_172_seedance, sid_173_seedance
- v2 성공 기준 대비 hit 제외 4개: sid_024_ltx2, sid_038_veo3, sid_041_ltx2, sid_111_veo3
- v2 의미 진단 대비 새 hit 4개: sid_040_seedance, sid_072_ltx2, sid_141_veo3, sid_173_seedance
- v2 의미 진단 대비 hit 제외 4개: sid_024_ltx2, sid_038_veo3, sid_041_ltx2, sid_111_veo3

## 실행과 해석 범위

- 채점 상태: {'completed': 58, 'invalid_response': 2}. 동일 최종 프롬프트의 성공 10개 재사용, 나머지 50개 평가.
- 모델: Vertex AI gemini-3.8-flash. 새 호출 시도 59회. 영상 탐지 호출 0회.
- 원본 탐지/영상 해시·전체 목록·모델/요청 설정을 대조했다. v2 결과와 개발 보정 첫 시도는 별도로 보존했다.
- 지정한 사람 보정 그룹: 6/6 대응. 이미 본 개발 사례이며 독립 검증이 아니다.
- pending은 의미 불확실성 또는 탐지/평가 미완료로 확정하지 못한 상태다. 라벨 밖 정탐을 뜻하지 않는다.
- 시간 차이·시간 비교 불가 자체로는 hit을 취소하지 않는다. 시간 포함 대응 수는 진단값이다.
- 사람이 전체 새 R–C 판정을 확인한 결과나 정밀도/재현율 추정으로 해석하지 않는다. 미사용 SID 그룹의 독립 검증은 후속 작업이다.

## 열람 파일

- `index.html`: 60개 영상별 의미 대응과 R–C 상세
- `comparison.csv`: 이전 v1/v2와 새 v3 결과의 영상별 비교
- `videos.csv`, `pairs.csv`, `claims.csv`: 새 평가의 영상/대응/라벨 증상 근거
- `evaluations/`: 모델 원본 응답
- `validation.json`: 실행·비교 검증 기록

## 영상별 요약

| 영상 | v2 상태 | v3 상태 | 시간 보조 | 인정 R–C |
|---|---|---|---|---|
| sid_013_ltx2 | hit | hit | 시간도 일치 | R2-C3 |
| sid_013_seedance | pending | hit | 시간 차이 있음 | R2-C1; R2-C4 |
| sid_013_veo3 | pending | hit | 시간 차이 있음 / 시간도 일치 | R2-C1; R2-C3; R3-C1; R3-C3 |
| sid_016_ltx2 | pending | pending | 의미 대응 없음 | 없음 |
| sid_016_seedance | pending | pending | 의미 대응 없음 | 없음 |
| sid_016_veo3 | pending | pending | 의미 대응 없음 | 없음 |
| sid_024_ltx2 | hit | pending | 의미 대응 없음 | 없음 |
| sid_024_seedance | hit | hit | 시간도 일치 | R1-C1; R1-C3; R2-C4; R3-C1; R3-C3 |
| sid_024_veo3 | hit | hit | 시간도 일치 | R2-C1 |
| sid_038_ltx2 | pending | pending | 의미 대응 없음 | 없음 |
| sid_038_seedance | no_hit | no_hit | 의미 대응 없음 | 없음 |
| sid_038_veo3 | hit | pending | 의미 대응 없음 | 없음 |
| sid_040_ltx2 | hit | hit | 시간도 일치 | R2-C2; R2-C3 |
| sid_040_seedance | no_hit | hit | 시간 차이 있음 / 시간도 일치 | R1-C1; R1-C3; R2-C1; R2-C3 |
| sid_040_veo3 | hit | hit | 시간 차이 있음 / 시간도 일치 | R2-C2; R2-C3; R3-C1; R3-C2; R3-C3; R4-C2; R4-C3 |
| sid_041_ltx2 | hit | pending | 의미 대응 없음 | 없음 |
| sid_041_seedance | no_hit | no_hit | 의미 대응 없음 | 없음 |
| sid_041_veo3 | hit | hit | 시간도 일치 | R1-C2; R1-C4; R2-C4; R3-C2 |
| sid_054_ltx2 | pending | pending | 의미 대응 없음 | 없음 |
| sid_054_seedance | hit | hit | 시간도 일치 | R1-C2; R2-C3; R2-C4 |
| sid_054_veo3 | no_hit | no_hit | 의미 대응 없음 | 없음 |
| sid_069_ltx2 | no_hit | no_hit | 의미 대응 없음 | 없음 |
| sid_069_seedance | hit | hit | 시간도 일치 | R2-C4 |
| sid_069_veo3 | no_hit | no_hit | 의미 대응 없음 | 없음 |
| sid_072_ltx2 | pending | hit | 시간도 일치 | R2-C2 |
| sid_072_seedance | hit | hit | 시간도 일치 | R1-C1; R2-C2 |
| sid_072_veo3 | no_hit | no_hit | 의미 대응 없음 | 없음 |
| sid_082_ltx2 | pending | pending | 의미 대응 없음 | 없음 |
| sid_082_seedance | pending | pending | 의미 대응 없음 | 없음 |
| sid_082_veo3 | hit | hit | 시간 차이 있음 / 시간도 일치 | R1-C2; R5-C3 |
| sid_090_ltx2 | pending | hit | 시간 차이 있음 | R2-C2 |
| sid_090_seedance | hit | hit | 시간도 일치 | R2-C4 |
| sid_090_veo3 | hit | hit | 시간도 일치 | R1-C3 |
| sid_111_ltx2 | pending | pending | 의미 대응 없음 | 없음 |
| sid_111_seedance | hit | hit | 시간도 일치 | R4-C3; R4-C5 |
| sid_111_veo3 | hit | pending | 의미 대응 없음 | 없음 |
| sid_119_ltx2 | hit | hit | 시간도 일치 | R1-C1; R1-C2 |
| sid_119_seedance | no_hit | no_hit | 의미 대응 없음 | 없음 |
| sid_119_veo3 | no_hit | no_hit | 의미 대응 없음 | 없음 |
| sid_128_ltx2 | hit | hit | 시간도 일치 | R1-C2; R1-C4 |
| sid_128_seedance | hit | hit | 시간도 일치 | R2-C4 |
| sid_128_veo3 | no_hit | no_hit | 의미 대응 없음 | 없음 |
| sid_141_ltx2 | hit | hit | 시간도 일치 | R3-C1; R3-C2 |
| sid_141_seedance | pending | pending | 의미 대응 없음 | 없음 |
| sid_141_veo3 | no_hit | hit | 시간 차이 있음 | R2-C2 |
| sid_172_ltx2 | hit | hit | 시간도 일치 | R2-C1; R2-C2 |
| sid_172_seedance | pending | hit | 시간 차이 있음 | R2-C2 |
| sid_172_veo3 | hit | hit | 시간도 일치 | R3-C1; R3-C3 |
| sid_173_ltx2 | hit | hit | 시간도 일치 | R5-C2 |
| sid_173_seedance | no_hit | hit | 시간도 일치 | R1-C2 |
| sid_173_veo3 | hit | hit | 시간도 일치 | R1-C4 |
| sid_176_ltx2 | pending | pending | 의미 대응 없음 | 없음 |
| sid_176_seedance | no_hit | no_hit | 의미 대응 없음 | 없음 |
| sid_176_veo3 | pending | pending | 의미 대응 없음 | 없음 |
| sid_178_ltx2 | no_hit | no_hit | 의미 대응 없음 | 없음 |
| sid_178_seedance | hit | hit | 시간도 일치 | R2-C3 |
| sid_178_veo3 | no_hit | no_hit | 의미 대응 없음 | 없음 |
| sid_198_ltx2 | no_hit | no_hit | 의미 대응 없음 | 없음 |
| sid_198_seedance | no_hit | no_hit | 의미 대응 없음 | 없음 |
| sid_198_veo3 | no_hit | no_hit | 의미 대응 없음 | 없음 |


## 보류와 감소 원인

이전 v2 성공에서 제외된 4개 중 sid_024_ltx2·sid_041_ltx2는 의미 불일치 확정이 아니라
**채점 응답 오류**다. 각 응답은 선택한 증상의 원문 범위를 벗어난 인용 근거로 검증에 실패했다.
최초 형식 재요청과 별도 재시도에서도 해결되지 않아 성공으로 집계하지 않았다.
sid_038_veo3·sid_111_veo3는 새 의미 판단에서 보류로 바뀌었다. 사람 대응과의 차이를 우선 재검토할 대상이다.
현재 결과만으로 평가기 정확도가 개선됐다고 결론 내리지 않는다.

| 보류 영상 | 원인 |
|---|---|
| sid_016_ltx2 | 의미 대응 불확실 |
| sid_016_seedance | 의미 대응 불확실 |
| sid_016_veo3 | 기존 탐지 미완료 |
| sid_024_ltx2 | 채점 응답 근거 검증 오류 |
| sid_038_ltx2 | 의미 대응 불확실 |
| sid_038_veo3 | 의미 대응 불확실 |
| sid_041_ltx2 | 채점 응답 근거 검증 오류 |
| sid_054_ltx2 | 기존 탐지 미완료 |
| sid_082_ltx2 | 의미 대응 불확실 |
| sid_082_seedance | 의미 대응 불확실 |
| sid_111_ltx2 | 기존 탐지 미완료 |
| sid_111_veo3 | 의미 대응 불확실 |
| sid_141_seedance | 기존 탐지 미완료 |
| sid_176_ltx2 | 의미 대응 불확실 |
| sid_176_veo3 | 의미 대응 불확실 |
