import json, re
from pathlib import Path
r=Path(__file__).resolve().parent
f=json.loads((r/'fresh-summary.json').read_text())
h=json.loads((r/'human-summary.json').read_text())
notes=json.loads((r/'analysis-notes.json').read_text())['notes']
html=(r/'review.html').read_text()
pattern=r'(<script id="case-data" type="application/json">)(.*?)(</script>)'
m=re.search(pattern,html,re.S)
cases=json.loads(m.group(2))
for case in cases:
    note=notes.get(case['id'])
    if note and note not in case['observation']:case['observation']+=' '+note
data=json.dumps(cases,ensure_ascii=False).replace('<',r'\u003c').replace('&',r'\u0026')
html=html[:m.start(2)]+data+html[m.end(2):]
banner=('<p class="intro">신규 컵·손 18개 · 고정 검출기 0.17.0 · 객체 소실/급변 항목만 평가<br>'
        f"합성 결함 {f['detected_events']}/{f['positive_events']}건 검출·유형 일치 {f['expected_type_matched']}건 · "
        f"사람 확인 정상 {h['human_normal_clips']}개 중 오탐 {h['human_normal_false_positive_candidates']}건 · "
        f"검수 의견 미제공 대조 {h['construction_only_normal_clips']}개는 제작 라벨만 유지. "
        '관측 기록상 검사 완료여도 결함을 놓칠 수 있습니다. '
        '<a href="OBJECT_FRESH_HUMAN_REVIEW_2026-11-25.md">결과 분석 문서</a></p>')
marker='<div class="toolbar"><label for="filter">'
if banner not in html:html=html.replace(marker,banner+marker,1)
(r/'review.html').write_text(html)
(r/'index.html').write_text(html)
