import streamlit as st
import requests
import subprocess
import time
import socket

API_BASE = "http://localhost:8000"
API_KEY = "guardian-secret-key-2026"
HEADERS = {"X-API-Key": API_KEY}

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Streamlit Cloud 등에서 백엔드가 안 켜져있을 때 자동 실행
if not is_port_in_use(8000):
    with st.spinner("Starting Backend Server..."):
        # uvicorn 실행 (백그라운드)
        subprocess.Popen(["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"])
        time.sleep(3) # 서버가 뜰 때까지 잠시 대기

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
            
            # 마스킹 전/후 비교 UI 추가
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**원본 텍스트 (시뮬레이션)**")
                st.caption("내부 에이전트가 생성한 원본 데이터")
                # Mock 원본 데이터를 추정하여 표시 (데모용)
                raw_sim = data["response"].replace("<KR_RRN>", "900101-1234567").replace("<KR_PHONE_NUMBER>", "010-1234-5678").replace("<PERSON>", "John Kim")
                st.code(raw_sim, language="text")
            with col_b:
                st.markdown("**🛡️ 마스킹된 결과 (The Guardian)**")
                st.caption("외부 에이전트에게 전달되는 안전한 데이터")
                st.code(data["response"], language="text")
                
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
            
            # 승인 후 결과 비교 표시
            st.markdown("### 📋 최종 처리 결과")
            st.code(result.get("response", ""), language="text")
            
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
