from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid

app = FastAPI(title="The Guardian Proxy")

# ── CORS 설정 (Streamlit 프론트엔드와의 통신 허용) ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Key 인증 (ASI10: Rogue Agent 방어) ──
VALID_API_KEY = "guardian-secret-key-2026"

async def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

# ── A2A Agent Card (v1.0 스펙) ──
@app.get("/.well-known/agent-card.json")
async def get_agent_card():
    return {
        "name": "The Guardian - Security Proxy",
        "description": "A2A 보안 게이트웨이: PII 마스킹 및 프롬프트 인젝션 방어",
        "version": "1.0.0",
        "protocolVersion": "1.0.0",
        "url": "http://localhost:8000",
        "capabilities": {
            "streaming": False,
            "pushNotifications": False
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
        "security": [{"apiKey": []}]
    }

# ── 요청 스키마 정의 (Pydantic BaseModel 사용) ──
class AgentRequest(BaseModel):
    query: str

# ── Mock 내부 에이전트 ──
@app.post("/internal/generate-report")
async def mock_internal_agent(request: AgentRequest):
    """실제 환경에서는 여기서 사내 DB나 LLM을 호출합니다."""
    dummy_report = (
        "Weekly Performance Report\n"
        f"Subject: {request.query}\n"
        "Prepared by: John Kim (김존)\n"
        "SSN: 900101-1234567\n"
        "Phone: 010-1234-5678\n"
        "Email: john.kim@company.com\n"
        "Summary: All tasks completed successfully."
    )
    return {"data": dummy_report}

from langgraph.types import Command
from backend.workflow import graph

# ── [핵심] 외부 에이전트 요청 진입점 ──
@app.post("/a2a/request")
async def handle_a2a_request(
    request: AgentRequest,
    x_api_key: str = Header(None)
):
    """외부 에이전트의 요청을 받아 보안 파이프라인을 실행합니다."""
    await verify_api_key(x_api_key)

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    # invoke()는 interrupt 발생 시 즉시 반환됩니다 (blocking 아님)
    result = graph.invoke(
        {"request": request.query, "is_safe": True, "response": "", "risk_detail": ""},
        config=config
    )

    # interrupt 상태 확인 (state.next가 비어있지 않으면 아직 완료되지 않은 것)
    state = graph.get_state(config)
    if state.next or (state.tasks and any(t.interrupts for t in state.tasks)):
        return {
            "status": "paused",
            "thread_id": thread_id,
            "interrupt_data": state.tasks[0].interrupts[0].value
        }

    return {
        "status": "complete",
        "thread_id": thread_id,
        "response": result.get("response", "")
    }


# ── [핵심] HITL 승인/거절 엔드포인트 ──
class ResumeAction(BaseModel):
    action: str  # "approve" 또는 "reject"

@app.post("/resume/{thread_id}")
async def resume_workflow(thread_id: str, body: ResumeAction):
    """Streamlit 대시보드에서 승인/거절 시 호출됩니다."""
    config = {"configurable": {"thread_id": thread_id}}

    result = graph.invoke(
        Command(resume=body.action),
        config=config
    )

    return {
        "status": "complete",
        "response": result.get("response", "")
    }


# ── 대기 중인 요청 목록 조회 (Streamlit용) ──
@app.get("/pending-requests")
async def get_pending_requests():
    """interrupt 상태인 thread 목록을 반환합니다.
    (간략화: 실제로는 DB 기반 관리가 필요하지만 데모용으로 메모리 기반)
    """
    # 프로덕션에서는 PostgresSaver + 쿼리로 구현
    return {"message": "Use /a2a/request to create requests, check thread_id from response"}
