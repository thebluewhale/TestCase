# AI 제작물 리스크 검토 API 연동 가이드

외부 시스템(node 등)에서 광고 리스크 검토(risk review)를 호출하는 방법이다.
검토는 **비동기 작업**으로 처리된다 — 제출하면 작업 ID를 바로 돌려주고, 결과는 상태 조회(폴링)로 받는다.

```
1) 업로드 URL 발급 ─▶ 2) 파일 PUT ─▶ 3) 검토 작업 제출 ─▶ 4) 상태 폴링 ─▶ 5) 리포트 HTML (선택)
```

## 1. 공통

| 항목 | 값 |
|---|---|
| Base URL | `https://riskcensoring.gbcaicreativelab.com` |
| API 경로 프리픽스 | `/api/risk_censoring` |
| 인증 | `X-API-Key: <발급받은 API 키>` 헤더 — 키 없이도 호출할 수 있다(키 없는 접속 권한: risk·제품 이미지 검토 가능, 제품 영상 검토 불가) |
| 출처 헤더 (선택) | `X-Client-Name: <호출 시스템 이름>` — 키 없이 부를 때 검토 이력의 출처 표시 (아래 참조) |
| 요청/응답 형식 | JSON (`Content-Type: application/json`), 필드명은 camelCase |
| 시각 표기 | ISO 8601 UTC (예: `2026-10-26T03:12:45Z`) |

- API 키는 별도 경로로 전달한다. 키는 서버에 해시로만 저장되므로 분실 시 재발급해야 한다.
- 키에 허용된 기능만 호출할 수 있다. 허용되지 않은 기능은 403이 돌아온다.
- 접근이 허용된 네트워크에서만 호출할 수 있다. 403 HTML 페이지(`403 Forbidden`)가 돌아오면
  호출 측 IP 허용 여부를 운영 담당자에게 확인한다.

### 출처 헤더 `X-Client-Name` (선택)

검토 결과는 서비스 웹 화면의 **검토 이력**에도 남는다. 이력의 "출처" 칸으로 어느 시스템이 의뢰했는지 구분한다.

| 호출 방식 | 이력의 출처 |
|---|---|
| `X-API-Key`로 호출 | 키 이름 (예: `node`) — `X-Client-Name`은 무시된다 |
| 키 없이 `X-Client-Name: node`로 호출 | `node` |
| 둘 다 없음 | `웹` (웹 화면에서 의뢰한 것과 구분되지 않는다) |

- 값은 **소문자·숫자·`-`로 된 1~32자**만 받는다(예: `node`, `node-batch`). 형식이 틀리면 오류 없이 무시되고
  출처는 `웹`으로 남는다.
- **표시 전용**이다 — 권한·작업 조회 범위에는 영향이 없다. 키 없이 부르면 키 없는 접속의 권한을 따른다.
- 작업 제출(4단계, `POST …/v1/reviews/*`)에 붙이면 된다. 다른 요청에 붙여도 문제는 없다.
- 응답에는 이 값이 나오지 않는다.

### 오류 응답

API 오류는 아래 형식이다. 분기는 `code`로 하고, `message`는 사용자 표시용 한국어 문구다.

```json
{ "detail": { "code": "invalid_file", "message": "지원하지 않는 파일 형식입니다: text/plain" } }
```

요청 본문 형식이 틀리면(필수 필드 누락 등) `422`와 함께 `{"detail": [ ... ]}`(필드별 검증 오류 목록)이 돌아온다.

## 2. 업로드 URL 발급

```
POST /api/risk_censoring/uploads
```

요청:

```json
{ "filename": "ad.mp4", "contentType": "video/mp4", "sizeBytes": 12345678 }
```

| 필드 | 타입 | 설명 |
|---|---|---|
| `filename` | string | 원본 파일명 (리포트에 표시된다) |
| `contentType` | string | 파일 MIME 타입 — 아래 허용 형식 중 하나 |
| `sizeBytes` | integer | 파일 크기(바이트), 0보다 커야 한다 |

응답 `200`:

```json
{ "uploadUrl": "https://storage.googleapis.com/...", "objectName": "uploads/..." }
```

허용 형식·한도:

| 종류 | `contentType` | 크기 | 길이 |
|---|---|---|---|
| 이미지 | `image/jpeg`, `image/png`, `image/webp`, `image/gif` | 20MB 이하 | — |
| 영상 | `video/mp4`, `video/quicktime` | 512MB 이하 | 120초 이하 |

- 형식·크기가 허용 범위 밖이면 `400 invalid_file`.
- 영상 길이는 실행 단계에서 확인한다 — 초과하면 작업이 `failed`(`duration_exceeded`)로 끝난다.

## 3. 파일 업로드 (PUT)

발급받은 `uploadUrl`(Google Cloud Storage 서명 URL)로 파일 바이트를 그대로 올린다. 이 요청에는 API 키를 붙이지 않는다.

```
PUT <uploadUrl>
Content-Type: <2단계에서 보낸 contentType과 동일>

<파일 바이트>
```

- `uploadUrl`은 **15분간** 유효하다.
- `Content-Type`이 발급 시 값과 다르면 스토리지가 서명 오류(403)로 거부한다.
- 성공하면 `200`이 돌아온다.

## 4. 검토 작업 제출

```
POST /api/risk_censoring/v1/reviews/risk
```

요청:

```json
{ "objectName": "uploads/...", "mediaType": "video/mp4", "clientRequestId": "node-req-0001" }
```

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `objectName` | string | ✔ | 2단계 응답의 `objectName` |
| `mediaType` | string | ✔ | 파일 MIME 타입 (2단계 `contentType`과 같은 값) |
| `clientRequestId` | string | | 호출 측 요청 ID (1~200자). **같은 키·같은 값이면 새 작업을 만들지 않고 기존 작업을 돌려준다** — 네트워크 재시도 시 중복 실행 방지용으로 넣는 것을 권장 |

응답:

- `202 Accepted` — 새 작업을 만들었다.
- `200 OK` — 같은 `clientRequestId`의 기존 작업을 돌려준다(상태는 그 시점 값).

```json
{
  "jobId": "4f1c2b3a-....",
  "type": "risk",
  "status": "queued",
  "clientRequestId": "node-req-0001",
  "mediaType": "video/mp4",
  "productId": null,
  "createdAt": "2026-10-26T03:12:45Z",
  "startedAt": null,
  "finishedAt": null,
  "attempts": 0,
  "progress": null,
  "summary": null,
  "error": null,
  "hasReport": false,
  "statusUrl": "/api/risk_censoring/v1/jobs/4f1c2b3a-...."
}
```

`statusUrl`·`reportUrl`은 Base URL을 붙여 쓰는 상대 경로다.

| 상태 코드 | `code` | 의미 |
|---|---|---|
| 401 | `invalid_api_key` | 키 누락 또는 잘못된 키 |
| 403 | `risk_disabled` | 이 키에 리스크 검토가 허용되지 않음 |
| 422 | — | 요청 본문 형식 오류 |
| 503 | `jobs_unavailable` | 작업 큐 등록 실패 — 잠시 후 다시 제출 |

## 5. 작업 상태 조회 (폴링)

```
GET /api/risk_censoring/v1/jobs/{jobId}
```

작업을 만든 **같은 API 키**로 조회한다. 응답 형태는 4단계와 같다. **2~5초 간격**으로 `status`가 `done` 또는
`failed`가 될 때까지 조회한다.

### `status`

| 값 | 의미 |
|---|---|
| `queued` | 대기 중 |
| `running` | 실행 중 (`progress`에 진행 상황) |
| `done` | 완료 — `summary`·`reportUrl` 제공 |
| `failed` | 실패 — `error` 제공 |

### `progress` (실행 중)

```json
{ "stage": "analyzing", "phase": "writing", "current": 7, "total": 20 }
```

| 필드 | 값 |
|---|---|
| `stage` | `downloading`(원본 받기) → `extracting`(전처리 — 이미지 변환·영상 프레임 추출) → `analyzing`(검토) |
| `phase` | `analyzing` 단계에서만 — `thinking`(모델 추론 중) → `writing`(항목별 평가 작성 중) |
| `current`, `total` | `phase`가 `writing`일 때만 — **작성 중인 검토 항목 번호 / 전체 검토 항목 수**(20 또는 21) |

- `stage`가 바뀌면 `phase`·`current`·`total`은 비워진다. `analyzing` 직후에는 `phase`가 아직 없을 수 있다.
- 퍼센트로 표시할 수 있는 구간은 `writing`(`current / total`)뿐이다. 그 전에는 단계 이름만 표시한다.
  예: 대기 중 → 파일 받는 중 → 전처리 중 → 분석 중 → 항목 작성 7/20.
- `thinking` 구간이 처리 시간의 상당 부분을 차지한다 — 이 동안 숫자가 바뀌지 않는 것은 정상이다.
- 서버는 진행 상황을 **최소 2초 간격**으로 기록한다(단계 변경은 즉시). 2초보다 자주 조회해도 새 정보는 없다.
- 일시 오류로 서버가 재시도하면 `status`가 잠시 `queued`로 돌아가고 `progress`가 비워지며 `attempts`가 1 늘어난다.

진행 표시용 값이며, 세부 구성은 바뀔 수 있으므로 `status` 외의 값으로 로직을 분기하지 않는다.

### `done` — 결과 요약

```json
{
  "jobId": "4f1c2b3a-....",
  "status": "done",
  "startedAt": "2026-10-26T03:12:47Z",
  "finishedAt": "2026-10-26T03:14:05Z",
  "attempts": 1,
  "summary": {
    "overall": { "level": "High", "summary": "종합 의견 문장 ..." },
    "categories": [
      { "n": 1, "ko": "항목명", "level": "None" },
      { "n": 2, "ko": "항목명", "level": "Medium" }
    ],
    "assetName": "ad.mp4"
  },
  "hasReport": true,
  "reportUrl": "/api/risk_censoring/v1/jobs/4f1c2b3a-..../report.html",
  "...": "..."
}
```

| 필드 | 설명 |
|---|---|
| `summary.overall.level` | 종합 등급 — `Critical` > `High` > `Medium` > `Low` > `None` |
| `summary.overall.summary` | 종합 의견 (한국어) |
| `summary.categories[]` | 검토 항목별 등급 — `n`(항목 번호), `ko`(항목명), `level`(위와 같은 등급). 항목 수는 서비스 설정에 따라 20~21개 — 개수를 고정 가정하지 않는다 |
| `summary.assetName` | 검토한 파일명 |

항목별 상세 근거(지적 내용·위치·개선 제안)는 리포트 HTML에 있다.

> 모델이 검토를 거부한 경우도 오류가 아니다 — `done`으로 끝나며 `overall.level`이 `Critical`이다.

### `failed` — 오류

```json
{ "status": "failed", "error": { "code": "duration_exceeded", "message": "영상 길이 135초 — 최대 120초까지 지원합니다" } }
```

| `code` | 의미 | 조치 |
|---|---|---|
| `object_not_found` | 업로드한 파일을 찾지 못함 | 업로드(3단계) 성공 여부 확인 후 재시도 |
| `storage_forbidden` | 파일 접근 권한 오류 | 운영 담당자 문의 |
| `invalid_file` | 지원하지 않는 형식·크기 | 파일 확인 |
| `corrupt_file` | 손상되었거나 열 수 없는 파일 | 파일 확인 |
| `duration_exceeded` | 영상 길이 120초 초과 | 영상 편집 후 재제출 |
| `extract_failed` | 영상 프레임 추출 실패 | 다른 인코딩으로 재제출 |
| `rate_limited` | 모델 호출 한도 초과 | 잠시 후 새 작업으로 재제출 |
| `upstream_error` | 모델 호출 오류 | 잠시 후 새 작업으로 재제출 |
| `internal_error` | 서버 내부 오류 | 운영 담당자 문의 (`jobId` 전달) |

- 일시 오류(`rate_limited`, `upstream_error` 등)는 서버가 **최대 3회까지 자동 재시도**한다(`attempts`로 확인).
  `failed`는 재시도까지 모두 실패한 최종 상태다.
- 재제출할 때는 **새 `clientRequestId`**를 쓴다 — 같은 값이면 실패한 기존 작업이 그대로 돌아온다.

### 조회 오류

| 상태 코드 | `code` | 의미 |
|---|---|---|
| 401 | `invalid_api_key` | 잘못된 키 |
| 404 | `not_found` | 작업이 없거나, 다른 키로 만든 작업, 또는 보관 기간(7일)이 지난 작업 |

## 6. 리포트 HTML (선택)

```
GET /api/risk_censoring/v1/jobs/{jobId}/report.html
```

- `done` 이후 같은 키로 조회한다. 아직 완료 전이면 `404 not_ready`.
- 외부 리소스 없이 혼자 열리는 단일 HTML 문서다(라이트 테마, 미리보기 이미지가 문서 안에 포함됨).
- 화면에 보여줄 때는 iframe에 `srcdoc`로 넣고 `sandbox="allow-scripts"`를 권장한다.
  파일로 저장해 브라우저에서 바로 열어도 된다.

## 7. 운영 정보

| 항목 | 값 |
|---|---|
| 처리 시간(대략) | 이미지 약 35초, 영상 약 80초 + 큐 대기 |
| 동시 실행 | 서비스 전체 4건 — 나머지는 큐에서 대기 |
| 작업 최대 실행 시간 | 30분 |
| 결과 보관 | **7일** — 이후 상태 조회·리포트 모두 404. 필요하면 호출 측에 저장 |
| 권장 폴링 | 2~5초 간격, 클라이언트 타임아웃 10분 이상 |

## 8. 예시 (Node.js 18+, 내장 fetch)

```js
import { readFile } from "node:fs/promises";
import { randomUUID } from "node:crypto";

const BASE = "https://riskcensoring.gbcaicreativelab.com/api/risk_censoring";
const KEY = process.env.RISK_API_KEY;
// 키 없이 부르면 출처 헤더로 이력의 출처를 표시한다 (키가 있으면 키 이름이 출처 — 헤더는 무시)
const json = {
  ...(KEY ? { "X-API-Key": KEY } : { "X-Client-Name": "node" }),
  "Content-Type": "application/json",
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function call(url, init) {
  const res = await fetch(url, init);
  const body = await res.json();
  if (!res.ok) throw new Error(`${res.status} ${body.detail?.code ?? ""} ${body.detail?.message ?? ""}`);
  return body;
}

export async function reviewRisk(path, filename, contentType) {
  const buf = await readFile(path);

  // 1) 업로드 URL 발급
  const up = await call(`${BASE}/uploads`, {
    method: "POST",
    headers: json,
    body: JSON.stringify({ filename, contentType, sizeBytes: buf.length }),
  });

  // 2) 파일 PUT (Content-Type은 발급 시 값과 동일, API 키 없음)
  const put = await fetch(up.uploadUrl, { method: "PUT", headers: { "Content-Type": contentType }, body: buf });
  if (!put.ok) throw new Error(`upload failed: ${put.status}`);

  // 3) 작업 제출
  let job = await call(`${BASE}/v1/reviews/risk`, {
    method: "POST",
    headers: json,
    body: JSON.stringify({ objectName: up.objectName, mediaType: contentType, clientRequestId: randomUUID() }),
  });

  // 4) 폴링
  const deadline = Date.now() + 15 * 60 * 1000;
  while (job.status === "queued" || job.status === "running") {
    if (Date.now() > deadline) throw new Error(`timeout (job ${job.jobId})`);
    await sleep(3000);
    job = await call(`${BASE}/v1/jobs/${job.jobId}`, { headers: KEY ? { "X-API-Key": KEY } : {} });
  }
  if (job.status === "failed") throw new Error(`${job.error.code}: ${job.error.message}`);

  // 5) 리포트 HTML (선택)
  const report = await fetch(`${BASE}/v1/jobs/${job.jobId}/report.html`, { headers: KEY ? { "X-API-Key": KEY } : {} });
  return { jobId: job.jobId, summary: job.summary, reportHtml: await report.text() };
}
```

### curl

```bash
BASE=https://riskcensoring.gbcaicreativelab.com/api/risk_censoring
KEY=<API 키>

curl -s -X POST "$BASE/uploads" -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"filename":"ad.png","contentType":"image/png","sizeBytes":'"$(stat -c%s ad.png)"'}'
# → {"uploadUrl": "...", "objectName": "..."}

curl -s -X PUT "<uploadUrl>" -H "Content-Type: image/png" --data-binary @ad.png

curl -s -X POST "$BASE/v1/reviews/risk" -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"objectName":"<objectName>","mediaType":"image/png","clientRequestId":"test-0001"}'

# 키 없이 부를 때 — 출처 헤더로 이력의 출처를 node로 표시
curl -s -X POST "$BASE/v1/reviews/risk" -H "X-Client-Name: node" -H "Content-Type: application/json" \
  -d '{"objectName":"<objectName>","mediaType":"image/png","clientRequestId":"test-0002"}'

curl -s "$BASE/v1/jobs/<jobId>" -H "X-API-Key: $KEY"
curl -s "$BASE/v1/jobs/<jobId>/report.html" -H "X-API-Key: $KEY" -o report.html
```
