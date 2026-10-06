# 객관적 음질 검사(A1) 벤치마크 결과 — 2026-10-06

`review_anomaly_v2` M2-4 구현(원본 PCM의 DSP 측정, **모델 호출 0회**)을 사용자 제작 벤치마크로 측정한 결과다.
원자료는 같은 폴더의 `reports.json`(파일별 전체 리포트), 라벨은 `benchmarks/label.json`.

> **주의** — 임계값은 이 자료(정상 16개·결함 16개)를 보고 정한 **잠정값**이다. 같은 자료로 잰 수치이므로
> 일반 성능이 아니며, 새 자료로 재검증하기 전에는 게이트 통과로 보지 않는다.

## 1. 한눈에 보기

| 구분 | 결과 |
|---|---|
| 음질 결함 파일 16개 — 라벨된 결함을 **warning 이상**으로 짚은 것 | **11 / 16** |
| 정상 파일 16개 — warning 이상 지적(오탐 후보) | **2건 = 0.125건/미디어** (`review_required` 2개) |
| 정상 파일의 info(참고) 지적 | 57건 = 3.56건/미디어 — 대부분 음악 다이내믹에 따른 음량 변화 관찰 |
| 영상 결함 파일 16개(음성은 원본 유지) | 원본과 같은 결과 — 음질 검사가 영상 열화에 반응하지 않음(정상 동작) |
| 처리 시간(파일당, S0 전처리 포함) | 최소 8.6초 · 중앙값 13.3초 · 최대 30.1초 (음질 계산 자체는 0.3~4초) |

### 결함 유형별

| 결함 유형 | 파일 수 | warning 이상 검출 | 비고 |
|---|---|---|---|
| 무음 구간(4~5초) | 1 | 1 / 1 | critical — 페이드가 아닌 급한 끊김 |
| 히스 잡음(8~9초) | 1 | 1 / 1 | 대역 평탄도·고역비가 함께 뚜렷 |
| 하드 클리핑(12초~끝) | 1 | 1 / 1 | 풀스케일 아래에서 잘린 클립 — 파고율·평탄 비율로 검출 |
| 모노 변환 | 4 | 4 / 4 | 채널 수 1 < 기준 2 (잠정 기준) |
| 샘플레이트 24kHz | 4 | 4 / 4 | 24000Hz < 기준 44100Hz (잠정 기준) |
| 비트레이트 96kbps | 4 | 0 / 4 | **정책상 미대조** — 정상 시드 5개가 65~80kbps라 기준선을 그을 수 없다(§4-①). 측정값은 리포트에 나온다 |
| 볼륨 램프(12~16초 +6dB) | 1 | 0 / 1 | 참조 없이는 음악 크레셴도와 구분 불가(§4-②). 일부 피크 포화 0.6ms는 info |

## 2. 음질 결함 파일별 결과 (`benchmarks/ng/audio/`)

| 파일 | 라벨(결함 내용 · 위치) | 결과 | 검출 내용 | 그 밖의 warning 이상 지적 |
|---|---|---|---|---|
| `GalaxyTabS12Ultra_Design_down_audio_bitrate` | 음성 비트레이트를 약 192kbps에서 목표 96kbps로 낮춤. 48kHz·스테레오·영상은 원본 유지. · **00** | ❌ 미검출 | 해당 유형의 지적 없음 | — |
| `GalaxyTabS12Ultra_Design_down_audio_channels` | 음성 채널을 스테레오(2채널)에서 모노(1채널)로 변경. 48kHz 유지, 음성 비트레이트 목표 192kbps. 영상은 원본 유지. · **00** | ✅ 검출 | 🟠 warning · 0.00~15.02초 — 채널 수 1(mono)가 기준 2채널 미만 (납품 기준은 잠정값) | — |
| `GalaxyTabS12Ultra_Design_down_audio_mute` | 4초 이상~5초 미만 구간을 무음 처리. 영상은 원본 유지. · **4초~5초** | ✅ 검출 | 🔴 critical · 4.00~5.00초 — 4.005~4.995초(990ms) 소리가 급격히 끊겼다 — 직전 대비 156dB 급락, 직후 162dB 급등 (페이드가 아님) | — |
| `GalaxyTabS12Ultra_Design_down_audio_samplerate` | 음성 샘플레이트를 48kHz에서 24kHz로 낮춤. 스테레오 유지, 음성 비트레이트 목표 192kbps. 영상은 원본 유지. · **00** | ✅ 검출 | 🟠 warning · 0.00~15.02초 — 샘플레이트 24000 Hz가 기준 44100 Hz 미만 — 재생 대역이 12 kHz로 제한된다 (납품 기준은 잠정값) | — |
| `GalaxyTabS12Ultra_Display_down_audio_bitrate` | 음성 비트레이트를 약 192kbps에서 목표 96kbps로 낮춤. 48kHz·스테레오·영상은 원본 유지. · **00** | ❌ 미검출 | 해당 유형의 지적 없음 | 음량 급변(warning, 10.90~11.30초) |
| `GalaxyTabS12Ultra_Display_down_audio_channels` | 음성 채널을 스테레오(2채널)에서 모노(1채널)로 변경. 48kHz 유지, 음성 비트레이트 목표 192kbps. 영상은 원본 유지. · **00** | ✅ 검출 | 🟠 warning · 0.00~16.04초 — 채널 수 1(mono)가 기준 2채널 미만 (납품 기준은 잠정값) | 음량 급변(warning, 10.90~11.30초) |
| `GalaxyTabS12Ultra_Display_down_audio_samplerate` | 음성 샘플레이트를 48kHz에서 24kHz로 낮춤. 스테레오 유지, 음성 비트레이트 목표 192kbps. 영상은 원본 유지. · **00** | ✅ 검출 | 🟠 warning · 0.00~16.04초 — 샘플레이트 24000 Hz가 기준 44100 Hz 미만 — 재생 대역이 12 kHz로 제한된다 (납품 기준은 잠정값) | 음량 급변(warning, 10.90~11.30초) |
| `GalaxyTabS12Ultra_Display_down_audio_volume_ramp` | 12초부터 16초까지 신호 진폭 배율을 1배에서 2배로 선형 증가시키고, 16초 이후 끝까지 2배 유지. 최대치를 넘는 일부 피크에 포화 왜곡 발생. 영상은 원본 유지. · **12초~끝 (12초~16초 선형 증가, 16초 이후 2배 유지)** | ⚠️ info만 | 14.00~14.40초 — 14.20초에서 음량이 -30.5 → -8.4 LUFS (+22.1 LU) 급변 — 곧 되돌아옴 | 음량 급변(warning, 10.90~11.30초) |
| `GalaxyTabS12Ultra_SPen_down_audio_bitrate` | 음성 비트레이트를 약 192kbps에서 목표 96kbps로 낮춤. 48kHz·스테레오·영상은 원본 유지. · **00** | ❌ 미검출 | 해당 유형의 지적 없음 | — |
| `GalaxyTabS12Ultra_SPen_down_audio_channels` | 음성 채널을 스테레오(2채널)에서 모노(1채널)로 변경. 48kHz 유지, 음성 비트레이트 목표 192kbps. 영상은 원본 유지. · **00** | ✅ 검출 | 🟠 warning · 0.00~15.04초 — 채널 수 1(mono)가 기준 2채널 미만 (납품 기준은 잠정값) | — |
| `GalaxyTabS12Ultra_SPen_down_audio_hiss` | 8초부터 9초까지 1.5~10kHz 대역의 명확한 쉬― 잡음을 원래 소리와 혼합. 영상은 원본 유지. · **8초~9초** | ✅ 검출 | 🟠 warning · 8.00~9.00초 — 8.0~9.0초의 조용한 블록이 잡음성이다 — 수준 -12.2 dBFS, 대역 평탄도 0.26, 고역비 +4 dB (참조 없는 추정값) | — |
| `GalaxyTabS12Ultra_SPen_down_audio_samplerate` | 음성 샘플레이트를 48kHz에서 24kHz로 낮춤. 스테레오 유지, 음성 비트레이트 목표 192kbps. 영상은 원본 유지. · **00** | ✅ 검출 | 🟠 warning · 0.00~15.04초 — 샘플레이트 24000 Hz가 기준 44100 Hz 미만 — 재생 대역이 12 kHz로 제한된다 (납품 기준은 잠정값) | — |
| `GalaxyZFold8_Gacha_down_audio_bitrate` | 음성 비트레이트를 약 192kbps에서 목표 96kbps로 낮춤. 48kHz·스테레오·영상은 원본 유지. · **00** | ❌ 미검출 | 해당 유형의 지적 없음 | — |
| `GalaxyZFold8_Gacha_down_audio_channels` | 음성 채널을 스테레오(2채널)에서 모노(1채널)로 변경. 48kHz 유지, 음성 비트레이트 목표 192kbps. 영상은 원본 유지. · **00** | ✅ 검출 | 🟠 warning · 0.00~31.04초 — 채널 수 1(mono)가 기준 2채널 미만 (납품 기준은 잠정값) | — |
| `GalaxyZFold8_Gacha_down_audio_clipping` | 12초부터 끝까지 음성을 증폭한 뒤 하드 클리핑하여 소리가 찢어지는 강한 왜곡 적용. 영상은 원본 유지. · **12초~끝** | ✅ 검출 | 🔴 critical · 12.00~29.50초 — 12.00~29.50초 파형이 평탄하게 잘려 있다(하드 클립) — 파고율 최소 2.5 dB, 평탄 샘플 최대 46.0% (정상 음악은 파고율 8 dB 이상·평탄 1% 이하) | — |
| `GalaxyZFold8_Gacha_down_audio_samplerate` | 음성 샘플레이트를 48kHz에서 24kHz로 낮춤. 스테레오 유지, 음성 비트레이트 목표 192kbps. 영상은 원본 유지. · **00** | ✅ 검출 | 🟠 warning · 0.00~31.04초 — 샘플레이트 24000 Hz가 기준 44100 Hz 미만 — 재생 대역이 12 kHz로 제한된다 (납품 기준은 잠정값) | — |

`Display` 계열 4개에 붙은 "음량 급변(10.9~11.3초)"은 **원본에도 있는 지적**이다(§3) — 주입한 결함이 아니다.

## 3. 정상 파일별 결과 (`benchmarks/seed/normal/`)

| 파일 | 판정 | warning 이상 지적 | info | LUFS | LRA | true peak(dBTP) | 최소 파고율(dB) | 평탄 최대(%) | 포맷 |
|---|---|---|---|---|---|---|---|---|---|
| `GalaxyTabS12Ultra_Design` | no_issue_detected | — | 3 | -16.9 | 2.7 | -0.4/-0.8 | 11.2 | 0.1 | 48kHz stereo 192kbps |
| `GalaxyTabS12Ultra_Display` | review_required | 음량 급변 🟠 warning 10.90~11.30초 | 6 | -15.8 | 19.7 | -1.0/-0.1 | 9.4 | 0.4 | 48kHz stereo 194kbps |
| `GalaxyTabS12Ultra_SPen` | no_issue_detected | — | 2 | -12.7 | 6.2 | +0.1/+0.1 | 8.3 | 1.0 | 48kHz stereo 196kbps |
| `GalaxyZFold8_Gacha` | no_issue_detected | — | 7 | -13.3 | 7.9 | +0.7/+0.7 | 8.8 | 0.9 | 48kHz stereo 195kbps |
| `VD_Multiverse` | review_required | 포화·하드 클립 🔴 critical 0.10~14.05초 | 1 | -5.8 | 4.1 | +5.2/+5.2 | 9.1 | 0.8 | 48kHz stereo 320kbps |
| `ZFold8Ulra_Fundamental_Battery_Flower` | no_issue_detected | — | 2 | -11.9 | 19.0 | -0.1/+0.1 | 10.2 | 0.7 | 48kHz stereo 189kbps |
| `ZFold8Ultra_Fundamental_Battery_Top` | no_issue_detected | — | 4 | -13.8 | 15.7 | +0.0/+0.1 | 10.4 | 0.1 | 48kHz stereo 189kbps |
| `ZFold8Ultra_Fundamental_Processor_Dragon` | no_issue_detected | — | 5 | -12.4 | 9.7 | -0.2/-0.2 | 9.6 | 0.5 | 48kHz stereo 189kbps |
| `ZFold8_Cassette` | no_issue_detected | — | 2 | -14.3 | 11.6 | +0.5/-0.0 | 10.9 | 0.1 | 48kHz stereo 68kbps |
| `ZFold8_Chocolate` | no_issue_detected | — | 6 | -14.3 | 11.8 | +2.1/+0.8 | 10.7 | 0.1 | 48kHz stereo 69kbps |
| `ZFold8_Dog` | no_issue_detected | — | 5 | -14.5 | 8.4 | -0.0/+0.6 | 10.6 | 0.2 | 48kHz stereo 76kbps |
| `ZFold8_Fundamental_Display_Butter` | no_issue_detected | — | 2 | -12.0 | 19.7 | -0.0/-0.1 | 10.6 | 0.5 | 48kHz stereo 189kbps |
| `ZFold8_Fundamental_Lightness_Card` | no_issue_detected | — | 3 | -11.6 | 23.2 | -0.1/-0.1 | 10.4 | 0.3 | 48kHz stereo 189kbps |
| `ZFold8_Fundamental_Lightness_Paper` | no_issue_detected | — | 1 | -12.1 | 7.5 | -0.1/-0.1 | 10.1 | 0.1 | 48kHz stereo 189kbps |
| `ZFold8_Scarf` | no_issue_detected | — | 6 | -15.1 | 17.9 | +0.1/+0.0 | 10.8 | 0.2 | 48kHz stereo 65kbps |
| `ZFold8_SwitchEasier` | no_issue_detected | — | 2 | -14.1 | 2.1 | -2.3/-1.5 | 10.8 | 0.1 | 48kHz stereo 80kbps |

### warning 이상 지적 2건의 내용

- **`GalaxyTabS12Ultra_Display`** — 음량 급변 🟠 warning · 10.90~11.30초
  - 설명: 11.10초에서 음량이 -33.8 → -15.6 LUFS (+18.2 LU) 급변 — 새 수준 유지
  - 정상 대안: 음악의 다이내믹·효과음 시작 등 의도된 음량 변화일 수 있다
  - 근거 수치: `{"delta_lu": 18.17, "before_lufs": -33.8, "after_lufs": -15.63, "before_std_lu": 0.61, "sustained": 1.0, "spectral_similarity": 0.949, "envelope_step_db": 10.31, "at_cut": 0.0}`
- **`VD_Multiverse`** — 포화·하드 클립 🔴 critical · 0.10~14.05초
  - 설명: L+R 채널에서 0.103~14.054초 사이 포화 샘플 합계 1001.2ms(|x| ≥ 0.99, 연속 4샘플 이상)
  - 정상 대안: 리미터·맥시마이저로 의도적으로 눌린 마스터일 수 있다 — 청취로 왜곡 여부 확인
  - 근거 수치: `{"clipped_ms": 1001.17, "clipped_samples": 48056.0}`

- `VD_Multiverse`는 디코딩 샘플이 풀스케일을 넘는 구간이 합계 약 1초이고 true peak가 +5 dBTP를 넘는다. **측정상 사실**이라
  오탐이 아닐 수 있다 — 청취 확인이 필요하다.
- `GalaxyTabS12Ultra_Display`는 조용한 도입부(−34 LUFS) 뒤 음악이 한 번에 들어오는 지점으로 보인다. 의도된 연출이면 오탐이다.

## 4. 결정이 필요한 것

1. **비트레이트 납품 기준** — 정상으로 받은 기존 시드 5개(`ZFold8_Cassette`·`Chocolate`·`Dog`·`Scarf`·`SwitchEasier`)가
   AAC **65~80kbps**로, 결함 라벨 파일(96kbps)보다 낮다. 기준을 128kbps로 두면 정상 5개가 기준 미달이 된다.
   납품 규격의 최소 비트레이트가 정해지면 `config/default.yaml`의 `audio.requirements.min_bitrate_kbps`에 넣는다(현재 `null` — 측정값만 보고).
2. **점진적 볼륨 변화**(4초에 걸친 +6dB)를 검출 대상으로 둘지 — 참조(원본) 없이는 음악의 크레셴도와 신호상 구분되지 않는다. 순간 계단은 검출한다.
3. `VD_Multiverse`의 포화가 실제로 들리는 왜곡인지 청취 확인 — 결함이면 시드 라벨을 고친다.
4. `GalaxyTabS12Ultra_Display` 11.1초의 음량 급변이 의도된 연출인지.
5. 샘플레이트 ≥ 44.1kHz·2채널 기준은 **잠정값**이다(정상 16개 전부 48kHz 스테레오). 규격과 다르면 알려 주면 된다.

## 5. 무엇을 어떻게 재는가

| 검사 | 관측 | warning 이상이 되는 조건(잠정) |
|---|---|---|
| 포화·하드 클립 | ① \|샘플\| ≥ 0.99가 4샘플 이상 연속 ② 0.5초 창의 파고율(피크/RMS)과 평탄 샘플 비율 — 천장 높이와 무관, 순음 제외 | ① 사건 안 포화 합 ≥ 5ms(≥ 100ms critical) ② 평탄 ≥ 2% 창이 2개 이상(사건 ≥ 3초 critical) |
| 끊김 | 5ms RMS 포락선의 무음(< −70 dBFS) | 20ms~5초, 앞뒤에 소리가 있고 경계가 30dB 이상 급락·급등(페이드 제외). 0.5초 이상이면 critical |
| 음량 급변 | 400ms 라우드니스의 앞뒤 0.3초 평균 차 ≥ 12 LU | 앞이 안정적이고, 뒤 1초가 새 수준을 유지하고, 경계 전후 스펙트럼이 닮았고(같은 내용), 5ms 안에 10dB 이상 뛰고, 영상 컷이 아닐 때. 아니면 info |
| 잡음(히스) | 1초 창에서 조용한 블록의 대역 평탄도·고역/저역 비 | 평탄도 ≥ 0.2 그리고 고역비 ≥ +3dB. 그보다 약하면 info |
| 포맷 기준 | 샘플레이트·채널·비트레이트(컨테이너), 좌우 동일 여부 | 샘플레이트 < 44.1kHz, 채널 < 2, 좌우가 사실상 같음. 비트레이트는 기준 미설정 |

- 라우드니스는 ITU-R BS.1770-4(K-weighting·게이트), LRA는 EBU R128, true peak는 4배 오버샘플링.
- 근거는 **구간(초)과 채널**이며 화면 위치(bbox)는 만들지 않는다. 시각은 영상 첫 프레임을 0초로 한 공통 시간축이다.
- 이미지·음원 없는 영상은 `not_applicable`, 오디오 디코딩 실패는 `failed` — 어느 것도 정상으로 처리하지 않는다.
- 측정값은 결함의 충분조건이 아니다. 모든 지적에 정상 대안(리미팅·의도된 무음·음악 다이내믹 등)을 함께 싣는다.

## 6. 한계

- 음량 급변은 음악의 급한 진입과 신호상 겹친다(정상 1건 오탐, 합성 주입 4건 중 2건만 warning).
- 점진적 음량 변화, 손실 압축에 따른 음질 저하(비트레이트)는 참조 없이 판정하지 않는다.
- 잡음 규칙의 여유가 작다 — 정상 파일의 최댓값(평탄도 0.24·고역비 −1dB, 평탄도 0.13·고역비 +1dB)과 실제 히스(0.26·+4dB)가 가깝다.
- 발음·립싱크·음악적 품질은 이 검사의 범위가 아니다(립싱크는 M2-5).
- 결함 16개 중 12개가 포맷 변환이고 내용 결함은 유형당 1개뿐이다 — 유형별 재현율을 말하기엔 표본이 작다.

## 7. 재현

```bash
cd backend/review_anomaly_v2
.venv/bin/python -m review_anomaly_v2.cli audio <파일>     # 파일 1개의 측정 요약·지적 JSON
.venv/bin/python -m pytest -q tests/test_audio.py          # 음질 단위 테스트
```

구현: `review_anomaly_v2/audio/`(decode·measure·checks), 임계: `config/default.yaml`의 `audio:` 절, 설계·실측 기록: `docs/SDP/REVIEW_ANOMALY_V2.md` §2.3 A1 구현.
