# S26 Ultra 제품 정합성 평가 자료 — 2026-11-17

[상세 결과 보고서](benchmarks/reports/METROLOGY_S26_RUNBOOK32_2026-11-17.md) · [이미지별 결과 바로 보기](index.html)

총 32장(good 21장 / ng 11장), 제품 위치 박스를 제공한 평가다. NG 경보 4장, UNKNOWN 28장이다.
NG 4장 중 Failed_06은 정답 결함과 검출 항목이 다르다. 평균 23.733초/장이며 박스 지정 시간 및 중단 대기 시간은 제외했다.

- `benchmarks/reports/`: 상세 보고서(MD/JSON/CSV), 독립 실행·분할 대조 검증, 이전 자동 평가 JSON.
- `outputs/metrology_s26_runbook32_2026-11-16/`: 32장별 HTML/JSON, 원본 사본, 근거 이미지, 분할 마스크, 오버레이, 실행 로그·메타데이터.
- `outputs/metrology_s26_runbook_segmentation/`: 사전 분할 검토 자료.
- `benchmarks/incoming/galaxy-s26-ultra/`: good/ng 원본 이미지와 사용자 정답.
- `benchmarks/datasets/`: 이미지 목록·해시, 제품 위치 박스·뷰 설정, 입고 기록.
- `product_library/galaxy-s26-ultra/`, `benchmarks/profiles/`: 제품 기준 자료.
- `references/`, `scripts/`: 참조 절차 및 평가·분할 준비 스크립트.
- `COPY_MANIFEST.json`: 원본과 바이트 일치를 검증한 복사 파일 목록·SHA-256.

저장 구조를 유지하여 상세 보고서에서 이미지별 결과 및 근거 이미지를 열 수 있다.
자료는 원본 저장소에서 복사했으며, 실행 환경 전체를 포함한 독립 배포 패키지는 아니다.
평가를 다시 실행하려면 원본 v4 코드와 Python 환경이 필요하다. 실행 명령은 상세 보고서에 있다.
원본 위치: `/home/jh_marc.kim/aic-creative-assurance/backend/review_product_consistency_v4`.
