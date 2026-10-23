"""Web chat interface.   Run:  streamlit run app.py

The sidebar shows what the agent is doing behind the scenes (tools, draft, cost,
audit log), which is the part to show in a client workshop.
"""

import streamlit as st

from agent311 import classifier, config, data
from agent311.agent import create_agent
from agent311.knowledge import KnowledgeBase

st.set_page_config(page_title="Toronto 311 Assistant (demo)", page_icon="🏙️")


@st.cache_resource(show_spinner="Loading 500,000 Toronto 311 requests...")
def load_everything():
    """Runs once per server start, then Streamlit reuses the result."""
    return data.load_requests(), classifier.load(), KnowledgeBase()


def new_conversation():
    rows, model, knowledge_base = load_everything()
    st.session_state.agent = create_agent(rows=rows, model=model, knowledge_base=knowledge_base)
    st.session_state.chat = []   # list of (role, text) for display


if "agent" not in st.session_state:
    new_conversation()
agent = st.session_state.agent

# ---- Sidebar: behind the scenes ----------------------------------------------
with st.sidebar:
    st.header("Behind the scenes")
    if st.button("New conversation"):
        new_conversation()
        st.rerun()

    st.subheader("Pending draft")
    if agent.toolbox.pending_draft:
        st.json(agent.toolbox.pending_draft)
        st.caption("Waiting for the resident to reply 'yes'. Claude cannot submit on its own.")
    else:
        st.caption("None")

    st.subheader("Tools called")
    st.write(", ".join(agent.audit.tools_called()) or "None yet")

    st.subheader("Cost so far")
    st.write(f"${agent.total_cost_usd:.4f}")

    with st.expander("Audit log"):
        for event in agent.audit.events[-30:]:
            st.json(event, expanded=False)

# ---- Main chat -----------------------------------------------------------------
st.title("Toronto 311 Assistant")
st.caption("Unofficial portfolio demo using City of Toronto open data. Nothing is sent to the City. "
           "For emergencies call 911.")

for role, text in st.session_state.chat:
    st.chat_message(role).write(text)

if not config.has_api_key():
    st.warning("ANTHROPIC_API_KEY is not set. Copy .env.example to .env, add your key, and restart.")
    st.stop()

user_text = st.chat_input("Describe the problem, e.g. 'There's a pothole outside 250 Dufferin St'")
if user_text:
    st.session_state.chat.append(("user", user_text))
    with st.spinner("Thinking..."):
        reply = agent.send(user_text)
    st.session_state.chat.append(("assistant", reply))
    st.rerun()
