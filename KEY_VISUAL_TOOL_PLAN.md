# 광고용 Key Visual 제작 툴 기획서

- 작성일: 2026-10-01
- 단계: 서비스 기획 (시장 조사 및 기술 검토)
- 조사 방법: 공식 문서, 리뷰, 기사 기반 웹 조사. ChatGPT Sketch만 직접 사용해 보았고, 나머지 서비스는 직접 검증하지 않음. 가격은 대부분 제3자 사이트 수치이므로 확정 전 공식 가격표 확인이 필요함.

---

## 1. 요약

- 기획안과 **동일한 흐름을 가진 상용 서비스는 찾지 못했다.** 다만 부분적으로 겹치는 서비스는 여럿 있고, 범용 서비스(ChatGPT, Krea)가 같은 방향으로 빠르게 오고 있다.
- 핵심 기능 3가지(영역 감지, 영역별 생성, 초안 조화)는 **현재 기술로 모두 구현 가능하다.**
- 가장 큰 리스크는 최종 조화 단계에서 **제품 공식 이미지가 변형될 수 있다**는 점이다. 이 부분은 PoC로 먼저 검증해야 한다.
- ChatGPT Sketch는 영역 분할 없이 스케치를 모델에 바로 넘겨 한 번에 생성하는 것으로 보인다. 따라서 영역 감지는 **생성을 위해서가 아니라 입력 UX를 위해서** 의미가 있고, 초안 단계는 필수가 아닐 수 있다. PoC에서 세 가지 파이프라인을 비교해 결정한다. (4.5절)

---

## 2. 서비스 개요

### 2.1 목표

클라이언트의 요구사항에 맞춰, 제품 공식 이미지가 포함된 Key Visual을 비교적 쉽게 생성한다.

### 2.2 핵심 기능 (사용자 흐름)

1. 사용자가 웹페이지에서 Canvas를 생성한다. (Canvas는 빈 작업 영역을 뜻하며, 반드시 HTML canvas element일 필요는 없음)
2. 사용자가 그림판처럼 화면에 대충 그림을 그린다.
3. AI가 그림의 영역을 감지하고 분할한 뒤, 영역별로 ID를 지정한다.
4. Canvas 하단에 감지된 영역 개수만큼 영역별 input 창이 생성된다.
5. 사용자가 영역별 input 창에 들어갈 내용을 간략히 입력하거나, 해당 영역에 들어갈 reference image를 첨부한다.
6. (필요한 경우) 이미지 전체의 톤과 느낌을 설명하는 전체 프롬프트를 입력한다.
7. 생성형 AI가 영역별로 이미지를 생성해 초안을 만든다. 초안은 큰 canvas에 영역별로 서로 다른 이미지를 붙여 놓은 형태이며, 조화롭지 않아도 된다.
8. 초안 이미지와 전체 프롬프트를 생성형 AI에 전달해, 조화롭고 완성된 하나의 이미지를 생성한다.

### 2.3 구동 환경

Google Cloud Platform. 버킷, VM, GPU, Cloud Run, Vertex AI(Claude, Gemini 등)를 포함해 GCP의 거의 모든 기능을 사용할 수 있다.

---

## 3. 유사 상용 서비스 조사

### 3.1 서비스별 비교

| 서비스 | 사용 방법 | 장점 | 단점 / 우리 기획과의 차이 |
|---|---|---|---|
| [Krea Edit – Annotations](https://www.krea.ai/blog/annotations) (가장 유사, 2026-03 출시) | 이미지 위에 사각형을 여러 개 그리면 번호가 붙고, 영역별 프롬프트와 참조 이미지를 넣어 한 번에 생성 | 영역별 프롬프트·참조 이미지 UX가 우리 기획과 거의 같음 | 기존 이미지 수정용이고 사각형만 지원. 빈 캔버스에서 시작하는 흐름이나 초안 단계는 없음 |
| [ChatGPT Images 2.5 – Sketch](https://www.unite.ai/openai-releases-chatgpt-images-2-5-with-sketch-and-two-new-api-models/) (2026-09 출시) | 채팅에서 `@Sketch`로 대충 그린 뒤 텍스트 지시와 함께 제출. 결과 이미지에 코멘트를 달아 부분 수정 | 접근성이 높고 참조 이미지 보존이 개선됨. Poster 등 템플릿 제공. 직접 사용해 본 결과 품질이 매우 좋았음 | 영역 자동 분할이나 영역별 입력창이 없음. 전부 하나의 프롬프트로 설명해야 함. Sketch는 ChatGPT 전용 UI 기능이라 API로는 제공되지 않음 |
| [Flair.ai](https://flair.ai) | 실제 제품 사진을 캔버스에 놓고 소품·배경을 드래그 앤 드롭으로 배치한 뒤 장면 생성 | 실제 제품 이미지를 그대로 쓰므로 제품 정확도가 높음. 유료 플랜 월 $8부터 | 스케치 기반이 아니고 제품 사진 중심. 영역별 프롬프트 없음 |
| [Photoshop](https://helpx.adobe.com/photoshop/desktop/repair-retouch/remove-objects-fill-space/blend-subjects-with-harmonize.html) (Generative Fill + Harmonize) | 영역을 선택해 프롬프트·참조 이미지로 채우고, Harmonize로 합성물의 조명·색·그림자를 맞춤 | 품질과 제어력이 가장 높고, 우리의 "초안 → 조화" 단계와 개념이 같음 | 전문가용 수작업. "쉽게"와 거리가 멂 |
| [Lovart](https://www.lovart.ai) | 무한 캔버스에서 디자인 에이전트와 대화로 생성하고, 요소를 클릭해 수정 | 브리프에서 시안까지 자동화, 브랜드 키트 | 레이아웃을 그림으로 지정하지 않음. 리뷰에서 제품 일관성이 약점으로 지적됨 |
| [Krea](https://www.krea.ai/apps/sketch-to-image) / [Freepik](https://www.freepik.com/ai/docs/sketch-to-image) 실시간 스케치 | 그리는 동안 이미지가 실시간으로 갱신됨 | 즉각적인 피드백 | 전체 프롬프트 하나만 있고 영역 개념과 제품 이미지 삽입이 없음 |
| [Invoke](https://invoke.ai) (오픈소스) | 영역을 브러시로 칠하고 영역별 프롬프트·참조 이미지 지정 | 기능상 우리 기획과 가장 가깝고 Apache 2.0 | 호스팅 서비스는 2025-10 종료, 자체 설치만 가능. 전문가용 UI |

### 3.2 우리 기획의 차별점

**장점**

- 빈 캔버스에서 자유롭게 그리면 영역이 자동 인식되고 영역별 입력 폼이 생긴다. 클라이언트 브리프를 그대로 옮기기 좋은 구조다.
- 초안을 눈으로 확인하고 영역 단위로 고칠 수 있다.
- 제품 공식 이미지 삽입이 기본 기능이다.

**단점**

- 범용 서비스(ChatGPT, Krea)가 빠르게 같은 방향으로 오고 있다.
- 2단계 생성이라 시간과 비용이 더 든다.
- 모델 자체는 Google 것을 쓰므로, 차별화는 UX와 워크플로에서만 나온다.

### 3.3 ChatGPT Sketch의 동작 방식 분석

ChatGPT Sketch는 영역 감지 단계 없이 바로 결과를 생성한다. 백엔드에서 영역을 나눠 생성한 뒤 붙이는 방식이 아니라, **스케치를 이미지 입력으로 모델에 그대로 넘겨 한 번에 생성하는 방식**일 가능성이 매우 높다. OpenAI가 내부 구조를 공개한 것은 아니므로 추정이며, 근거는 다음과 같다.

- **Sketch는 모델 기능이 아니라 UI 기능이다.** API에는 Sketch가 없고 ChatGPT 인터페이스에만 있다고 보도되었다. 그리기 화면은 스케치 이미지를 만드는 도구일 뿐이고, 생성은 일반 이미지 입력을 받는 같은 모델(`gpt-image-2.5`)이 한다.
- **모델이 이미지를 직접 이해한다.** GPT Image 계열은 텍스트와 이미지를 한 신경망에서 처리하는 네이티브 멀티모달 모델이라, 스케치의 배치와 형태를 별도 분할 없이 읽고 반영할 수 있다.
- **분할 후 합성 방식의 흔적이 없다.** 영역별로 따로 생성해 붙였다면 경계선과 조명 불일치가 생기고 이를 다듬는 추가 생성 단계가 필요하다. 실제로는 한 번에 자연스러운 결과가 나온다.

**우리 기획에 주는 의미**

- 같은 방식은 `gemini-3-pro-image`로도 가능하다. 스케치를 입력 이미지로 넣고 참조 이미지와 프롬프트를 함께 주면 된다.
- 영역 감지는 생성을 위해서는 필요 없고, 입력 UX를 위해서만 의미가 있다. "이 위치에 무엇이 들어가는지"를 영역별 입력창으로 받고, 특정 위치에 제품 공식 이미지를 연결할 수 있다는 점이 ChatGPT Sketch 대비 차별점이다.
- 초안 단계의 필요성은 약해졌다. 대안 파이프라인은 4.5절에 정리한다.

---

## 4. 기술 구현 가능성 검토

### 4.1 검토 결과 요약

| 검토 항목 | 결론 | 난이도 | 핵심 리스크 |
|---|---|---|---|
| ① 대충 그린 그림의 영역 감지·분리 | 가능 | 낮음~중 | "무엇이 한 영역인가"의 모호함 |
| ② 영역별 이미지 생성 | 가능 | 낮음 | 투명 배경 출력 지원 여부 미확인 |
| ③ 초안 + 프롬프트 → 조화로운 한 장 | 가능하나 품질 검증 필요 | 중~높음 | 제품 변형, 레이아웃 이탈 |

### 4.2 ① 영역 감지·분리

- 캔버스를 직접 만들기 때문에 픽셀이 아니라 획(stroke) 데이터를 갖고 있어 유리하다.
- 닫힌 도형은 OpenCV의 연결 영역 분석으로 비용 없이 확정적으로 분리된다.
- 끊긴 선이나 낙서형 그림은 Gemini의 [bounding box·segmentation 출력](https://ai.google.dev/gemini-api/docs/image-understanding)으로 보완하고, "이건 병 모양" 같은 라벨도 받을 수 있다.
- 단, Gemini의 이 기능은 실사 이미지 기준으로 문서화되어 있다. 추상적인 스케치에서의 정확도는 테스트가 필요하다.
- 겹침, 도형 안의 도형, 배경 처리 등은 AI가 완벽히 맞출 수 없다. 영역 병합·분할·삭제 UI가 필수다.

### 4.3 ② 영역별 이미지 생성

- 영역마다 bounding box 비율에 가까운 종횡비로 `gemini-3.1-flash-image`를 병렬 호출하고, 결과를 잘라서 붙인다.
- 제품 공식 이미지는 생성하지 않고, 원본을 배경 제거해 그대로 배치하는 편이 낫다.
- 이를 위해 참조 이미지에 "그대로 사용"과 "참고만" 구분이 필요하다.
- Gemini 이미지 모델이 투명 배경 출력을 지원하는지는 확인하지 못했다. 오브젝트형 영역에는 배경 제거 단계(Cloud Run GPU에 오픈 모델)를 따로 둬야 할 수 있다.

### 4.4 ③ 초안 → 조화로운 최종 이미지

`gemini-3-pro-image`(Nano Banana Pro)가 스케치·레이아웃 이미지와 참조 이미지 최대 14장(고충실도 오브젝트 6장)을 받아 최대 4K로 생성한다. [스케치로 배치를 지정하는 용도](https://dev.to/googleai/nano-banana-pro-prompting-guide-strategies-1h9n)가 공식 가이드에 있다.

품질 리스크는 이 단계에 집중된다.

| 리스크 | 내용 | 대응 방안 |
|---|---|---|
| 제품 변형 | 작은 글자와 로고가 뭉개지거나 바뀔 수 있음. 픽셀 단위 보존은 보장되지 않음. 광고용으로는 가장 치명적 | 원본을 고충실도 참조로 함께 입력. 필요하면 최종 결과에 원본 제품을 다시 합성하는 후처리 검토 (미검증 제안) |
| 레이아웃 이탈 | 모델이 요소의 위치와 크기를 임의로 바꿀 수 있음 | 후보를 2~4장 생성해 사용자가 고르는 UX |
| 명시적 마스크 없음 | Vertex의 Imagen 계열(마스크 인페인팅, product recontext)은 검색 결과상 2026-03 종료되어 Gemini 이미지 모델로 통합됨 (공식 문서 재확인 필요) | 특정 픽셀을 잠가야 하면 GPU에 오픈 모델을 올림 |
| 종횡비 제한 | 정해진 목록의 종횡비만 지원 | 캔버스 생성 시 해당 비율로 제한 |
| 해상도 상한 | 최대 4K | 대형 인쇄물은 업스케일 단계 추가 |
| 워터마크·필터 | 출력물에 SynthID 비가시 워터마크 포함. 인물·브랜드는 안전 필터에 걸릴 수 있음 | 클라이언트 사전 고지, 실패 시 재시도·안내 UX |
| 텍스트 품질 | 카피와 로고를 생성하면 오류 가능 | 생성하지 않고 최종 이미지 위에 실제 레이어로 얹음 |

### 4.5 생성 파이프라인 대안

ChatGPT Sketch 분석(3.3절) 결과, 영역별 초안을 거치지 않는 방식도 가능하다. 후보는 세 가지다.

| 안 | 방식 | 생성 호출 수 | 장점 | 단점 |
|---|---|---|---|---|
| A. 직접 생성 | 스케치 + 전체 프롬프트만으로 한 번에 생성 (ChatGPT Sketch 방식) | 1회 | 가장 빠르고 저렴. 구현이 단순 | 영역별 지시와 제품 이미지 위치 지정을 모두 글로 풀어 써야 함. ChatGPT와 차별점이 없음 |
| B. 번호 스케치 직접 생성 | 영역 번호를 표시한 스케치 + 영역별 설명 + 참조 이미지를 함께 넘겨 한 번에 생성 | 1회 | 영역별 입력 UX를 유지하면서 A와 같은 속도와 비용 | 초안 확인 단계가 없어 결과를 보기 전에는 영역별 수정이 어려움. 영역 번호와 지시를 모델이 정확히 대응시키는지 검증 필요 |
| C. 초안 후 조화 | 영역별로 이미지를 생성해 붙인 초안을 만들고, 이를 조화롭게 재생성 (기존 기획) | 영역 수 + 1회 | 초안을 확인하고 영역 단위로 고칠 수 있음. 레이아웃 지시가 가장 구체적 | 가장 느리고 비쌈. 초안의 이질감이 최종 결과에 남을 수 있음 |

- 영역 감지(①)는 B안과 C안에서만 쓰이며, 용도는 영역별 입력창 생성과 번호 표시다.
- B가 C와 비슷한 품질을 낸다면, 초안 단계를 빼고 영역별 입력 UX만 유지하는 쪽이 더 빠르고 저렴하다.
- B에서 번호가 표시된 스케치가 최종 이미지에 그대로 그려지지 않는지도 확인해야 한다.

---

## 5. 시스템 구성안 (GCP)

| 역할 | 구성 |
|---|---|
| 웹·API | Cloud Run |
| 원본·초안·결과 저장 | Cloud Storage |
| 영역 분석·라벨링, 프롬프트 정리 | OpenCV + Vertex AI의 Gemini 또는 Claude |
| 영역별 초안 생성 | `gemini-3.1-flash-image` |
| 최종 조화 | `gemini-3-pro-image` |
| 배경 제거 등 보조 | Cloud Run GPU 또는 VM의 오픈 모델 (필요 시) |

**참고 사항**

- FLUX.2 dev는 비상업 라이선스다. 자체 호스팅으로 상용 서비스에 쓰려면 별도 계약이 필요하다.
- 이미지 모델의 서울 리전(asia-northeast3) 제공 여부는 확인하지 못했다. global endpoint 사용 가능성을 포함해 확인이 필요하다.

---

## 6. 예상 비용

| 항목 | 단가 (제3자 사이트 기준) |
|---|---|
| 영역별 초안 (`gemini-3.1-flash-image`, 1K) | 약 $0.067/장 |
| 최종 조화 (`gemini-3-pro-image`, 1K·2K) | 약 $0.134/장 |
| 최종 조화 (`gemini-3-pro-image`, 4K) | 약 $0.24/장 |

- C안(초안 후 조화): 영역 5개에 최종 후보 3장(2K)이면 KV 1건당 약 $0.7~1 수준이다.
- A안·B안(직접 생성): 초안 비용이 없으므로 최종 후보 3장(2K) 기준 약 $0.4 수준이다.
- 재생성 횟수에 비례해 늘어나므로, C안에서는 영역 단위 재생성과 저해상도 초안으로 비용을 관리한다.

---

## 7. 제안 및 다음 단계

1. **최종 이미지 생성 단계부터 PoC를 진행한다.**
   - 실제 의뢰 사례 10~20건을 `gemini-3-pro-image`로 A·B·C 세 가지 파이프라인(4.5절)에 각각 돌려 비교한다. C안의 초안은 수작업으로 만들어도 된다.
   - 제품 충실도, 레이아웃 유지율, 영역별 지시 반영 정도, 소요 시간과 비용을 측정한다.
   - 같은 사례를 ChatGPT Sketch로도 만들어 품질 기준선으로 삼는다.
   - ①②는 확실히 되는 영역이고, 서비스 성패는 이 단계에서 갈린다.
2. **PoC 결과로 초안 단계 유지 여부를 결정한다.**
   - B안이 C안과 비슷한 품질을 내면 초안 단계를 빼고 영역별 입력 UX만 유지한다.
   - C안이 뚜렷하게 낫다면 초안 단계를 유지하되, 저해상도·저가 모델로 싸고 빠르게 만든다.
   - 초안 단계를 빼더라도 영역별 입력창과 제품 이미지 위치 지정은 ChatGPT Sketch 대비 차별점으로 남는다.
3. **영역 감지 UX를 프로토타이핑한다.**
   - 스케치에서의 Gemini 영역 인식 정확도를 테스트한다.
   - 병합·분할·삭제 UI를 포함한 영역 보정 흐름을 설계한다.
4. **확인이 필요한 항목을 정리한다.**
   - Vertex AI 공식 가격과 리전 제공 여부
   - Imagen 계열 종료 여부 (공식 문서)
   - Gemini 이미지 모델의 투명 배경 출력 지원 여부

---

## 8. 참고 자료

**유사 서비스**

- [Annotations in Krea Edit](https://www.krea.ai/blog/annotations)
- [Krea Edit 문서](https://www.krea.ai/docs/user-guide/features/edit)
- [Krea Sketch to Image](https://www.krea.ai/apps/sketch-to-image)
- [OpenAI Releases ChatGPT Images 2.5 With Sketch (Unite.AI)](https://www.unite.ai/openai-releases-chatgpt-images-2-5-with-sketch-and-two-new-api-models/)
- [ChatGPT Images 2.5: What Changed and How to Use Sketch (FindSkill)](https://findskill.ai/blog/chatgpt-images-2-5-sketch-tool-explained/)
- [ChatGPT Images 2.5: Features, Sketch, and API Models (DataCamp)](https://www.datacamp.com/blog/chatgpt-images-2-5)
- [OpenAI Introduces 4o Image Generation: A Native, Autoregressive Alternative to Diffusion Models](https://medium.com/byte-sized-ai/openai-introduces-4o-image-generation-a-native-autoregressive-alternative-to-diffusion-models-6f17a6db0ad3)
- [Flair AI Pricing (WizCommerce)](https://wizcommerce.com/blog/flair-ai-pricing/)
- [Flair AI Review 2026](https://www.aicentralresources.com/tool/flair-ai)
- [Best AI Image Generators for Marketing 2026](https://www.lilachbullock.com/best-ai-image-generators-marketing-product-shots/)
- [Photoshop Harmonize (Adobe)](https://helpx.adobe.com/photoshop/desktop/repair-retouch/remove-objects-fill-space/blend-subjects-with-harmonize.html)
- [Photoshop Generative Fill 참조 이미지 (Adobe)](https://helpx.adobe.com/photoshop/desktop/create-open-import-images/create-images/use-reference-images-for-consistent-results.html)
- [Lovart AI Review (Designkit)](https://www.designkit.com/blog/lovart-ai-review)
- [Freepik Sketch to Image](https://www.freepik.com/ai/docs/sketch-to-image)
- [Invoke Regional Guidance Layers](https://support.invoke.ai/support/solutions/articles/151000165024-regional-guidance-layers)
- [InvokeAI Commercial Platform Shuts Down](https://softuts.com/invokeai-commercial-platform-shuts-down-open-source-project-continues/)

**모델 및 기술**

- [Gemini 3 Pro Image (Vertex AI 문서)](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/3-pro-image)
- [Gemini API 이미지 생성 문서](https://ai.google.dev/gemini-api/docs/image-generation)
- [Gemini API Image understanding](https://ai.google.dev/gemini-api/docs/image-understanding)
- [Nano-Banana Pro Prompting Guide](https://dev.to/googleai/nano-banana-pro-prompting-guide-strategies-1h9n)
- [Nano Banana Pro Reference Images](https://www.aifreeapi.com/en/posts/nano-banana-pro-reference-images)
- [How to Use Nano Banana for Product Photography](https://medium.com/ai-product-photography/how-to-use-nano-banana-for-product-photography-2025-guide-a0b91c6c928f)
- [FLUX.2 (Black Forest Labs)](https://bfl.ai/blog/flux-2)

**가격 및 서비스 종료 정보**

- [Nano Banana Pricing (BenchLM)](https://benchlm.ai/media-pricing/nano-banana)
- [Gemini 3 Pro Image pricing — Vertex AI (FutureAGI)](https://futureagi.com/llm-cost-calculator/vertex-ai/gemini-3-pro-image/)
- [Google Imagen 4: 2026 Sunset Timeline](https://invideo.io/blog/imagen-ai-image-generator/)
