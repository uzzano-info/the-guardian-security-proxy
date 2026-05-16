# 🛡️ The Guardian (A2A Security Proxy) — Final Plan v7

**부제:** Google A2A Protocol v1.0 및 OWASP Top 10 For Agentic Applications 기반 에이전트 간 통신 보안 게이트웨이
**목적:** AI Agent Engineer 채용(금융권 및 엔터프라이즈) 포트폴리오용
**전략:** 구현 난이도를 최소화하여 **2주 내 핵심 기능만 완성**하고 취업 활동 즉시 시작.
**최종 검토일:** 2026-05-16 (v7 — 전체 진행 상태 최종 동기화)

---

## 📊 진행 상태 (Progress Tracker)

### ✅ 완료된 작업
| # | 작업 | 계획 일정 | 완료일 | 상태 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | FastAPI 프록시 서버 뼈대 + CORS 설정 | W1 Day 1 | 2026-05-16 | ✅ |
| 2 | A2A Agent Card (`agent-card.json`) v1.0 구현 | W1 Day 1 | 2026-05-16 | ✅ |
| 3 | API Key 인증 미들웨어 (ASI10) | W1 Day 1 | 2026-05-16 | ✅ |
| 4 | Mock 내부 에이전트 API 구현 | W1 Day 2 | 2026-05-16 | ✅ |
| 5 | Presidio PII 마스킹 + 한국어 커스텀 Recognizer (ASI07) | W1 Day 3~4 | 2026-05-16 | ✅ |
| 6 | 룰 기반 프롬프트 인젝션 필터 (ASI01) | W1 Day 5 | 2026-05-16 | ✅ |
| 7 | LangGraph StateGraph + HITL interrupt() (ASI08) | W2 Day 1~2 | 2026-05-16 | ✅ |
| 8 | FastAPI ↔ LangGraph 연동 엔드포인트 (/a2a/request, /resume) | W2 Day 2 | 2026-05-16 | ✅ |
| 9 | Streamlit 보안 관제 대시보드 | W2 Day 3~4 | 2026-05-16 | ✅ |
| 10 | README.md (Mermaid 다이아그램, 기술 스택, 설치 가이드) | W2 Day 5 | 2026-05-16 | ✅ |
| 11 | requirements.txt 생성 | W2 Day 5 | 2026-05-16 | ✅ |
| 12 | 자동화 테스트 스크립트 (tests/test_scenarios.py) | — | 2026-05-16 | ✅ 보너스 |
| 13 | 보안 이벤트 로깅 (`security/logger.py` + JSONL 감사 추적) | — | 2026-05-16 | ✅ |
| 14 | README.md 향후 계획(Future Work) 섹션 추가 | — | 2026-05-16 | ✅ |
| 15 | .gitignore 생성 | — | 2026-05-16 | ✅ |
| 16 | Git 초기화 + 첫 커밋 | — | 2026-05-16 | ✅ |
| 18 | Streamlit 마스킹 전/후 비교 UI | — | 2026-05-16 | ✅ |

### 🔲 남은 작업
| # | 작업 | 우선순위 | 예상 소요 |
| :--- | :--- | :--- | :--- |
| 16b | **GitHub Remote Push** — `git remote add origin` → `git push` | 🔴 높음 | 10분 |
| 17 | **시연 GIF 2종 녹화** — (1)정상 PII 마스킹 (2)공격 차단 HITL | 🟡 중간 | 30분 |
| 19 | **기술 블로그 포스팅** — "OWASP ASI 2026 기반 에이전트 프록시 구축기" | 🟢 낮음 | 2시간 |

---

## 🎯 프로젝트 목표

외부 에이전트가 내부 에이전트의 데이터에 접근할 때, **A2A v1.0 스펙에 맞는 Agent Card 기반 인증**을 수행하고, **PII 마스킹 및 인젝션 방어**를 강제하는 보안 프록시 시스템 구축.

**어필 포인트:**
> "단순히 LLM을 쓰는 것을 넘어, 최신 에이전트 간 통신(A2A) 표준과 2026년 발표된 OWASP Agentic Security Issues(ASI)를 완벽하게 이해하고 아키텍처에 녹여낸 엔지니어."

---

## 💡 빠른 구현 전략

### Mock API 활용 (기존 프로젝트와 코드 분리)
기존 `Auto_Weekly_Report` 코드와 직접 연동하지 않습니다.
FastAPI 내부에 **가짜(Dummy) 주간 보고서 데이터를 반환하는 Mock 함수**를 만들어 독립적으로 구동합니다.

- **포트폴리오 스토리:** "이 프록시는 내부망에 위치한 '자동 주간 보고서 에이전트'를 외부의 무분별한 접근과 데이터 유출로부터 보호합니다."
- **실제 코드:** Mock 내부 에이전트 → 기존 코드 의존성 없이 독립 실행.

### 아키텍처 결정: FastAPI + Streamlit 분리 구조
FastAPI(백엔드)와 Streamlit(프론트엔드)를 **같은 프로세스에서 실행하지 않습니다.**
독립된 두 서비스로 분리하고, Streamlit이 FastAPI의 엔드포인트를 HTTP로 호출하는 구조를 채택합니다.

```
guardian-proxy/
├── backend/          # FastAPI (A2A 프록시 서버)
│   ├── __init__.py
│   ├── main.py
│   ├── workflow.py
│   └── security/
│       ├── __init__.py
│       ├── pii_masking.py
│       ├── injection_filter.py
│       └── logger.py
├── frontend/         # Streamlit (보안 관제 대시보드)
│   └── app.py
├── tests/            # 자동화 테스트
│   └── test_scenarios.py
├── logs/             # 보안 이벤트 로그 (JSONL)
├── .gitignore
├── README.md
└── requirements.txt
```

> 이유: 2주 패스트 트랙에서는 Docker 없이 **터미널 2개**로 각각 실행하면 충분합니다.
> 면접에서는 "프로덕션에서는 docker-compose로 오케스트레이션합니다"라고 설명합니다.

---

## ⚠️ 사전 결정 사항 (착수 전 확인 완료)

### 1. PII 마스킹 언어 전략
Microsoft Presidio는 **한국어 PII를 기본 지원하지 않습니다.**

**✅ 채택 전략: 영어 보고서 + 한국 포맷 커스텀 Recognizer**
- 보고서 본문, 이름, 이메일 → **영어 데이터** (Presidio 기본 동작)
- 주민등록번호, 한국 전화번호 → **정규식 커스텀 `PatternRecognizer`** 추가

**⚠️ 엔티티 타입별 개별 Recognizer 분리** (Presidio Best Practice):
```python
from presidio_analyzer import Pattern, PatternRecognizer

# ✅ 주민등록번호 전용 Recognizer
kr_rrn_pattern = Pattern(
    name="kr_rrn", regex=r"\d{6}-[1-4]\d{6}", score=0.9
)
kr_rrn_recognizer = PatternRecognizer(
    supported_entity="KR_RRN",
    patterns=[kr_rrn_pattern]
)

# ✅ 한국 전화번호 전용 Recognizer
kr_phone_pattern = Pattern(
    name="kr_phone", regex=r"01[016789]-\d{3,4}-\d{4}", score=0.85
)
kr_phone_recognizer = PatternRecognizer(
    supported_entity="KR_PHONE_NUMBER",
    patterns=[kr_phone_pattern]
)
```

> 엔티티를 분리해야 Anonymizer에서 주민번호는 `000000-0000000`, 전화번호는 `010-0000-0000` 등 타입별 마스킹 전략을 다르게 적용할 수 있습니다.

### 2. A2A Agent Card 스펙 준수 (v1.0 — 2026년 4월 Stable 출시)

> ⚠️ A2A v0.3은 레거시(Draft)로 분류됨. 2026년 4월 v1.0이 Linux Foundation을 통해 정식 출시되었으므로 v1.0 기준으로 구현합니다.

공식 스펙 필수 필드: `name`, `description`, `version`, `protocolVersion`, `url`, `skills[]`

> ⚠️ **v1.0 Breaking Change:** Agent Card 경로가 `/.well-known/agent.json` (v0.3) → **`/.well-known/agent-card.json`** (v1.0)으로 변경됨 (IANA RFC 8615 준수).

**인증 필드:** OpenAPI Specification(OAS 3.x) 호환 `securitySchemes` 형식 사용:

```json
{
  "name": "The Guardian - Security Proxy",
  "description": "A2A 보안 게이트웨이: PII 마스킹 및 프롬프트 인젝션 방어",
  "version": "1.0.0",
  "protocolVersion": "1.0.0",
  "url": "http://localhost:8000",
  "capabilities": {
    "streaming": false,
    "pushNotifications": false
  },
  "skills": [
    {
      "id": "pii-masking",
      "name": "PII Masking",
      "description": "응답 내 개인식별정보(PII)를 자동 비식별화합니다."
    },
    {
      "id": "injection-detection",
      "name": "Prompt Injection Detection",
      "description": "프롬프트 인젝션 공격 페이로드를 탐지하고 차단합니다."
    },
    {
      "id": "human-approval",
      "name": "Human Approval Gate",
      "description": "고위험 요청에 대해 관리자 승인을 요구합니다."
    }
  ],
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain"],
  "securitySchemes": {
    "apiKey": {
      "type": "apiKey",
      "in": "header",
      "name": "X-API-Key"
    }
  },
  "security": [{ "apiKey": [] }]
}
```

### 3. A2A 공식 Python SDK → 2주 패스트 트랙에서는 스킵
FastAPI로 직접 구현하되, Agent Card JSON만 A2A v1.0 스펙에 맞춥니다.

### 4. LangGraph HITL 패턴 → 최신 `interrupt()` + `Command(resume=)` 사용
- 구식: `interrupt_before` / `interrupt_after` (디버깅 전용)
- **최신:** `interrupt(payload)` → `Command(resume=value)` (동적 중단/재개)
- 주의: `interrupt()`를 `try/except` 안에 넣으면 안 됨 (내부적으로 예외를 활용하기 때문)
- 개발용: `MemorySaver` Checkpointer + `thread_id` 기반 상태 관리
- 프로덕션 권장: `PostgresSaver` (README "향후 계획"에 명시)

### 5. OWASP 용어 정확성: Top 10 For Agentic Applications (2026 최신 스펙) ✅
기존 단순 LLM Top 10이 아닌, 에이전트 특화 취약점 가이드라인인 **OWASP ASI 2026**을 프로젝트 코어 방어 모델로 채택합니다.
- **ASI01 (Agent Goal Hijack) 대응:** 프롬프트 인젝션을 통한 목표 변조 시도를 룰 기반 필터로 차단.
- **ASI07 (Insecure Inter-Agent Communication) 대응:** A2A v1.0 Agent Card 스펙을 활용한 안전한 통신 규격 확립 및 PII 마스킹 처리로 타 에이전트로의 민감정보 유출 방지.
- **ASI08 (Cascading Failures) 대응:** 위험 요청 감지 시 LangGraph `interrupt()`를 활용한 Human-in-the-Loop 중재로 연쇄적인 시스템 장애/오염 확산 방지.
- **ASI10 (Rogue Agents) 방어:** 인가되지 않았거나 신뢰할 수 없는 외부 에이전트의 접근을 프록시 레이어에서 통제.

---

## ⚡ 주차별 진행 계획 (2주 패스트 트랙)

### 🚀 Week 1: 프록시 뼈대 + Agent Card + PII 마스킹 ✅ 완료

> 보안 게이트웨이의 뼈대와 A2A 핵심 컴포넌트, 개인정보 필터링을 1주차에 끝냅니다.

**Day 1: FastAPI 프록시 서버 뼈대 + A2A Agent Card (ASI07, ASI10 대응)** ✅
- `backend/` 디렉토리에 FastAPI 프로젝트 초기화 및 GitHub Repo 생성.
- `GET /.well-known/agent-card.json` 엔드포인트 구현 (위 v1.0 Agent Card 스펙 참조).
- `securitySchemes` 기반 API Key 인증 미들웨어 적용.
- CORS 미들웨어 설정 (Streamlit 프론트엔드에서 접근 허용).

**Day 2: Mock 내부 에이전트 API 구현** ✅
- 영어 보고서 + 한국 주민번호/전화번호가 혼합된 가짜 주간 보고서 JSON 반환하는 내부 Mock 엔드포인트.
- `POST /a2a/request` → The Guardian → 내부 Mock → 응답 의 기본 HTTP 라우팅 확인.

**Day 3~4: Microsoft Presidio PII 마스킹 미들웨어 (ASI07 대응)** ✅
- `presidio-analyzer`, `presidio-anonymizer` 설치 및 연동.
- `KR_RRN` (주민등록번호)과 `KR_PHONE_NUMBER` (전화번호)를 **별도 Recognizer**로 등록.
- Mock 보고서 내 민감 정보를 `<PERSON>`, `<PHONE_NUMBER>`, `<KR_RRN>`, `<KR_PHONE_NUMBER>` 등으로 자동 치환.

**Day 5: 룰 기반 목표 변조/인젝션 차단 (ASI01 대응)** ✅
- 요청 페이로드에 금지어(`"ignore previous instructions"`, `"reveal system prompt"` 등)가 포함되면 HITL 게이트로 전환하는 필터.

---

### 🧠 Week 2: LangGraph HITL + 대시보드 + 문서화 ✅ 핵심 완료 / 🔲 잔여 작업 있음

> 에이전틱 워크플로우를 구현하고, 면접관이 볼 결과물을 완성합니다.

**Day 1~2: LangGraph 노드 변환 + HITL `interrupt()` 도입 (ASI08 대응)** ✅
- 보안 파이프라인을 LangGraph StateGraph 노드로 재구성:
  ```
  [인젝션 검사] → [HITL 승인 게이트] → [내부 에이전트 + PII 마스킹] → [응답]
  ```
- 고위험 요청 시 `interrupt()` 로 실행 중단, `Command(resume="approve"/"reject")` 로 재개.
- `MemorySaver` Checkpointer + `thread_id` 기반 상태 보존.

**Day 3~4: Streamlit 보안 관제 대시보드 (`frontend/`)** ✅
- FastAPI의 상태 API를 호출하여 `interrupt` 대기 중인 요청 목록 표시.
- **[승인] / [거절]** 버튼 → FastAPI로 `Command(resume=)` 전달 → 파이프라인 재개.

**Day 5: 문서화 및 시연 영상 제작 (최종)** ✅ 핵심 완료
- `README.md` 완성: ✅
  - ✅ Mermaid.js 아키텍처 다이아그램 (A2A 통신 흐름 시각화)
  - ✅ "Google A2A Protocol **v1.0** Agent Card 스펙 준수" 명시
  - ✅ OWASP ASI 2026 방어 명시
  - ✅ 향후 계획(Future Work) 섹션 추가 완료
- ✅ 보안 이벤트 로깅 (`security/logger.py` + JSONL 감사 추적)
- 🔲 시연 GIF/영상 2종 녹화 (사용자 직접 수행)

---

### 🆕 추가 작업 상세

**#16b. GitHub Remote Push** 🔴 높음
- 로컬 Git 리포지토리는 초기화 완료 → GitHub에 Remote 리포지토리를 생성하고 `git push` 수행.
- **사용자 직접 수행** 필요: GitHub 인증(SSH Key 또는 Personal Access Token).

**#17. 시연 GIF 2종 녹화** 🟡 중간
- (1) 정상 PII 마스킹 시나리오
- (2) 공격 차단 HITL 시나리오
- **사용자 직접 수행** 필요: 화면 녹화 도구(예: macOS 기본 녹화 또는 Kap).

**#19. 기술 블로그 포스팅** 🟢 낮음 (선택)
- 튜토리얼(`The_Guardian_Tutorial.md`)의 내용을 기반으로 블로그 시리즈 작성.
- "OWASP ASI 2026을 대비하는 에이전트 프록시 구축기" 주제 추천.

---

## 🛠️ 기술 스택

| 역할 | 기술 | 선택 이유 |
| :--- | :--- | :--- |
| API 서버 / 프록시 | **FastAPI** | 빠른 구현, Agent Card 직접 노출 |
| PII 마스킹 | **Microsoft Presidio** | 산업 표준, 커스텀 Recognizer 확장 가능 |
| 워크플로우 / HITL | **LangGraph** | `interrupt()` 기반 연쇄 장애(Cascading Failure) 방지 |
| 관제 대시보드 | **Streamlit** | 기존 프로젝트와 동일 스택, 빠른 UI |
| 통신 표준 | **Google A2A Protocol v1.0** | Agent Card 기반 에이전트 Discovery (2026.04 Stable) |
| 보안 기준 | **OWASP ASI 2026** | ASI01, ASI07, ASI08 대응으로 완벽한 에이전트 특화 방어망 구축 |

---

## 💡 이력서 반영용 핵심 문구

> "Google A2A Protocol v1.0 스펙에 준거한 Agent Card(`/.well-known/agent-card.json`)를 구현하고, 최신 **OWASP Top 10 for Agentic Applications(2026)** 가이드라인을 기반으로 ASI01(Goal Hijack 방어) 및 ASI07(PII 비식별화)을 FastAPI 미들웨어로 적용했으며, LangGraph의 `interrupt()` 패턴을 도입하여 ASI08(Cascading Failures)을 방지하는 Human-in-the-Loop 중재 시스템을 구축."

---

## 📋 리스크 및 완화 방안

| 리스크 | 영향 | 완화 방안 |
| :--- | :--- | :--- |
| Presidio 설치 시 spaCy 모델 다운로드 오류 | Week 1 지연 | ✅ 해결: `SpacyNlpEngine(models=[...en_core_web_sm...])` 명시 설정 |
| LangGraph `interrupt()` + Streamlit 연동 시 상태 동기화 이슈 | Week 2 지연 | ✅ 해결: `session_state`에 `thread_id` 저장, `state.next` 보조 체크 |
| Mock 데이터가 너무 단순해 보이는 리스크 | 포트폴리오 인상 저하 | ✅ 해결: 마스킹 전/후 비교 UI 구현 완료 |
| A2A v1.0 세부 스키마 변동성 | 스펙 불일치 | ✅ 해결: v1.0 Stable 기준 구현 완료, `agent-card.json` 경로 확인 |

