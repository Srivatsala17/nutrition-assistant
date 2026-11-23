import sys
from pathlib import Path

# lets Streamlit find config.py, core/ and db/ in the project root
sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st

from core.agent import build_agent, chat
from db import crud

st.set_page_config(page_title="AI Nutrition Assistant", page_icon="🥗", layout="wide")
st.title("🥗 AI Nutrition Assistant")
st.caption("Not medical advice. Nutrition data comes from a Kaggle dataset.")

# ---------- Sidebar: choose or create a profile ----------
users = crud.list_users()
options = {f"{u['name']} (id {u['id']})": u["id"] for u in users}

st.sidebar.header("Profile")
user_id = None
if options:
    choice = st.sidebar.selectbox("Select profile", list(options.keys()))
    user_id = options[choice]

with st.sidebar.expander("Create new profile", expanded=not options):
    with st.form("new_profile"):
        name = st.text_input("Name")
        age = st.number_input("Age", 10, 100, 25)
        gender = st.selectbox("Gender", ["female", "male"])
        height = st.number_input("Height (cm)", 100.0, 250.0, 165.0)
        weight = st.number_input("Weight (kg)", 30.0, 250.0, 65.0)
        goal = st.selectbox("Goal", ["lose", "maintain", "gain"])
        diet = st.selectbox("Diet", ["veg", "non-veg"])
        allergies = st.text_input("Allergies (comma separated)")
        activity = st.selectbox("Activity", ["sedentary", "light", "moderate", "active"], index=2)
        if st.form_submit_button("Create profile") and name.strip():
            crud.create_user(name.strip(), age, gender, height, weight,
                             goal, diet, allergies, activity)
            st.rerun()

if user_id is None:
    st.info("Create a profile in the sidebar to start.")
    st.stop()

# ---------- Reset the agent when the profile changes ----------
if st.session_state.get("active_user") != user_id:
    st.session_state.active_user = user_id
    st.session_state.agent = build_agent(user_id)
    st.session_state.messages = []

user = crud.get_user(user_id)
st.sidebar.write(f"**Goal:** {user['goal']} | **Diet:** {user['diet']}")
st.sidebar.write(f"**Daily target:** {user['calorie_target']} kcal")

# ---------- Tabs ----------
tab_chat, tab_today, tab_progress = st.tabs(["💬 Chat", "📅 Today", "📈 Progress"])

with tab_chat:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("e.g. I had 2 rotis and dal for lunch"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    reply = chat(st.session_state.agent, user_id, prompt)
                except Exception as e:
                    reply = f"Sorry, something went wrong: {e}"
            st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

with tab_today:
    rem = crud.get_remaining_calories(user_id)
    c1, c2, c3 = st.columns(3)
    c1.metric("Target", f"{rem['target']} kcal")
    c2.metric("Eaten", f"{rem['eaten']} kcal")
    c3.metric("Remaining", f"{rem['remaining']} kcal")
    st.progress(min(max(rem["eaten"] / rem["target"], 0), 1.0))

    meals = crud.get_today_meals(user_id)
    if meals:
        st.dataframe(pd.DataFrame(meals), use_container_width=True)
    else:
        st.write("No meals logged today. Tell the chatbot what you ate.")
    st.caption("Switch to this tab again after chatting to see updated numbers.")

with tab_progress:
    weights = crud.get_weight_history(user_id, days=90)
    if weights:
        st.subheader("Weight (kg)")
        st.line_chart(pd.DataFrame(weights).set_index("date"))

    summary = crud.get_weekly_summary(user_id)
    if summary["daily_calories"]:
        st.subheader("Calories per day (last 7 days)")
        st.bar_chart(pd.Series(summary["daily_calories"]))
        st.write(f"Average: **{summary['average_calories']} kcal** "
                 f"(target {summary['target']} kcal)")
    else:
        st.write("No calorie data yet.")