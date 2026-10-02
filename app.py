import html
import re

import streamlit as st

from rag import answer_question

AREAS = [
    "Chitral, Khyber Pakhtunkhwa",
    "Upper Chitral",
    "Lower Chitral",
    "Khyber Pakhtunkhwa",
    "Pakistan",
]

TOPICS = {
    "flood": ("Flood safety", "🌊", "What should I do before, during, and after a flood in Chitral?"),
    "quake": ("Earthquake safety", "⌁", "What should I do during an earthquake in Chitral?"),
    "heat": ("Heatwave guidance", "☀", "What should I do during a heatwave in Chitral?"),
    "kit": ("Emergency kit", "▣", "What should I include in an emergency kit for my family in Chitral?"),
    "glof": ("GLOF awareness", "▲", "What are glacier-lake outburst floods (GLOFs) and how can communities in Chitral stay safe?"),
}

st.set_page_config(
    page_title="Climate Information Bot | Chitral",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&family=Noto+Nastaliq+Urdu:wght@400;500&display=swap');

        :root {
            --navy: #143947; --navy-deep: #0d2b36; --teal: #287b7b; --teal-light: #dfeeed;
            --teal-soft: #eef7f6; --ink: #18313b; --muted: #657b83; --page: #f5f8f7;
            --surface: #ffffff; --line: #d9e5e2; --amber: #c87a24; --amber-bg: #fff5e5; --danger: #a34636;
        }
        * { box-sizing: border-box; }
        .stApp { background: var(--page); color: var(--ink); font-family: "DM Sans", sans-serif; }
        #MainMenu, footer, header { visibility: hidden; }
        .block-container { max-width: 1220px; padding-top: 2rem; padding-bottom: 3.5rem; }

        /* Sidebar */
        [data-testid="stSidebar"] { background: var(--navy); border-right: 0; }
        [data-testid="stSidebar"] > div:first-child { background: var(--navy); }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span, [data-testid="stSidebar"] .stCaption,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { color: #f4f8f7 !important; }
        [data-testid="stSidebar"] hr { border-color: rgba(235, 247, 245, 0.16); margin: 1.25rem 0; }
        .sidebar-brand { padding: 0.25rem 0 0.75rem; }
        .sidebar-kicker { color: #9bd2cb !important; font-size: 0.69rem; font-weight: 700; letter-spacing: 0.13em; text-transform: uppercase; margin-bottom: 0.5rem; }
        .sidebar-title { color: #ffffff !important; font-family: "Playfair Display", serif; font-size: 1.45rem; line-height: 1.15; margin: 0; }
        .sidebar-copy { color: #c8dedb !important; font-size: 0.88rem; line-height: 1.55; margin-top: 0.6rem; }

        [data-testid="stSidebar"] div[data-baseweb="select"] > div { background-color: #235566 !important; border: 1px solid #4c7d88 !important; border-radius: 10px !important; min-height: 44px !important; }
        [data-testid="stSidebar"] div[data-baseweb="select"] * { color: #ffffff !important; opacity: 1 !important; }
        [data-testid="stSidebar"] div[data-baseweb="select"] svg { fill: #ffffff !important; }
        div[data-baseweb="popover"], div[data-baseweb="popover"] ul { background-color: #1b4b5b !important; }
        div[data-baseweb="popover"] li { background-color: #1b4b5b !important; color: #ffffff !important; }
        div[data-baseweb="popover"] li:hover { background-color: #2b7880 !important; }

        [data-testid="stSidebar"] .stButton > button { background: transparent; color: #eaf5f3; border: 1px solid rgba(234, 245, 243, 0.38); border-radius: 9px; min-height: 40px; font-weight: 600; }
        [data-testid="stSidebar"] .stButton > button:hover { background: rgba(255, 255, 255, 0.10); border-color: #9bd2cb; }

        .sidebar-emergency { background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 12px; padding: 0.9rem; }
        .sidebar-emergency-label { color: #f4c57c !important; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase; margin-bottom: 0.35rem; }
        .sidebar-emergency-number { color: #ffffff !important; font-size: 1.3rem; font-weight: 700; margin: 0; }
        .sidebar-emergency-copy { color: #c8dedb !important; font-size: 0.8rem; line-height: 1.45; margin: 0.35rem 0 0; }

        /* Hero */
        .hero { position: relative; overflow: hidden; background: radial-gradient(circle at 92% 12%, rgba(106, 191, 181, 0.25), transparent 29%), linear-gradient(125deg, #133946 0%, #1c5967 58%, #287b7b 100%); border-radius: 20px; padding: 2.7rem 3rem; color: #ffffff; box-shadow: 0 12px 30px rgba(16, 55, 67, 0.16); margin-bottom: 1.25rem; }
        .hero::before { content: ""; position: absolute; width: 440px; height: 440px; border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 50%; right: -165px; top: -260px; }
        .hero::after { content: ""; position: absolute; width: 245px; height: 245px; border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 50%; right: 85px; bottom: -180px; }
        .hero-content { position: relative; z-index: 1; max-width: 770px; }
        .hero-eyebrow { color: #a7ded6; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.13em; text-transform: uppercase; margin-bottom: 0.7rem; }
        .hero h1 { color: #ffffff; font-family: "Playfair Display", serif; font-size: clamp(2.25rem, 4vw, 3.35rem); letter-spacing: -0.035em; line-height: 1.05; margin: 0 0 0.8rem; }
        .hero p { color: #e0efed; font-size: 1.04rem; line-height: 1.65; max-width: 670px; margin: 0; }
        .hero-meta { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1.35rem; }
        .hero-tag { border: 1px solid rgba(255, 255, 255, 0.30); border-radius: 999px; color: #f6fffd; font-size: 0.82rem; padding: 0.35rem 0.7rem; }

        /* Emergency notice */
        .emergency-notice { display: flex; align-items: flex-start; gap: 0.85rem; background: var(--amber-bg); border: 1px solid #f0d5a5; border-left: 4px solid var(--amber); border-radius: 12px; color: #694719; padding: 0.95rem 1.1rem; margin: 0 0 1.7rem; }
        .notice-icon { font-size: 1.15rem; line-height: 1.35; }
        .notice-title { font-weight: 700; margin-bottom: 0.12rem; }
        .notice-copy { font-size: 0.92rem; line-height: 1.5; }

        /* Headings */
        .section-heading { color: var(--navy); font-family: "Playfair Display", serif; font-size: 1.65rem; margin: 0; }
        .section-copy { color: var(--muted); font-size: 0.95rem; line-height: 1.55; margin: 0.3rem 0 1rem; }

        /* Topic buttons */
        .stButton > button { width: 100%; min-height: 82px; background: var(--surface); color: var(--ink); border: 1px solid var(--line); border-radius: 14px; box-shadow: 0 3px 12px rgba(19, 57, 71, 0.04); font-size: 0.9rem; font-weight: 700; transition: all 0.18s ease; }
        .stButton > button:hover { background: var(--teal-soft); border-color: #76aaa5; color: var(--navy); transform: translateY(-2px); box-shadow: 0 7px 18px rgba(19, 57, 71, 0.10); }
        .stButton > button:focus-visible { outline: 3px solid rgba(40, 123, 123, 0.35); outline-offset: 2px; }
        .st-key-topic-flood button { border-top: 4px solid #4999b6; }
        .st-key-topic-quake button { border-top: 4px solid #9c7655; }
        .st-key-topic-heat button { border-top: 4px solid #db9a3f; }
        .st-key-topic-kit button { border-top: 4px solid #52966a; }
        .st-key-topic-glof button { border-top: 4px solid #6a86bf; }

        /* Info cards */
        .info-card { background: rgba(255, 255, 255, 0.92); border: 1px solid var(--line); border-radius: 15px; min-height: 128px; padding: 1.15rem; box-shadow: 0 3px 14px rgba(19, 57, 71, 0.035); }
        .info-card-icon { color: var(--teal); font-size: 1rem; font-weight: 700; margin-bottom: 0.55rem; }
        .info-card h3 { color: var(--navy); font-family: "Playfair Display", serif; font-size: 1.18rem; margin: 0 0 0.4rem; }
        .info-card p { color: var(--muted); font-size: 0.9rem; line-height: 1.5; margin: 0; }

        /* Chat */
        .chat-heading { display: flex; align-items: baseline; justify-content: space-between; gap: 1rem; border-top: 1px solid var(--line); margin-top: 2rem; padding-top: 1.8rem; }
        .chat-hint { color: var(--muted); font-size: 0.85rem; }
        [data-testid="stChatMessage"] { background: #ffffff; border: 1px solid var(--line); border-radius: 14px; padding: 0.75rem 0.95rem; box-shadow: 0 2px 9px rgba(19, 57, 71, 0.035); margin-bottom: 0.85rem; }
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { background: #eaf5f3; border-color: #c7e2dd; }
        [data-testid="stChatInput"] { background: #ffffff; border: 1px solid #bdd8d4; border-radius: 14px; box-shadow: 0 5px 16px rgba(19, 57, 71, 0.07); }
        [data-testid="stChatInput"]:focus-within { border-color: var(--teal); box-shadow: 0 0 0 3px rgba(40, 123, 123, 0.14); }

        /* Sources */
        .sources { color: var(--muted); font-size: 0.78rem; margin-top: 0.55rem; }
        .sources-label { color: #527079; font-weight: 700; margin-right: 0.25rem; }
        .source-chip { display: inline-block; background: #e6f2f0; border: 1px solid #d0e5e1; border-radius: 999px; color: #245b62; font-size: 0.77rem; margin: 0.25rem 0.3rem 0 0; padding: 0.16rem 0.58rem; }

        /* Urdu */
        .urdu, .urdu p, .urdu li { direction: rtl; text-align: right; font-family: "Noto Nastaliq Urdu", serif; font-size: 1.04rem; line-height: 2.25; }

        @media (max-width: 850px) {
            .block-container { padding: 1.2rem 1rem 2.5rem; }
            .hero { padding: 2rem 1.4rem; }
            .hero h1 { font-size: 2.3rem; }
            .chat-heading { display: block; }
            .chat-hint { display: block; margin-top: 0.35rem; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []


def is_urdu(text: str) -> bool:
    return bool(re.search(r"[\u0600-\u06FF]", text))


def show_text(text: str) -> None:
    """Show a reply in RTL styling if it contains Urdu characters."""
    if is_urdu(text):
        safe_text = html.escape(text).replace("\n", "<br>")
        st.markdown(f'<div class="urdu" dir="rtl">{safe_text}</div>', unsafe_allow_html=True)
    else:
        st.markdown(text)


def show_sources(sources: list[str]) -> None:
    """Show answer references as safe visual tags."""
    if not sources:
        return
    chips = "".join(f'<span class="source-chip">{html.escape(str(s))}</span>' for s in sources)
    st.markdown(
        f'<div class="sources"><span class="sources-label">Reference guides:</span>{chips}</div>',
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-kicker">Preparedness service</div>
            <div class="sidebar-title">Climate Information Bot</div>
            <div class="sidebar-copy">
                Practical disaster-preparedness support for Chitral and Khyber Pakhtunkhwa.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    location = st.selectbox("Select your area", AREAS, index=0)
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.markdown(
        """
        <div class="sidebar-emergency">
            <div class="sidebar-emergency-label">Immediate danger</div>
            <p class="sidebar-emergency-number">Rescue 1122</p>
            <p class="sidebar-emergency-copy">
                Follow official instructions from district administration, PDMA, NDMA, and PMD.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.caption(
        "This tool provides general preparedness guidance. It is not a live-alert "
        "or emergency-dispatch service."
    )

st.markdown(
    """
    <section class="hero">
        <div class="hero-content">
            <div class="hero-eyebrow">Chitral • climate preparedness</div>
            <h1>Plan ahead. Stay safer.</h1>
            <p>
                Clear, practical guidance for floods, earthquakes, heatwaves,
                emergency kits, and glacier-lake outburst flood risks.
            </p>
            <div class="hero-meta">
                <span class="hero-tag">English & Urdu</span>
                <span class="hero-tag">Local context</span>
                <span class="hero-tag">Preparedness guidance</span>
            </div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="emergency-notice">
        <div class="notice-icon">⚠</div>
        <div>
            <div class="notice-title">For immediate emergencies, call Rescue 1122.</div>
            <div class="notice-copy">
                This chatbot provides general preparedness information. During an active
                emergency, follow directions from local authorities and official warning services.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<h2 class="section-heading">What do you need help with?</h2>', unsafe_allow_html=True)
st.markdown(
    '<p class="section-copy">Choose a topic to start a question, or write your own below.</p>',
    unsafe_allow_html=True,
)

quick_prompt = None
topic_columns = st.columns(len(TOPICS))
for column, (topic_key, (title, icon, question)) in zip(topic_columns, TOPICS.items()):
    with column:
        if st.button(f"{icon}\n{title}", key=f"topic-{topic_key}", use_container_width=True):
            quick_prompt = question

st.markdown("<div style='height: 1.2rem'></div>", unsafe_allow_html=True)

card_one, card_two, card_three = st.columns(3)
with card_one:
    st.markdown(
        """
        <div class="info-card">
            <div class="info-card-icon">01</div>
            <h3>Before a hazard</h3>
            <p>Prepare supplies, contacts, evacuation plans, and reliable sources of official updates.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with card_two:
    st.markdown(
        """
        <div class="info-card">
            <div class="info-card-icon">02</div>
            <h3>During an event</h3>
            <p>Focus on immediate safety, protect vulnerable family members, and follow official instructions.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with card_three:
    st.markdown(
        """
        <div class="info-card">
            <div class="info-card-icon">03</div>
            <h3>Afterwards</h3>
            <p>Check injuries and hazards carefully, reconnect with support, and avoid unsafe return areas.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="chat-heading">
        <div>
            <h2 class="section-heading">Ask the preparedness assistant</h2>
            <p class="section-copy">Write in English or Urdu. Include your location when it is relevant.</p>
        </div>
        <span class="chat-hint">General guidance • Not live emergency instructions</span>
    </div>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🏔️"):
        st.write(
            "Hello. I can help you prepare for floods, earthquakes, heatwaves, "
            "emergency kits, and GLOFs in Chitral. You may write in English or Urdu."
        )

for message in st.session_state.messages:
    avatar = "🏔️" if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        show_text(message["content"])
        show_sources(message.get("sources", []))

prompt = st.chat_input("Ask about floods, earthquakes, heatwaves, GLOFs, or emergency kits...")
if quick_prompt:
    prompt = quick_prompt

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        show_text(prompt)

    with st.chat_message("assistant", avatar="🏔️"):
        with st.spinner("Checking preparedness guidance..."):
            try:
                data = answer_question(prompt, location)
                answer = data.get("answer", "I could not find an answer right now. Please try again.")
                sources = data.get("sources", [])

                show_text(answer)
                show_sources(sources)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer, "sources": sources}
                )
            except Exception as error:
                st.error(f"Something unexpected went wrong: {error}")