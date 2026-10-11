import os
import tempfile

import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_groq import ChatGroq

load_dotenv()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ResumeAI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------- STYLES ----------------
# Design idea: a resume is a sheet of paper that gets marked up.
# Pale sage desk, ink-green text, highlighter-yellow accent, red-pen for emphasis.
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap');

    :root {
        --desk: #ECEFE8;
        --desk-deep: #DFE5DB;
        --ink: #17252A;
        --muted: #5B6B68;
        --line: #C5CEC6;
        --sheet: #FFFEFA;
        --highlighter: #F7DC45;
        --pen: #D1432F;
        --display: 'Bricolage Grotesque', 'Segoe UI', sans-serif;
        --reading: 'Newsreader', Georgia, serif;
    }

    /* ---- base ---- */
    .stApp {
        background: var(--desk);
        color: var(--ink);
        font-family: var(--display);
    }
    header[data-testid="stHeader"] { background: transparent; }
    #MainMenu, footer { visibility: hidden; }

    .block-container {
        max-width: 1040px;
        padding-top: 3rem;
        padding-bottom: 4rem;
    }

    [data-testid="stSidebar"] {
        background: var(--desk-deep);
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] * { color: var(--ink); }

    h1, h2, h3, h4 {
        font-family: var(--display);
        color: var(--ink);
        letter-spacing: -0.02em;
    }

    /* ---- hero ---- */
    .hero {
        display: grid;
        grid-template-columns: 1.35fr 1fr;
        gap: 40px;
        align-items: center;
        margin-bottom: 44px;
    }
    .hero h1 {
        font-size: clamp(2.2rem, 5vw, 3.6rem);
        line-height: 1.04;
        font-weight: 800;
        margin: 0 0 18px 0;
        padding: 0;
    }
    .hero p {
        font-family: var(--reading);
        font-size: 1.25rem;
        line-height: 1.55;
        color: var(--muted);
        max-width: 34ch;
        margin: 0;
    }

    /* the marked-up sheet of paper */
    .paper {
        position: relative;
        background: var(--sheet);
        border-radius: 4px;
        padding: 30px 28px 34px;
        transform: rotate(2.2deg);
        box-shadow: 0 1px 0 var(--line), 0 18px 40px -18px rgba(23, 37, 42, .35);
    }
    .paper .bar {
        height: 9px;
        border-radius: 2px;
        background: var(--line);
        margin-bottom: 13px;
    }
    .paper .bar.title { height: 14px; width: 48%; background: var(--ink); margin-bottom: 20px; }
    .paper .bar.w90 { width: 90%; }
    .paper .bar.w75 { width: 75%; }
    .paper .bar.w60 { width: 60%; }
    .paper .bar.w40 { width: 40%; }
    .paper .bar.marked {
        background: var(--line);
        box-shadow: 0 0 0 5px var(--highlighter);
        position: relative;
        z-index: 0;
    }
    .paper .bar.marked::before {
        content: "";
        position: absolute;
        inset: -5px -6px;
        background: var(--highlighter);
        z-index: -1;
        border-radius: 2px;
    }
    .paper .note {
        position: absolute;
        right: -14px;
        bottom: 22px;
        background: var(--pen);
        color: #fff;
        font-family: var(--display);
        font-weight: 700;
        font-size: .85rem;
        padding: 6px 12px;
        border-radius: 4px;
        transform: rotate(-4deg);
    }

    /* ---- section headings ---- */
    .section-title {
        font-family: var(--display);
        font-size: 1.35rem;
        font-weight: 700;
        color: var(--ink);
        margin: 34px 0 6px 0;
    }
    .hint {
        font-family: var(--reading);
        font-size: 1.02rem;
        color: var(--muted);
        margin-bottom: 14px;
    }

    /* ---- uploader ---- */
    [data-testid="stFileUploader"] label { display: none; }
    [data-testid="stFileUploaderDropzone"] {
        background: var(--sheet);
        border: 2px dashed var(--ink);
        border-radius: 8px;
        padding: 26px;
    }
    [data-testid="stFileUploaderDropzone"] * { color: var(--ink); }
    [data-testid="stFileUploaderDropzone"] button {
        background: var(--ink);
        color: #fff;
        border: none;
        border-radius: 8px;
    }
    [data-testid="stFileUploaderDropzone"] button * { color: #fff; }

    .file-chip {
        display: flex;
        align-items: center;
        gap: 12px;
        background: var(--sheet);
        border: 1px solid var(--line);
        border-left: 6px solid var(--highlighter);
        border-radius: 4px;
        padding: 12px 16px;
        margin: 16px 0 6px 0;
        font-weight: 600;
        color: var(--ink);
    }
    .file-chip span {
        font-family: var(--reading);
        font-weight: 400;
        color: var(--muted);
    }

    /* ---- buttons ---- */
    .stButton > button,
    .stDownloadButton > button {
        font-family: var(--display);
        font-weight: 700;
        font-size: 1rem;
        min-height: 52px;
        border-radius: 8px;
        border: 2px solid var(--ink);
        background: transparent;
        color: var(--ink);
        transition: background .12s ease, color .12s ease;
    }
    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: var(--highlighter);
        color: var(--ink);
        border-color: var(--ink);
    }
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"] {
        background: var(--ink);
        color: #fff;
    }
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="stBaseButton-primary"]:hover {
        background: var(--highlighter);
        color: var(--ink);
    }
    .stButton > button:focus-visible,
    .stDownloadButton > button:focus-visible {
        outline: 3px solid var(--pen);
        outline-offset: 2px;
    }

    /* ---- question-count radio ---- */
    div[data-testid="stRadio"] label p {
        font-family: var(--display);
        font-weight: 600;
        color: var(--ink);
    }
    /* ---- result sheet ---- */
    .st-key-sheet,
    /* ---- result sheet ---- */
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .sheet-title) {
        background: var(--sheet);
        border-radius: 4px;
        padding: 36px 44px 40px;
        margin-top: 12px;
        box-shadow: 0 1px 0 var(--line), 0 22px 44px -24px rgba(23, 37, 42, .35);
    }
    .st-key-sheet p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .sheet-title) p,
    .st-key-sheet li,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .sheet-title) li {
        font-family: var(--reading);
        font-size: 1.14rem;
        line-height: 1.7;
        color: var(--ink);
        max-width: 72ch;
    }
    .st-key-sheet h1,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .sheet-title) h1,
    .st-key-sheet h2,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .sheet-title) h2,
    .st-key-sheet h3,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .sheet-title) h3,
    .st-key-sheet h4,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .sheet-title) h4 {
        font-family: var(--display);
        color: var(--ink);
    }
    .st-key-sheet h3,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .sheet-title) h3,
    .st-key-sheet h4,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .sheet-title) h4 {
        margin-top: 1.6rem;
        padding-bottom: 6px;
        border-bottom: 3px solid var(--highlighter);
        display: inline-block;
    }
    .sheet-title {
        font-family: var(--display);
        font-size: 1.7rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0 0 10px 0;
        color: var(--ink);
    }
    .stats { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 22px; }
    .stat {
        background: var(--desk);
        border-radius: 4px;
        padding: 5px 12px;
        font-size: .9rem;
        font-weight: 600;
        color: var(--ink);
    }

    hr { border-color: var(--line); }

    .footer-note {
        text-align: center;
        font-family: var(--reading);
        color: var(--muted);
        font-size: .95rem;
        margin-top: 8px;
    }

    @media (max-width: 760px) {
        .hero { grid-template-columns: 1fr; gap: 28px; }
        .paper { transform: rotate(1deg); margin-right: 14px; }
    .st-key-sheet,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .sheet-title) { padding: 24px 20px 28px; }
    }
</style>
""",
    unsafe_allow_html=True,
)


# ---------------- HELPER FUNCTION ----------------
def process_resume(pdf_bytes, action, question_count):
    """Extract resume text and generate the requested result."""

    file_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:
            temp_file.write(pdf_bytes)
            file_path = temp_file.name

        documents = PyPDFLoader(file_path).load()

        resume_text = "\n\n".join(
            doc.page_content for doc in documents
        ).strip()

        if not resume_text:
            raise ValueError(
                "No readable text found in this PDF. "
                "Scanned resumes may require OCR."
            )

        llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.2
        )

        if action == "summary":
            prompt = f"""
You are a professional resume analyst.

Analyze the resume and create a concise, professional report.

Use these sections:
1. Professional Summary
2. Technical Skills
3. Education
4. Experience
5. Key Projects
6. Achievements

Use only facts stated in the resume.
Do not invent missing information.
Use clear headings and bullet points.

RESUME:
{resume_text}
"""
        else:
            prompt = f"""
You are an experienced technical interviewer.

Generate exactly {question_count} interview questions
based on the candidate's resume.

Include questions about:
- Technical skills and fundamentals
- Projects and implementation decisions
- Challenges and trade-offs
- Design choices and possible improvements

Use the resume as the source of candidate facts.
Do not assume an implementation detail is true if it
is not supported by the resume.

Number the questions clearly. Keep them specific
to the candidate's actual experience.

RESUME:
{resume_text}
"""

        response = llm.invoke(prompt)

        return response.content, len(documents), len(resume_text.split())

    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## ResumeAI")
    st.markdown("**How it works**")
    st.markdown(
        "1. Upload a PDF resume\n"
        "2. Pick a summary or interview questions\n"
        "3. Read it, download it, or try again"
    )
    st.divider()
    st.caption(
        "Your resume text is sent to Groq to generate the result. "
        "The uploaded file is deleted from the server right after it is read."
    )
    st.caption("Scanned PDFs (images of text) are not supported yet.")


# ---------------- HERO ----------------
st.markdown(
    """
<div class="hero">
    <div>
        <h1>Know your resume the way an interviewer will.</h1>
        <p>
            Upload your PDF. Get a clean summary, or questions
            pulled straight from your own projects.
        </p>
    </div>
    <div class="paper" aria-hidden="true">
        <div class="bar title"></div>
        <div class="bar w90"></div>
        <div class="bar w75 marked"></div>
        <div class="bar w60"></div>
        <div class="bar w90"></div>
        <div class="bar w40 marked"></div>
        <div class="bar w75"></div>
        <div class="note">Explain this one</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# ---------------- UPLOAD ----------------
st.markdown('<div class="section-title">Add your resume</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hint">PDF only, with selectable text.</div>',
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Resume (PDF)",
    type=["pdf"],
    help="Upload a PDF containing selectable text.",
)

if uploaded_file:
    size_kb = len(uploaded_file.getvalue()) / 1024

    st.markdown(
        f"""
        <div class="file-chip">
            📎 {uploaded_file.name}
            <span>{size_kb:.1f} KB</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------------- ACTIONS ----------------
    st.markdown(
        '<div class="section-title">What do you need?</div>',
        unsafe_allow_html=True,
    )

    question_count = st.radio(
        "Number of interview questions",
        [5, 10, 15],
        index=0,
        horizontal=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        summarize_clicked = st.button(
            "Summarize my resume",
            type="primary",
            use_container_width=True,
        )

    with col2:
        questions_clicked = st.button(
            "Write interview questions",
            use_container_width=True,
        )

    if summarize_clicked or questions_clicked:

        action = "summary" if summarize_clicked else "questions"

        with st.spinner("Reading your resume..."):
            try:
                result, page_count, word_count = process_resume(
                    uploaded_file.getvalue(),
                    action,
                    question_count,
                )

                st.session_state["result"] = result
                st.session_state["result_type"] = action
                st.session_state["file_name"] = uploaded_file.name
                st.session_state["page_count"] = page_count
                st.session_state["word_count"] = word_count
                st.session_state["question_count"] = question_count

            except Exception as error:
                st.error(
                    f"Could not process this resume: {error}"
                )

    # ---------------- RESULTS ----------------
    if (
        "result" in st.session_state
        and st.session_state.get("file_name") == uploaded_file.name
    ):
        result_type = st.session_state["result_type"]

        title = (
            "Resume summary"
            if result_type == "summary"
            else "Interview questions"
        )

        pages = st.session_state["page_count"]
        words = st.session_state["word_count"]
        stats = [
            f"{pages} page{'s' if pages != 1 else ''} read",
            f"{words:,} words",
        ]
        if result_type == "questions":
            stats.append(f"{st.session_state['question_count']} questions")

        st.markdown(
            '<div class="section-title">Your result</div>',
            unsafe_allow_html=True,
        )

        try:
            sheet = st.container(key="sheet")  # Streamlit >= 1.39
        except TypeError:
            sheet = st.container()  # older versions: styled via :has()

        with sheet:
            st.markdown(
                f'<div class="sheet-title">{title}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="stats">'
                + "".join(f'<span class="stat">{s}</span>' for s in stats)
                + "</div>",
                unsafe_allow_html=True,
            )
            st.markdown(st.session_state["result"])

        st.write("")
        dl_col, clear_col = st.columns([3, 1])

        with dl_col:
            st.download_button(
                label="Download as text",
                data=st.session_state["result"],
                file_name=(
                    "resume_summary.txt"
                    if result_type == "summary"
                    else "interview_questions.txt"
                ),
                mime="text/plain",
                use_container_width=True,
            )

        with clear_col:
            if st.button("Clear", use_container_width=True):
                for key in [
                    "result",
                    "result_type",
                    "file_name",
                    "page_count",
                    "word_count",
                    "question_count",
                ]:
                    st.session_state.pop(key, None)
                st.rerun()

else:
    st.info("Add a PDF resume above to get started.")

st.divider()

st.markdown(
    '<p class="footer-note">ResumeAI, built with Python, LangChain and Streamlit.</p>',
    unsafe_allow_html=True,
)