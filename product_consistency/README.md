# S26 Ultra — 구현된 기능 범위 평가

[이미지별 상세 결과](report.html) · [JSON](S26_IMPLEMENTED_CHECKS_2026-11-17.json) · [CSV](S26_IMPLEMENTED_CHECKS_2026-11-17.csv)

검사 범위: 카메라 개수, 카메라 섬 유무·형태, 본체 종횡비, 카메라 상대 위치, 렌즈 크기 비율, 센서·플래시, 모서리 형태, 렌즈 외곽 원형도.

제외: C03 로고·문자 내용/형태, C07 로고 크기·위치, C11 버튼·포트·스피커 홀, C10 두께 독립 검증, C12 렌즈 내부 형태.

- 추론 재실행 없이 기존 32장의 저장된 측정값으로 재집계했다. 제품 위치 박스를 제공했던 평가다.
- 모든 이미지에 같은 8개 검사 범위를 적용했다. UNKNOWN인 구현 항목을 임의로 빼서 정상으로 만들지 않았다.
- 결함이 하나라도 있으면 ng, 8개 모두 MATCH면 범위 내 good, 나머지는 unknown이다. good은 제품 전체 정상 승인이 아니다.
- C12_OUTER는 기존 C12 측정값과 동일한 외곽 판정 함수(허용 편차 8%, sigma 1%, 4sigma)를 사용한다. 렌즈 내부의 미검사 때문에 강제되던 UNKNOWN만 분리했다. 다른 7개 항목의 판정과 임계값은 변경하지 않았다.
- 두께는 자세 추정의 입력 가정으로만 사용되어 독립 검증 결과에서 제외했다.
- 처리 시간은 이전 실행의 값이다. 이번 보고서 생성 시간이나 8개 검사만 새로 실행한 성능을 뜻하지 않는다. 박스 지정 및 중단 대기 시간은 제외했다.
- Failed_06은 정답(렌즈 크기)과 검출 항목(C02)이 다르므로 이미지 수준 ng 경보와 정답 결함 검출을 구분해야 한다.
- Test_15의 상세 정답은 label.json 파일명 불일치로 미연결이다. ng 폴더의 이미지 수준 정답은 유지했다.
- 공식 참조와 중복인 2장을 포함한 개발 데이터이며 독립 holdout 평가가 아니다. 기준 프로파일은 초안이다.

| 실제 분류 | 범위 내 good | ng | 판단 보류 |
|---|---:|---:|---:|
| good | 3/21 | 0/21 | 18/21 |
| ng | 0/11 | 4/11 | 7/11 |

| 항목 | 정상 | 결함 | 판단 보류 |
|---|---:|---:|---:|
| 카메라 개수 | 14 | 2 | 16 |
| 카메라 섬 유무·형태 | 14 | 2 | 16 |
| 본체 종횡비 | 6 | 0 | 26 |
| 카메라 상대 위치 | 18 | 0 | 14 |
| 렌즈 크기 비율 | 14 | 0 | 18 |
| 센서·플래시 | 15 | 0 | 17 |
| 모서리 형태 | 5 | 0 | 27 |
| 렌즈 외곽 원형도 | 14 | 0 | 18 |

| 파일 | 정답 | 범위 내 판정 | 판정 가능 | 보류 항목 |
|---|---|---|---:|---|
| [Good_01.png](report.html#case-0) | good | unknown | 7/8 | C09 |
| [Good_02.png](report.html#case-1) | good | unknown | 6/8 | C04, C09 |
| [Official_S26U_Back.png](report.html#case-2) | good | good | 8/8 | — |
| [Official_S26U_BackLeft30.png](report.html#case-3) | good | unknown | 6/8 | C04, C09 |
| [Official_S26U_BackLeft30_Black.png](report.html#case-4) | good | unknown | 6/8 | C04, C09 |
| [Official_S26U_BackLeft30_White.png](report.html#case-5) | good | unknown | 6/8 | C04, C09 |
| [Official_S26U_BackRight30.png](report.html#case-6) | good | unknown | 6/8 | C04, C09 |
| [Official_S26U_Back_Black.png](report.html#case-7) | good | good | 8/8 | — |
| [Official_S26U_Back_White.png](report.html#case-8) | good | good | 8/8 | — |
| [Official_S26U_Front.png](report.html#case-9) | good | unknown | 0/8 | C01, C02, C04, C05, C06, C08, C09, C12_OUTER |
| [Official_S26U_LeftSide.png](report.html#case-10) | good | unknown | 0/8 | C01, C02, C04, C05, C06, C08, C09, C12_OUTER |
| [Official_S26U_RightSide.png](report.html#case-11) | good | unknown | 0/8 | C01, C02, C04, C05, C06, C08, C09, C12_OUTER |
| [Test_01.jpg](report.html#case-12) | good | unknown | 1/8 | C01, C02, C04, C06, C08, C09, C12_OUTER |
| [Test_02.jpg](report.html#case-13) | good | unknown | 4/8 | C04, C06, C09, C12_OUTER |
| [Test_03.png](report.html#case-14) | good | unknown | 1/8 | C02, C04, C05, C06, C08, C09, C12_OUTER |
| [Test_04.jpg](report.html#case-15) | good | unknown | 0/8 | C01, C02, C04, C05, C06, C08, C09, C12_OUTER |
| [Test_06.png](report.html#case-16) | good | unknown | 0/8 | C01, C02, C04, C05, C06, C08, C09, C12_OUTER |
| [Test_16.png](report.html#case-17) | good | unknown | 5/8 | C04, C08, C09 |
| [Test_17.png](report.html#case-18) | good | unknown | 6/8 | C04, C09 |
| [final.png.1280 (1).jpg](report.html#case-19) | good | unknown | 0/8 | C01, C02, C04, C05, C06, C08, C09, C12_OUTER |
| [final.png.1280.jpg](report.html#case-20) | good | unknown | 0/8 | C01, C02, C04, C05, C06, C08, C09, C12_OUTER |
| [Failed_01.png](report.html#case-21) | ng | unknown | 0/8 | C01, C02, C04, C05, C06, C08, C09, C12_OUTER |
| [Failed_02.png](report.html#case-22) | ng | unknown | 0/8 | C01, C02, C04, C05, C06, C08, C09, C12_OUTER |
| [Failed_03.png](report.html#case-23) | ng | unknown | 0/8 | C01, C02, C04, C05, C06, C08, C09, C12_OUTER |
| [Failed_04.png](report.html#case-24) | ng | ng | 8/8 | — |
| [Failed_05.png](report.html#case-25) | ng | ng | 8/8 | — |
| [Failed_06.png](report.html#case-26) | ng | ng | 4/8 | C04, C06, C09, C12_OUTER |
| [Failed_07.png](report.html#case-27) | ng | unknown | 0/8 | C01, C02, C04, C05, C06, C08, C09, C12_OUTER |
| [Failed_08.png](report.html#case-28) | ng | unknown | 0/8 | C01, C02, C04, C05, C06, C08, C09, C12_OUTER |
| [Failed_09.png](report.html#case-29) | ng | ng | 5/8 | C01, C04, C09 |
| [Test_08.png](report.html#case-30) | ng | unknown | 1/8 | C01, C02, C04, C06, C08, C09, C12_OUTER |
| [Test_15.png](report.html#case-31) | ng | unknown | 0/8 | C01, C02, C04, C05, C06, C08, C09, C12_OUTER |
