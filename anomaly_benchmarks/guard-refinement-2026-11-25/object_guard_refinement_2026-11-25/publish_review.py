import json
from pathlib import Path
from review_anomaly_v3.evaluation.object_review import write_review_index
r=Path(__file__).resolve().parent
plan=json.loads((r/'plan.json').read_text());summary=json.loads((r/'summary.json').read_text())
write_review_index(r,plan,summary)
html=(r/'review.html').read_text()
banner='<p class="intro">0.19.0 · 컵·손 18개 · 객체 소실/급변 평가<br>결함 검출·유형 일치 5/8 → 8/8 · 정상 확인 오탐 2건 유지 · 컵 위치·손 위치/비율 3건을 새로 검출했습니다.<br>사람 확인 정상 8개, 의견 없는 제작 정상 대조 2개를 구분합니다. 기존 책·병 21개 검출·유형 8/8 유지.<br><a href="OBJECT_GUARD_REFINEMENT_2026-11-25.md">개선 전후 보고서</a> · <a href="../onset-refinement-2026-11-25/index.html">개선 전 영상 리포트</a></p>'
html=html.replace('<div class="toolbar"><label for="filter">',banner+'<div class="toolbar"><label for="filter">',1)
(r/'review.html').write_text(html);(r/'index.html').write_text(html)
