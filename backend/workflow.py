from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from typing import TypedDict

from backend.security.injection_filter import check_injection
from backend.security.pii_masking import mask_pii
from backend.security.logger import log_security_event


class SecurityState(TypedDict):
    request: str
    is_safe: bool
    response: str
    risk_detail: str


def injection_node(state: SecurityState):
    """ASI01 방어: 프롬프트 인젝션 검사"""
    is_safe = not check_injection(state["request"])
    risk_detail = "" if is_safe else f"Blocked pattern detected in: {state['request'][:50]}..."
    
    if not is_safe:
        log_security_event("INJECTION_DETECTED", {"request": state["request"], "detail": risk_detail})
        
    return {"is_safe": is_safe, "risk_detail": risk_detail}


def hitl_node(state: SecurityState):
    """ASI08 방어: 위험 요청 시 관리자 승인 대기"""
    if not state["is_safe"]:
        # interrupt()로 실행 중단 — 외부에서 Command(resume=) 로 재개할 때까지 대기
        action = interrupt({
            "message": "⚠️ High risk request detected. Approve or Reject?",
            "detail": state["risk_detail"]
        })
        
        log_security_event("HITL_DECISION", {"action": action, "risk_detail": state["risk_detail"]})
        
        if action == "reject":
            return {"response": "🚫 Request Blocked by Admin"}
    return {}


def agent_node(state: SecurityState):
    """내부 에이전트 호출 + PII 마스킹"""
    # Mock 보고서 생성
    raw_report = (
        "Weekly Performance Report\n"
        f"Subject: {state['request']}\n"
        "Prepared by: John Kim (김존)\n"
        "SSN: 900101-1234567\n"
        "Phone: 010-1234-5678\n"
        "Email: john.kim@company.com\n"
        "Summary: All tasks completed successfully."
    )
    # PII 마스킹 적용
    masked_report = mask_pii(raw_report)
    
    log_security_event("PII_MASKING_APPLIED", {"request": state["request"]})
    
    return {"response": masked_report}


def route_after_hitl(state: SecurityState):
    """조건부 라우팅: 거절되면 바로 END, 승인되면 agent로 이동"""
    if state.get("response") == "🚫 Request Blocked by Admin":
        return END
    return "agent"


# ── 그래프 조립 ──
builder = StateGraph(SecurityState)
builder.add_node("injection", injection_node)
builder.add_node("hitl", hitl_node)
builder.add_node("agent", agent_node)

builder.add_edge(START, "injection")
builder.add_edge("injection", "hitl")
builder.add_conditional_edges("hitl", route_after_hitl)
builder.add_edge("agent", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
