# SPOTLIGHT 30개 영상 POC 결과 모음

[index.html](index.html)을 열면 원본 라벨과 POC 검출 후보 비교표로 이동합니다.

- Seedance / Veo3 / LTX-2 각각 10개, 같은 프롬프트 그룹 10개.
- 기존 12개 결과 재사용 + 신규 18개 검사, 좌표 오류 2건 별도 재실행.
- 최종 실행 완료 29개, 부분 실행 1개(`sid_178_seedance`).
- 원본 오류 주석 85개, POC 후보 55개. 후보 수는 정답 검출 수가 아닙니다.
- 실제 성공한 검수 모델: Vertex AI `gemini-3.8-flash` (Argon 403 후 대체).

| 위치 | 내용 |
|---|---|
| [상세 비교표](work/spotlight_poc30_comparison_20261104/index.html) | 모델/난이도/파일명 필터, 원본 라벨·후보 설명, 영상 재생 |
| [영상별 CSV](work/spotlight_poc30_comparison_20261104/videos.csv) | 30개 영상별 요약 |
| [원본 오류별 CSV](work/spotlight_poc30_comparison_20261104/annotations.csv) | 85개 원본 주석과 시간 비교 |
| [후보별 CSV](work/spotlight_poc30_comparison_20261104/candidates.csv) | POC 후보 55개 |
| [실행 설명·전체 요약](benchmarks/SPOTLIGHT_POC30.md) | 선정 기준·실행 결과·한계 |
| `input_videos/` | 생성 모델별 원본 영상 30개 |
| [입력 목록](input_manifest.json) | 원본 영상의 이 폴더 내 경로, SHA-256, 실행 당시 경로 |
| `work/` | 개별 리포트·원본 프레임 근거·재생용 영상·검수 CSV, 최초 실행과 재실행 이력 |
| `source_data/` | 선정한 30개 원본 메타데이터, 데이터셋 설명과 라이선스 |
| `bundle_manifest.json` | 복사 파일의 출처·SHA-256·크기와 링크 검증 결과 |

폴더 구조를 유지하면 다른 위치로 옮겨도 HTML·CSV의 상대 링크가 연결됩니다.
JSON에 남은 절대 경로는 실행 당시의 기록입니다. 현재 보관된 원본 영상은 `input_manifest.json`에서 찾습니다.
원본 리포트·검증 JSON은 해시 보존을 위해 수정하지 않았습니다. 재실행 명령은 원래 v4 프로젝트 환경을 기준으로 합니다.
검수 CSV는 원래 출력 상태 그대로 복사했습니다. 원래 프로젝트의 결과 파일도 그대로 유지했습니다.
