import re
import streamlit as st
from difflib import SequenceMatcher

# Lyla Company AI
# No external AI API, no web search.
# Answers are retrieved only from the approved company knowledge written below.
# Add new facts only after your team has approved them.

st.set_page_config(
    page_title="Lyla | Company AI",
    page_icon="🧠",
    layout="centered",
)

st.title("🧠 Lyla — Company AI")
st.caption("Ask about our proposed semiconductor and AI company. Answers are based only on the current company data.")

UNKNOWN_ANSWER = (
    "This information is not currently available in our company data. "
    "Please ask the team for confirmed information."
)

# Each entry contains only information from the project documents supplied so far.
# The 'keywords' help match a visitor's question to the right section.
KNOWLEDGE = [
    {
        "title": "Company project overview",
        "keywords": [
            "company", "what do you do", "about us", "business", "overview",
            "what does your company do", "proposed company", "semiconductor company",
        ],
        "content": (
            "Our team is developing a proposed semiconductor/AI company in Taiwan. "
            "The project combines four parts: Amber is responsible for the overall business model "
            "and investment plan; Irene researches company problems, risks, and solutions; "
            "Lyla develops the AI business branch; and Belle develops the training and education branch. "
            "The company proposal connects services, customers, operations, costs, risks, AI services, "
            "training programs, and revenue."
        ),
    },
    {
        "title": "Lyla AI business branch",
        "keywords": [
            "lyla", "ai branch", "ai business", "ai department", "ai revenue",
            "how can ai make money", "ai product", "ai service",
        ],
        "content": (
            "Lyla is responsible for the AI business branch of the proposed semiconductor company. "
            "The project goal is to explore how AI can become a product or service that generates "
            "additional profit. Possible service areas listed in the project are AI chip inspection, "
            "AI defect detection, predictive equipment maintenance, semiconductor data analysis, "
            "production optimization, AI customer support, and semiconductor training AI. "
            "These are possible service ideas, not confirmation that every service has already been built."
        ),
    },
    {
        "title": "Possible AI services",
        "keywords": [
            "defect detection", "inspection", "predictive maintenance", "equipment maintenance",
            "production optimization", "data analysis", "semiconductor data", "customer support",
            "training ai", "ai services", "services list",
        ],
        "content": (
            "The project lists these possible AI services: AI chip inspection, AI defect detection, "
            "predictive equipment maintenance, semiconductor data analysis, production optimization, "
            "AI customer support, and semiconductor training AI. "
            "The current documents do not confirm a finished commercial AI product or provide measured "
            "performance results for these services."
        ),
    },
    {
        "title": "AI department resources",
        "keywords": [
            "ai resources", "what does ai need", "employees", "computers", "software",
            "data", "technology", "ai equipment",
        ],
        "content": (
            "The project says the AI department should identify its required employees/workers, "
            "computers, software, data, technology, and other necessary resources. "
            "The documents supplied so far do not specify a complete staffing plan, exact equipment list, "
            "or confirmed budget for the AI department."
        ),
    },
    {
        "title": "Training center customers",
        "keywords": [
            "training customers", "who can enroll", "students", "trainees", "target customers",
            "training center", "education branch",
        ],
        "content": (
            "The training center is intended for university students, high-school students, new "
            "semiconductor employees, and people who want to work in the semiconductor industry. "
            "The goals include learning semiconductor knowledge, getting hands-on experience, learning "
            "about equipment, processes and safety, and preparing for semiconductor careers."
        ),
    },
    {
        "title": "Training center courses",
        "keywords": [
            "courses", "classes", "training courses", "semiconductor basics", "process training",
            "equipment training", "cleanroom", "safety", "programming", "hands-on practice",
        ],
        "content": (
            "The training center lists six course areas: Semiconductor Basics, Semiconductor Process, "
            "Equipment Training, Cleanroom and Safety, AI and Programming, and Hands-on Practice. "
            "Students can choose classes by level: Basic includes Basics and Safety; Intermediate includes "
            "Process and Equipment; Advanced includes AI, Programming, and Practice."
        ),
    },
    {
        "title": "Training center operation and revenue",
        "keywords": [
            "training fees", "course fees", "how training makes money", "training revenue",
            "registration", "course duration", "class size", "dormitory", "how does training earn money",
        ],
        "content": (
            "According to the project plan, students register online, take a simple test, and join a class "
            "based on their level. Courses may last from one week to three months. Class sizes are planned "
            "at 15–20 students. The plan says students pay for courses and dormitory accommodation. "
            "Exact course prices and dormitory prices have not been provided."
        ),
    },
    {
        "title": "Training center capacity and space",
        "keywords": [
            "training center size", "facility", "building", "room", "space", "capacity",
            "how many students", "total area", "training rooms",
        ],
        "content": (
            "The project plan estimates an indoor area of 2,441 square meters, an outdoor area of "
            "490 square meters, and a total site area of about 2,931 square meters. It estimates about "
            "120 people at one time: about 100 students and about 20 teachers and staff. "
            "Regular classes are planned for 20 students and lab classes for 15 students."
        ),
    },
    {
        "title": "Semiconductor supply chain and equipment risk",
        "keywords": [
            "supply chain", "equipment shortage", "equipment demand", "production capacity",
            "supplier", "fab expansion", "bottleneck",
        ],
        "content": (
            "The risk research says Taiwan's semiconductor supply chain may struggle to keep pace with "
            "demand as AI infrastructure expands. The document reports that TSMC's equipment demand "
            "forecast for Q1 started at 1x, rose to 1.5x after one quarter, and was raised to 1.9x in July. "
            "Potential effects include slower output expansion, delayed fab expansion, higher costs, "
            "unfilled orders, and damage to customer trust. Suggested responses are earlier forecasts "
            "to suppliers, long-term purchase agreements, investment in key suppliers, backup suppliers, "
            "efficiency and yield improvements, and phased expansion across locations."
        ),
    },
    {
        "title": "Worker and talent risks",
        "keywords": [
            "workers", "talent", "engineers", "staff", "salary", "recruiting", "retention",
            "human resources", "labor shortage",
        ],
        "content": (
            "The risk research says fast growth in semiconductor and AI industries increases competition "
            "for electricity, land, basic resources, and skilled engineers. International salary competition "
            "can make recruitment and retention harder. Possible effects include higher salary costs, "
            "project delays when key staff leave, and weaker competitiveness. Suggested responses are "
            "partnering with universities such as National Taiwan University, National Tsing Hua University, "
            "and National Chiao Tung University to identify and train students early, and proactively "
            "recruiting overseas talent."
        ),
    },
    {
        "title": "Materials risks",
        "keywords": [
            "materials", "helium", "hydrogen bromide", "gas shortage", "middle east",
            "material supply", "shipping routes",
        ],
        "content": (
            "The risk research identifies helium and hydrogen bromide as materials at risk. It says helium "
            "is important in chip cooling and lithography, and hydrogen bromide is used for plasma etching "
            "in advanced processes. A prolonged shortage could slow or stop production and reduce revenue "
            "from AI chips. Suggested responses include safety stocks, helium recycling and recovery, "
            "capacity-allocation plans, suppliers in different regions, long-term supply contracts, and "
            "alternative shipping routes."
        ),
    },
    {
        "title": "International competition risk",
        "keywords": [
            "competition", "united states", "us", "japan", "europe", "production outflow",
            "overseas fabs", "market share", "taiwan semiconductor industry",
        ],
        "content": (
            "The risk research says Europe, the United States, and Japan are pushing for greater "
            "self-reliance in semiconductor supply chains. It describes a future risk that some production "
            "could move away from Taiwan. Possible effects include stronger overseas competition and "
            "the cost and complexity of building overseas fabs. Suggested responses are keeping the most "
            "advanced technology and the largest share of capacity in Taiwan, expanding overseas in a "
            "controlled way, strengthening Taiwan's domestic ecosystem, and building close relationships "
            "with key customers and governments."
        ),
    },
    {
        "title": "Company risk framework",
        "keywords": [
            "risk", "problems", "challenges", "backup plan", "solutions", "risk management",
            "what could go wrong",
        ],
        "content": (
            "The project asks the team to examine risks involving employees, equipment, manufacturing, "
            "quality control, electricity, water, materials, suppliers, production capacity, safety, "
            "environment, finance, customers, competition, supply chain, and technology changes. "
            "Each major risk should be explained using this structure: Problem → Why/Cause → Effect on the "
            "Company → Solution/Backup Plan."
        ),
    },
    {
        "title": "Why investors may consider the company",
        "keywords": [
            "why invest", "investor", "investment", "investment case", "why should i invest",
            "invest in your company", "future growth",
        ],
        "content": (
            "The project asks the team to explain why an investor should consider investing, how the company "
            "could operate successfully and generate profit, and how it could grow in the future. "
            "The AI branch is intended to create additional revenue, new products or services, and future "
            "growth opportunities. However, the current documents do not provide a confirmed investment "
            "amount, financial forecast, profit estimate, or verified return on investment, so those figures "
            "cannot be stated."
        ),
    },
    {
        "title": "Confirmed AI pricing and payment model",
        "keywords": [
            "price", "pricing", "subscription", "license", "licence", "per machine",
            "enterprise license", "how much does ai cost", "ai payment", "ai business model",
        ],
        "content": (
            "The documents supplied so far list possible AI services, but they do not confirm a selected "
            "AI payment model or a specific customer price. A subscription, license, per-use fee, consulting "
            "service, or custom development fee must not be presented as a confirmed company decision until "
            "the team approves it."
        ),
    },
]

# Simple English keyword matching. This does not call an external model.
STOP_WORDS = {
    "the", "a", "an", "is", "are", "do", "does", "did", "what", "why", "how",
    "who", "when", "where", "can", "could", "would", "should", "our", "your",
    "you", "we", "i", "me", "it", "for", "of", "to", "in", "on", "and", "or",
    "about", "tell", "please", "company", "information",
}

def tokenize(text):
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return {w for w in words if w not in STOP_WORDS and len(w) > 1}

def score_entry(question, entry):
    q_words = tokenize(question)
    if not q_words:
        return 0.0

    keyword_text = " ".join(entry["keywords"])
    content_text = entry["title"] + " " + keyword_text + " " + entry["content"]
    content_words = tokenize(content_text)

    overlap = len(q_words & content_words) / max(len(q_words), 1)
    keyword_words = tokenize(keyword_text)
    keyword_overlap = len(q_words & keyword_words) / max(len(q_words), 1)

    q_normalized = " ".join(sorted(q_words))
    title_similarity = SequenceMatcher(
        None, q_normalized, " ".join(sorted(tokenize(entry["title"])))
    ).ratio()

    return (0.55 * overlap) + (0.35 * keyword_overlap) + (0.10 * title_similarity)

def answer_question(question):
    question = question.strip()
    if not question:
        return UNKNOWN_ANSWER, []

    ranked = sorted(
        ((score_entry(question, entry), entry) for entry in KNOWLEDGE),
        key=lambda item: item[0],
        reverse=True,
    )

    best_score, best_entry = ranked[0]

    # Conservative threshold: prefer saying "not available" over guessing.
    if best_score < 0.16:
        return UNKNOWN_ANSWER, []

    # If the user asks about price/ROI and no figures are provided, use the specific gap response.
    q = question.lower()
    price_terms = ["price", "pricing", "cost", "how much", "subscription", "license", "licence", "fee"]
    if any(term in q for term in price_terms) and any(
        term in q for term in ["ai", "service", "product", "company", "subscription", "license", "licence"]
    ):
        price_entry = next((e for e in KNOWLEDGE if e["title"] == "Confirmed AI pricing and payment model"), None)
        if price_entry:
            return price_entry["content"], [price_entry["title"]]

    roi_terms = ["roi", "return on investment", "profit forecast", "expected profit", "investment return"]
    if any(term in q for term in roi_terms):
        investor_entry = next((e for e in KNOWLEDGE if e["title"] == "Why investors may consider the company"), None)
        if investor_entry:
            return investor_entry["content"], [investor_entry["title"]]

    # Include a second entry only when it is clearly relevant, and cap the answer to avoid unrelated facts.
    selected = [best_entry]
    if len(ranked) > 1:
        second_score, second_entry = ranked[1]
        if second_score >= max(0.20, best_score * 0.72):
            selected.append(second_entry)

    answer = "\n\n".join(entry["content"] for entry in selected)
    sources = [entry["title"] for entry in selected]
    return answer, sources

with st.sidebar:
    st.header("About this demo")
    st.write(
        "This prototype uses a local, approved knowledge base and keyword matching. "
        "It does not call an external AI API or search the internet."
    )
    st.write("If the current company data does not support an answer, it should say so.")
    st.divider()
    st.subheader("Example questions")
    examples = [
        "What does our company do?",
        "What AI services are possible?",
        "How does the training center make money?",
        "What risks could affect semiconductor production?",
        "What is the AI product price?",
        "Why should an investor consider our company?",
    ]
    for example in examples:
        if st.button(example, use_container_width=True):
            st.session_state["suggested_question"] = example

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I am Lyla, the Company AI demo. Ask me about the proposed company, "
                "AI service ideas, training programs, or risks. I only answer from the current company data."
            ),
            "sources": [],
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            st.caption("Company data used: " + " · ".join(message["sources"]))

suggested = st.session_state.pop("suggested_question", "")
prompt = st.chat_input("Ask Lyla a question...")
if suggested and not prompt:
    prompt = suggested

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt, "sources": []})
    with st.chat_message("user"):
        st.markdown(prompt)

    answer, sources = answer_question(prompt)
    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )
    with st.chat_message("assistant"):
        st.markdown(answer)
        if sources:
            st.caption("Company data used: " + " · ".join(sources))

with st.expander("Current knowledge base topics"):
    for entry in KNOWLEDGE:
        st.markdown(f"**{entry['title']}**")
        st.write(entry["content"])

st.divider()
st.caption(
    "Prototype limitation: this is a retrieval-based demo, not a generative language model. "
    "Its knowledge is limited to the information approved and added to this file."
)
