import streamlit as st
import re

st.set_page_config(
    page_title="LYLA | Company AI",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# LYLA Company AI
# No external AI API. Answers come from approved project facts and keyword matching.
# This is a rule-based prototype, not a generative AI model.

st.markdown("""
<style>
    .block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 1100px;}
    .hero {
        padding: 1.6rem 1.8rem; border-radius: 18px;
        background: linear-gradient(120deg, #13283f, #246b75);
        color: white; margin-bottom: 1.2rem;
    }
    .hero h1 {color: white; margin-bottom: .25rem;}
    .hero p {color: #e6f2f3; margin-bottom: 0;}
    .small-note {font-size: .88rem; color: #6b7280;}
    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,.25);
        border-radius: 12px; padding: 12px;
    }
</style>
""", unsafe_allow_html=True)

COMPANY_DATA = {
    "company": {
        "title": "What does LYLA do?",
        "keywords": ["what does your company do", "company do", "company about",
                     "介紹公司", "公司做什麼", "你們公司是做什麼"],
        "answer": (
            "LYLA is a proposed student business: a semiconductor and AI company in Taiwan. "
            "The proposal combines semiconductor-related services, an AI business branch, "
            "and a training and education branch."
        ),
    },
    "invest": {
        "title": "Why should I invest?",
        "keywords": ["why should i invest", "why invest", "投資你們", "為什麼要投資"],
        "answer": (
            "Our proposal connects semiconductor-related services, AI services, and training "
            "programs to create several possible revenue sources. This is a student business "
            "proposal, not a guarantee of profit. Investors would need validated customer "
            "demand, costs, technical performance, and a detailed financial plan."
        ),
    },
    "revenue": {
        "title": "How does LYLA make money?",
        "keywords": ["how do you make money", "make money", "revenue", "earn money",
                     "營收", "怎麼賺錢", "收入來源"],
        "answer": (
            "Possible revenue sources include AI subscriptions or licenses, per-use fees, "
            "custom AI development, consulting plus AI, and training-course fees. These are "
            "proposed business models and have not been market-verified."
        ),
    },
    "customers": {
        "title": "Who are your customers?",
        "keywords": ["who are your customers", "target customers", "customers", "客戶", "目標客戶"],
        "answer": (
            "Potential customers include semiconductor manufacturers and other companies that "
            "need inspection, production analysis, equipment support, or workforce training."
        ),
    },
    "ai_services": {
        "title": "What AI services do you provide?",
        "keywords": ["ai services", "ai product", "ai branch", "ai部門", "ai服務", "ai產品"],
        "answer": (
            "The proposed AI services include AI defect detection, production optimization, "
            "predictive equipment maintenance, semiconductor data analysis, AI customer support, "
            "and semiconductor training AI. These are proposed services; not all are confirmed "
            "as finished commercial products."
        ),
    },
    "defect": {
        "title": "What is AI defect detection?",
        "keywords": ["defect detection", "瑕疵檢測", "product inspection", "產品檢查"],
        "answer": (
            "AI defect detection would inspect product images and classify them as normal or "
            "possibly defective. A real image model needs labelled training images and testing. "
            "This Company AI page does not itself classify uploaded images."
        ),
    },
    "optimization": {
        "title": "What is production optimization?",
        "keywords": ["production optimization", "production efficiency", "生產最佳化", "生產效率"],
        "answer": (
            "Production optimization uses production information to identify possible "
            "inefficiencies and support better decisions. A real deployment would require "
            "relevant production data and validation by qualified staff."
        ),
    },
    "maintenance": {
        "title": "What is predictive maintenance?",
        "keywords": ["predictive maintenance", "equipment maintenance", "預測性維護", "設備維護"],
        "answer": (
            "Predictive maintenance aims to identify signs that equipment may need maintenance "
            "before a failure. A real system would need equipment or sensor history and validation."
        ),
    },
    "analysis": {
        "title": "What is semiconductor data analysis?",
        "keywords": ["semiconductor data analysis", "data analysis", "半導體資料分析", "資料分析"],
        "answer": (
            "Semiconductor data analysis can help organize and examine manufacturing or quality "
            "data. The exact analysis depends on the data available and the customer's needs."
        ),
    },
    "training": {
        "title": "What training courses are available?",
        "keywords": ["training", "courses", "education", "課程", "培訓", "訓練中心"],
        "answer": (
            "The proposed training center serves high-school students, university students, "
            "new semiconductor employees, and people preparing for semiconductor careers. "
            "Possible courses include semiconductor basics, process training, equipment training, "
            "cleanroom and safety, AI and programming, and hands-on practice. The proposal suggests "
            "course lengths from one week to three months."
        ),
    },
    "investment_amount": {
        "title": "How much initial investment is required?",
        "keywords": ["investment amount", "initial investment", "how much investment",
                     "投資金額", "初始投資"],
        "answer": (
            "The current project information does not provide a confirmed final investment amount. "
            "We will not invent a number. The team needs to calculate costs for facilities, "
            "equipment, staff, software, training resources, and operations."
        ),
    },
    "facilities": {
        "title": "What facilities does the company need?",
        "keywords": ["facilities", "buildings", "equipment", "設施", "建築", "設備需求"],
        "answer": (
            "The proposed training center includes classrooms, a computer/AI lab, equipment "
            "training and process training rooms, cleanroom and safety training areas, hands-on "
            "practice spaces, offices, meeting areas, and supporting facilities."
        ),
    },
    "risks": {
        "title": "What are the main risks?",
        "keywords": ["risk", "risks", "problems", "solutions", "風險", "問題", "解決方案"],
        "answer": (
            "The team's research identifies supply-chain and equipment constraints, competition "
            "for skilled workers, possible shortages of helium and hydrogen bromide, and overseas "
            "competitive pressure. Proposed responses include supplier diversification, safety "
            "stock, helium recovery where applicable, long-term contracts, training partnerships, "
            "and controlled overseas expansion."
        ),
    },
    "pricing": {
        "title": "What is your example AI subscription price?",
        "keywords": ["price", "pricing", "subscription fee", "how much does it cost", "價格", "收費"],
        "answer": (
            "Student business-model assumption (not market-verified): a starter AI dashboard "
            "subscription at NT$3,000 per month per customer. This is an example for the school "
            "project, not a researched market price."
        ),
    },
}

UNKNOWN = (
    "This information is not currently available in the company data. "
    "We will not invent company facts. Please ask about our proposed services, customers, "
    "training programs, risks, or business model."
)

def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", value.lower())).strip()

def get_answer(question: str):
    q = normalize(question)
    # Decline to invent exact financial or performance claims.
    unsupported = [
        r"\b(exact|confirmed|actual)\b.*\b(profit|revenue|customer count|market share)\b",
        r"\b(annual profit|customer count|market share)\b",
        r"\bguarantee\b.*\bnever\b.*\bmistake",
        r"\bcompetitor.*market share\b",
    ]
    if any(re.search(pattern, q) for pattern in unsupported):
        return UNKNOWN

    best_answer = None
    best_score = 0
    q_words = set(q.split())

    for item in COMPANY_DATA.values():
        for keyword in item["keywords"]:
            k = normalize(keyword)
            if k and k in q:
                score = len(k) + 10
                if score > best_score:
                    best_score = score
                    best_answer = item["answer"]
            else:
                k_words = set(k.split())
                overlap = len(k_words & q_words)
                if overlap >= 2 and overlap > best_score:
                    best_score = overlap
                    best_answer = item["answer"]

    return best_answer or UNKNOWN

SUGGESTED_QUESTIONS = [
    "What does your company do?",
    "Why should I invest?",
    "How do you make money?",
    "Who are your customers?",
    "What is AI defect detection?",
    "What are the company's main risks?",
]

TEST_QUESTIONS = [
    "What does your company do?",
    "Why should I invest?",
    "How do you make money?",
    "Who are your customers?",
    "What AI services do you provide?",
    "What is AI defect detection?",
    "How does production optimization help?",
    "What is predictive maintenance?",
    "What is semiconductor data analysis?",
    "What courses does your training center provide?",
    "Who can join the training courses?",
    "How long do the courses last?",
    "What facilities does the company need?",
    "How much initial investment is required?",
    "What are the company's main risks?",
    "How can you reduce supply-chain risks?",
    "How will you recruit and train workers?",
    "How can the company earn AI revenue?",
    "What is your example subscription price?",
    "Is the example price market-verified?",
    "What is the company's confirmed annual profit?",
    "What is the company's confirmed customer count?",
    "What is the competitor's exact market share?",
    "Can you guarantee that the AI will never make mistakes?",
    "What is the company's confirmed annual revenue?",
]

with st.sidebar:
    st.markdown("## 🏭 LYLA")
    st.caption("Semiconductor + AI Company")
    page = st.radio(
        "Navigation",
        ["Company AI", "AI Service Catalog", "Test Questions", "About This Prototype"],
    )
    st.divider()
    st.markdown("**Demo status**")
    st.success("No external API required")
    st.caption("Answers are selected from the project's prepared company information.")
    st.caption("Unknown facts are not invented.")

st.markdown("""
<div class="hero">
    <h1>LYLA Company AI</h1>
    <p>Ask our company AI about our proposed services, customers, training, risks, and business model.</p>
</div>
""", unsafe_allow_html=True)

if page == "Company AI":
    st.subheader("ASK OUR COMPANY AI")
    st.write("Choose a sample question or type your own.")
    cols = st.columns(3)
    for i, prompt in enumerate(SUGGESTED_QUESTIONS):
        with cols[i % 3]:
            if st.button(prompt, key=f"sample_{i}", use_container_width=True):
                st.session_state["lyla_question"] = prompt

    question = st.text_input(
        "Your question",
        key="lyla_question",
        placeholder="e.g. How does LYLA make money?",
        max_chars=300,
    )
    if st.button("Ask LYLA", type="primary", use_container_width=True):
        if question.strip():
            st.session_state["lyla_last_question"] = question.strip()
            st.session_state["lyla_last_answer"] = get_answer(question.strip())
        else:
            st.warning("Please enter a question.")

    if st.session_state.get("lyla_last_answer"):
        st.markdown("### Answer")
        st.info(st.session_state["lyla_last_answer"])
        st.caption("Source: LYLA team project information and clearly labelled student assumptions.")

elif page == "AI Service Catalog":
    st.subheader("Proposed AI Service Catalog")
    st.write("These are proposed services for the student business plan.")
    services = [
        ("AI Defect Detection", "Classifies product images as normal or possibly defective.",
         "Manufacturers with inspection needs.",
         "Could support faster and more consistent inspection after model validation.",
         "Possible per-machine license or monthly subscription."),
        ("Production Optimization", "Analyzes production information to identify inefficiencies.",
         "Manufacturers seeking better production decisions.",
         "Could reduce waste or delays if validated with real production data.",
         "Possible annual license or consulting + AI."),
        ("Predictive Maintenance", "Looks for patterns that may signal equipment maintenance needs.",
         "Factories and equipment operators.",
         "Could help plan maintenance and reduce unexpected downtime.",
         "Possible per-machine license or enterprise license."),
        ("Semiconductor Data Analysis", "Organizes and analyzes manufacturing or quality data.",
         "Semiconductor manufacturers and engineering teams.",
         "Could help teams identify trends and make evidence-based decisions.",
         "Possible subscription or custom AI development."),
    ]
    for name, does, customer, benefit, payment in services:
        with st.expander(name, expanded=True):
            st.markdown(f"**What it does:** {does}")
            st.markdown(f"**Who needs it:** {customer}")
            st.markdown(f"**Potential benefit:** {benefit}")
            st.markdown(f"**Possible payment:** {payment}")
    st.warning(
        "Student business-model assumption (not market-verified): "
        "NT$3,000/month per customer for a starter AI dashboard."
    )

elif page == "Test Questions":
    st.subheader("Company AI Test Questions")
    st.write("Use these 25 questions to check whether the assistant answers supported facts and avoids unsupported claims.")
    for index, question in enumerate(TEST_QUESTIONS, start=1):
        with st.expander(f"{index}. {question}"):
            st.write(get_answer(question))
    test_text = "\n\n".join(
        f"{i}. {q}\nAnswer: {get_answer(q)}"
        for i, q in enumerate(TEST_QUESTIONS, start=1)
    )
    st.download_button(
        "Download test results (.txt)",
        data=test_text,
        file_name="lyla_ai_test_questions.txt",
        mime="text/plain",
    )

elif page == "About This Prototype":
    st.subheader("How this prototype works")
    st.markdown("""
    1. A visitor types a question.
    2. Python compares the question with prepared keywords and patterns.
    3. The app selects a prepared answer from the company data.
    4. If it cannot find a reliable match, it says the information is not available.

    **Important limitation:** This is a rule-based information assistant, not a generative AI model.
    It does not train itself from visitors' questions and it does not classify product images.
    A separate defect-detection model would need labelled normal/defective images, training,
    and testing.
    """)
    st.markdown("### Company information currently included")
    for item in COMPANY_DATA.values():
        st.markdown(f"**{item['title']}**")
        st.write(item["answer"])
