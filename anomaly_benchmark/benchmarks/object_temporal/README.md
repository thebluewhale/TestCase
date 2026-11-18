# 객체 대조 기준선 실행 안내

아래 명령은 원래 v3 개발 저장소에서 재실행할 때 사용하는 명령입니다. 이 복사본에서는 루트의 `index.html`을 열어 영상과 검수 근거를 확인하세요.

## 객체 소실·급변 대조 기준선

새 비교는 **자동 입력 → 실제 추적 API → 전체 트랙 후보 → 표시 리포트**를 평가한다. 앞 절의 단일 대상
추적 점수와 분모/의미가 다르다. [고정 개발셋](comparison_v1/README.md)과
[첫 기준선](../reports/OBJECT_COMPARISON_2026-11-18.md)을 참고한다.

```bash
# v3 안에서 실행. parent에는 기존 LaSOT 영상 변환과 완료된 API 응답이 필요하다.
.venv/bin/python scripts/object_comparison.py prepare \
  --parent work/lasot-vi-baseline-2026-11-18 --run work/object-comparison-new
.venv/bin/python scripts/object_comparison.py run \
  --run work/object-comparison-new --project dev-comfyui --region asia-east1
.venv/bin/python scripts/object_comparison.py evaluate --run work/object-comparison-new
```

prepare는 새 디렉터리만 허용하고 계획/미디어/라벨/설정을 해시로 고정한다. 새 합성 입력 최대 18개·108초,
기존 응답 재사용 3개이며 두 요청만 동시 처리한다. GT는 생성과 사후 평가에서만 사용한다.
run 재실행은 같은 경로의 완료 응답/리포트를 검증해 재사용하고 pending은 기존 operation을 조회한다.
operation ID가 없는 불명확한 제출은 자동 재전송하지 않는다. 새 디렉터리를 생성하면 새 호출 비용이 발생한다.
검출기 소스/설정이 바뀌면 기존 run을 혼용하지 않고 새 비교 실행을 준비해야 한다. 평가 코드 해시는 summary에 남긴다.

evaluate는 전체 계획 분모를 유지해 summary.json을 쓰며 미실행/실패도 보존한다. API/리포트/미디어/설정 해시
불일치는 중단한다. summary.json/review.html은 재채점 때 갱신되므로 비교용 결과는 별도 보관한다.
`review.html`은 영상/리포트 상대 경로를 참조하므로 실행 디렉터리 전체를 함께 보존한다.
정상 대조에서 후보가 없어도 관측 불가를 정상 판정으로 바꾸지 않는다. 원본 LaSOT에는 AI 결함 정답이 없다.
