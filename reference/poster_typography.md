# 포스터 레퍼런스 스터디 (2026-07-03)

## 1. 참고 포스터 정량 분석

| 항목 | 허경훈 KAIST 포스터 | AHLI CHIL 2022 | NeurIPS'22 DynamicD (Bolei Zhou) |
|---|---|---|---|
| 크기 | **A1 세로 594×841mm** | 339×190mm (인쇄시 확대) | 1219×914mm (48×36in 가로) |
| 총 단어수 | **418 words** | 364 words | **120 words** |
| 텍스트 박스 | 40개 | 28개 | 23개 |
| 이미지 | 12개 | 8개 | 다수(표+사진 그리드) |
| 제목 | 44pt | 17pt(→인쇄 ~60pt) | 96pt |
| 저자 | 33pt | 11pt | 72pt |
| 섹션 헤더 | 28–29.4pt (색 바 위 흰 글씨) | 11pt(→~38pt) | 72pt (파랑 볼드) |
| 서브 헤더 | 22.1pt (파랑 볼드) | 7.5pt | 60pt |
| 본문 | **18.4pt 단일** (61개 런 전부 동일) | 7–7.5pt(→24–26pt) | 48–54pt |
| 배경 | 다크 네이비 + 흰 카드(주황 테두리) | 흰 배경 + 색 pill 라벨 | 흰 배경, 세로 구분선 1개 |

### 공통 패턴 (메인 AI 학회 포스터 관행)
1. **폰트 체계가 정확히 4단계**: 제목 > 섹션헤더 > 서브헤더 > 본문(단일 크기). 본문 크기가 여러 개면 지저분해 보임. 폰트는 1–2종.
2. **단어 예산 300–450** (시각 중심 스타일은 120–250). 본문은 완결 문장이 아니라 bullet 구/절.
3. **구성 = IMRAD 변형**: Motivation(불릿 2–3) → Method/Framework(히어로 다이어그램+번호 스텝) → Results/Validation(표·그래프, **볼드 숫자**) → Conclusion(2–3 불릿) → QR/Code + 저자 블록.
4. **강조 규칙**: 키워드만 색·볼드 (허경훈: 빨강=문제, 파랑=방법; DynamicD: 파랑=조작 대상). 본문 안 색 남용 없음.
5. **figure 40–50%, 텍스트 ~20%, 여백 ~30–40%** (UC Davis/NTU 가이드).
6. **읽기 거리 기준**: 1.5–1.8m에서 본문이 읽혀야 함 → A1급에서 본문 ≥18pt, A0급에서 ≥24pt (UC Davis: 6ft=30pt).
7. QR 코드 필수 (code/paper), 상단 모서리 또는 결론 옆.
8. 허경훈 스타일 특징: 섹션마다 알약형 색 헤더바가 카드 상단 중앙에 걸침, 카드 흰 배경+포인트색 테두리, 다크 페이지 배경, Author & Supervisor 블록(사진+QR+#OPENTOWORK 배너).

## 2. 우리 포스터(610×910mm 세로)에 적용할 스펙

| 요소 | 권장 | 기존 v3/arch (문제) |
|---|---|---|
| 제목 | **48–54pt** 볼드 | 30–33pt (너무 작음) |
| 저자 | 26–30pt | 15–17pt |
| 섹션 헤더 | **30–32pt**, 색 바/알약 위 흰 볼드 | 16–19pt |
| 서브 헤더 | 22–24pt 색 볼드 | 없음/혼재 |
| 본문 | **18–20pt 단일 크기**, 좌정렬 | 13–15.5pt 제각각 |
| 캡션 | 14–16pt 이탤릭 | 10.5–12pt |
| 단어 예산 | ≤ 400 | v3 ~470 (축소 필요) |
| 구성 | Motivation → Framework(그림) → 2 Bottlenecks → (Validation/Plan) → SDL 홍보 → Collaborators+QR | 훅배너/중복 밴드 정리 필요 |
| 강조 | 색 2계열(KETI 블루=B1, KIMS 그린=B2) + 빨강/볼드는 문제 문구 한정 | 대체로 준수 |

## 3. Higgsfield 조사 결과
- Higgsfield의 포스터 기능 = [apps/poster](https://higgsfield.ai/apps/poster) **제품 광고 포스터** 생성기, [AI Design Generator](https://higgsfield.ai/ai-design-generator) 4K 이미지 출력. 모두 **납작한 이미지** 출력 — pptx 불가.
- 학술(research) 포스터 제작 사례는 커뮤니티/블로그에서 **확인되지 않음**. 학술 포스터 자동생성은 별도 연구계열(Paper2Poster/PosterAgent, P2P, PosterGen 등 arXiv)이 존재하나 힉스필드와 무관.
- 결론: 힉스필드는 **히어로 비주얼(배경/일러스트) 1–2장 생성용**으로만 활용. 레이아웃·텍스트는 PPTX에서 유지.

## 4. 소스
- 허경훈 실제 포스터 & CHIL 2022 포스터 (assets 제공)
- [zhoubolei/bolei_awesome_posters](https://github.com/zhoubolei/bolei_awesome_posters) — CVPR/NeurIPS 실물 포스터 + pptx
- [NTU LibGuides Poster Text & Fonts](https://libguides.ntu.edu.sg/posterdesign/text-fonts), [UC Davis Poster Design Principles](https://urc.ucdavis.edu/sites/g/files/dgvnsk3561/files/inline-files/General%20Poster%20Design%20Principles%20-%20Handout.pdf)
- [Higgsfield poster app](https://higgsfield.ai/apps/poster), [Higgsfield AI Design Generator](https://higgsfield.ai/ai-design-generator)
