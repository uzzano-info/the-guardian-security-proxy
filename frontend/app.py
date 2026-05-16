import streamlit as st
import requests

API_BASE = "http://localhost:8000"
API_KEY = "guardian-secret-key-2026"
HEADERS = {"X-API-Key": API_KEY}

st.set_page_config(page_title="The Guardian Dashboard", page_icon="🛡️")
st.title("🛡️ The Guardian — 보안 관제 대시보드")

# ── 섹션 1: 외부 에이전트 요청 시뮬레이션 ──
st.subheader("📤 에이전트 요청 보내기")
query = st.text_input("프롬프트 입력:", placeholder="예: 이번 주 실적 보고서를 요약해줘")

if st.button("요청 전송"):
    if query:
        resp = requests.post(
            f"{API_BASE}/a2a/request",
            json={"query": query},
            headers=HEADERS
        )
        data = resp.json()

        if data["status"] == "complete":
            st.success("✅ 정상 처리 완료")
            st.text_area("마스킹된 응답:", value=data["response"], height=200)
        elif data["status"] == "paused":
            st.warning("⚠️ 고위험 요청 감지! 관리자 승인이 필요합니다.")
            st.json(data["interrupt_data"])
            # thread_id를 session_state에 저장
            st.session_state["pending_thread_id"] = data["thread_id"]

st.divider()

# ── 섹션 2: 관리자 승인/거절 ──
st.subheader("🔒 대기 중인 요청 처리")

if "pending_thread_id" in st.session_state:
    thread_id = st.session_state["pending_thread_id"]
    st.info(f"Thread ID: `{thread_id}`")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ 승인 (Approve)"):
            resp = requests.post(
                f"{API_BASE}/resume/{thread_id}",
                json={"action": "approve"}
            )
            result = resp.json()
            st.success("승인 완료!")
            st.text_area("마스킹된 응답:", value=result.get("response", ""), height=200)
            del st.session_state["pending_thread_id"]

    with col2:
        if st.button("🚫 거절 (Reject)"):
            resp = requests.post(
                f"{API_BASE}/resume/{thread_id}",
                json={"action": "reject"}
            )
            result = resp.json()
            st.error("차단 완료!")
            st.write(result.get("response", ""))
            del st.session_state["pending_thread_id"]
else:
    st.write("현재 대기 중인 요청이 없습니다.")
