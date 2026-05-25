import os
import streamlit as st
from dotenv import load_dotenv
from llm import ask_llm
from knowledge_base import KNOWLEDGE

# Load .env for local dev; fall back to st.secrets on Streamlit Cloud
load_dotenv()
if not os.getenv("GROQ_API_KEY"):
    try:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
    except (KeyError, FileNotFoundError):
        pass

# --------------------------------------------------
# Page setup
# --------------------------------------------------
st.set_page_config(
    page_title="AI-Powered Multilingual Healthcare Chatbot PoC",
    page_icon="🩺",
    layout="centered"
)

# --------------------------------------------------
# Styling
# --------------------------------------------------
st.markdown(
    """
    <style>
    .title {
        font-size: 32px;
        font-weight: 800;
        color: #0f766e;
        margin-bottom: 5px;
    }
    .subtitle {
        font-size: 16px;
        color: #64748b;
        margin-bottom: 20px;
    }
    .notice {
        background-color: #fefce8;
        color: #713f12;
        border-left: 5px solid #ca8a04;
        padding: 14px;
        border-radius: 10px;
        margin-bottom: 15px;
        font-size: 15px;
    }
    .source-box {
        background-color: #eff6ff;
        color: #0f172a;
        border-left: 5px solid #2563eb;
        padding: 14px;
        border-radius: 10px;
        margin-top: 12px;
    }
    .next-box {
        background-color: #f0fdf4;
        color: #0f172a;
        border-left: 5px solid #16a34a;
        padding: 14px;
        border-radius: 10px;
        margin-top: 12px;
    }
    .danger-box {
        background-color: #fff1f2;
        color: #7f1d1d;
        border-left: 5px solid #dc2626;
        padding: 14px;
        border-radius: 10px;
        margin-top: 12px;
        font-weight: 600;
    }
    .framework-box {
        background-color: rgba(255, 255, 255, 0.06);
        color: #e2e8f0;
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 8px;
        font-size: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# Session state
# --------------------------------------------------
if "language" not in st.session_state:
    st.session_state.language = None

if "profile_done" not in st.session_state:
    st.session_state.profile_done = False

if "name" not in st.session_state:
    st.session_state.name = ""

if "age" not in st.session_state:
    st.session_state.age = None

if "sex" not in st.session_state:
    st.session_state.sex = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

if "pending_intent" not in st.session_state:
    st.session_state.pending_intent = None

if "followup_needed" not in st.session_state:
    st.session_state.followup_needed = False


# --------------------------------------------------
# Language helper
# --------------------------------------------------
def t(key):
    lang = st.session_state.language or "English"

    translations = {
        "English": {
            "welcome": "Hello 👋 I am your AI-powered multilingual healthcare assistant.",
            "choose_language": "Please choose your preferred language.",
            "profile_intro": "Before we continue, please provide a little context. This helps me give safer and more relevant guidance.",
            "name": "Name (optional)",
            "age": "Age",
            "sex": "Sex",
            "continue": "Continue",
            "ask": "How may I help you today?",
            "chat_placeholder": "Type your health question here...",
            "followup_intro": "To guide you better, please answer these quick follow-up questions.",
            "duration": "How long have you had this concern?",
            "severity": "How severe is it?",
            "extra": "Any other symptoms or details?",
            "submit_followup": "Submit follow-up details",
            "source": "Source",
            "next_step": "Recommended Next Step",
            "reset": "Start New Chat"
        },
        "Yoruba": {
            "welcome": "Kaabo 👋 Emi ni oluranlọwọ ilera AI multilingual.",
            "choose_language": "Jọwọ yan ede ti o fẹ.",
            "profile_intro": "Ṣaaju ki a tẹsiwaju, jọwọ fun mi ni alaye kekere nipa rẹ. Eyi yoo ran mi lọwọ lati fun ọ ni itọsọna to dara.",
            "name": "Orukọ (kii ṣe dandan)",
            "age": "Ọjọ-ori",
            "sex": "Ibalopo",
            "continue": "Tẹsiwaju",
            "ask": "Bawo ni mo ṣe le ran ọ lọwọ loni?",
            "chat_placeholder": "Kọ ibeere ilera rẹ nibi...",
            "followup_intro": "Lati ran ọ lọwọ daradara, jọwọ dahun awọn ibeere kukuru wọnyi.",
            "duration": "Igba melo ni iṣoro yii ti bẹrẹ?",
            "severity": "Bawo ni o ṣe le to?",
            "extra": "Ṣe awọn aami aisan miiran wa?",
            "submit_followup": "Fi alaye ranṣẹ",
            "source": "Orisun",
            "next_step": "Igbesẹ Tó Kàn",
            "reset": "Bẹrẹ ìjíròrò tuntun"
        },
        "Igbo": {
            "welcome": "Nnọọ 👋 Abụ m onye enyemaka ahụike AI multilingual.",
            "choose_language": "Biko họrọ asụsụ ịchọrọ.",
            "profile_intro": "Tupu anyị gaa n’ihu, biko nye obere ozi gbasara gị. Nke a ga-enyere m aka inye ndụmọdụ ka mma.",
            "name": "Aha (ọ bụghị iwu)",
            "age": "Afọ",
            "sex": "Mmekọahụ",
            "continue": "Gaa n’ihu",
            "ask": "Kedu ka m ga-esi nyere gị aka taa?",
            "chat_placeholder": "Dee ajụjụ ahụike gị ebe a...",
            "followup_intro": "Ka m nyere gị nke ọma, biko zaa ajụjụ ole na ole ndị a.",
            "duration": "Kemgbe ole mgbe ka nsogbu a malitere?",
            "severity": "Kedu ogo nsogbu ahụ?",
            "extra": "Enwere mgbaàmà ọzọ?",
            "submit_followup": "Zipu nkọwa ndị ọzọ",
            "source": "Isi mmalite",
            "next_step": "Nzọụkwụ ọzọ",
            "reset": "Malite mkparịta ụka ọhụrụ"
        },
        "Hausa": {
            "welcome": "Sannu 👋 Ni ne mataimakin lafiya na AI multilingual.",
            "choose_language": "Da fatan za a zaɓi harshen da kake so.",
            "profile_intro": "Kafin mu ci gaba, da fatan za a bayar da ɗan bayani game da kai. Wannan zai taimaka wajen bada shawara mai dacewa.",
            "name": "Suna (ba dole ba)",
            "age": "Shekaru",
            "sex": "Jinsi",
            "continue": "Ci gaba",
            "ask": "Ta yaya zan taimaka maka yau?",
            "chat_placeholder": "Rubuta tambayar lafiyarka a nan...",
            "followup_intro": "Don in taimaka maka sosai, amsa waɗannan tambayoyin.",
            "duration": "Tun yaushe wannan matsalar ta fara?",
            "severity": "Yaya tsanani yake?",
            "extra": "Akwai wasu alamomi?",
            "submit_followup": "Aika ƙarin bayani",
            "source": "Tushe",
            "next_step": "Mataki na gaba",
            "reset": "Fara sabon hira"
        },
        "Nigerian Pidgin": {
            "welcome": "Hello 👋 I be your AI multilingual health assistant.",
            "choose_language": "Abeg choose the language wey you wan use.",
            "profile_intro": "Before we continue, abeg give small information about yourself. E go help me give better guidance.",
            "name": "Name (optional)",
            "age": "Age",
            "sex": "Sex",
            "continue": "Continue",
            "ask": "How I fit help you today?",
            "chat_placeholder": "Type your health question here...",
            "followup_intro": "To guide you better, abeg answer these small questions.",
            "duration": "How long e don start?",
            "severity": "How serious e be?",
            "extra": "Any other symptom or detail?",
            "submit_followup": "Submit details",
            "source": "Source",
            "next_step": "Next Step",
            "reset": "Start New Chat"
        }
    }

    return translations[lang][key]


# --------------------------------------------------
# Intent detection
# --------------------------------------------------
def detect_intent(user_text):
    text = user_text.lower()

    emergency_words = [
        "chest pain", "difficulty breathing", "shortness of breath",
        "severe bleeding", "confusion", "fainting", "unconscious",
        "cannot breathe", "breathless", "blue lips", "convulsion",
        "seizure", "bleeding badly"
    ]

    malaria_words = [
        "malaria", "fever", "headache", "chills", "body pain",
        "high temperature", "sweating", "vomiting",
        "mo fe mo boya mo ni malaria", "mo ni malaria",
        "iba", "ori fifo", "ara mi gbona",
        "achoro m ima ma enwere m malaria", "ahu mgbu",
        "i get fever", "body dey pain me", "cold and fever"
    ]

    immunization_words = [
        "polio", "vaccine", "vaccination", "immunization",
        "immunisation", "ajesara", "child vaccine", "baby vaccine",
        "routine immunization", "routine immunisation"
    ]

    family_planning_words = [
        "family planning", "contraceptive", "contraception",
        "pills", "birth control", "implant", "iud", "condom",
        "prevent pregnancy", "emergency contraceptive", "oyun",
        "ifetosomobibi", "dina oyun"
    ]

    medication_words = [
        "antibiotics", "antibiotic", "typhoid", "medicine", "drug",
        "self medication", "self-medication", "can i take",
        "without test", "dosage"
    ]

    if any(word in text for word in emergency_words):
        return "Emergency"
    if any(word in text for word in malaria_words):
        return "Malaria"
    if any(word in text for word in immunization_words):
        return "Immunization"
    if any(word in text for word in family_planning_words):
        return "Family Planning"
    if any(word in text for word in medication_words):
        return "Medication Safety"

    return "General Health"


# --------------------------------------------------
# Source-backed response bank
# --------------------------------------------------
def get_final_response(intent, duration, severity, extra_details):
    lang = st.session_state.language
    age = st.session_state.age
    sex = st.session_state.sex

    emergency_response = {
        "English": "This may require urgent medical attention. Please go to the nearest hospital or emergency unit immediately.",
        "Yoruba": "Eyi le nilo itọju pajawiri. Jọwọ lọ si ile-iwosan to sunmọ ọ lẹsẹkẹsẹ.",
        "Igbo": "Nke a nwere ike ịchọ enyemaka ngwa ngwa. Biko gaa ụlọ ọgwụ kacha nso ozugbo.",
        "Hausa": "Wannan na iya bukatar kulawar gaggawa. Da fatan za a je asibiti mafi kusa nan da nan.",
        "Nigerian Pidgin": "This one fit be emergency. Abeg go nearest hospital now now."
    }

    responses = {
        "Malaria": {
            "English": "Based on the symptoms described, this may be related to malaria or another infection. A malaria test is recommended before taking antimalarial medicine. Avoid self-medication.",
            "Yoruba": "Da lori awọn aami ara ti o sọ, eyi le ni ibatan si malaria tabi arun miiran. O dara lati ṣe idanwo malaria ki o to lo oogun malaria. Maṣe lo oogun lai gba imọran oniṣẹ ilera.",
            "Igbo": "Dabere na mgbaàmà ị kọwara, nke a nwere ike ịdị ka malaria ma ọ bụ ọrịa ọzọ. Ọ ka mma ime ule malaria tupu iwere ọgwụ malaria. Ejila ọgwụ n’onwe gị.",
            "Hausa": "Bisa alamomin da ka bayyana, wannan na iya danganta da malaria ko wata cuta. Ana ba da shawarar yin gwajin malaria kafin shan magani. Kada a sha magani ba tare da shawarar likita ba.",
            "Nigerian Pidgin": "Based on wetin you talk, e fit be malaria or another infection. Abeg do malaria test before you take malaria medicine. No self-medicate.",
            "source": "Source: Nigeria Centre for Disease Control and Prevention (NCDC) and Federal Ministry of Health malaria-related guidance. Full RAG implementation would retrieve exact passages from official malaria guideline documents.",
            "next": "Next step: Do a malaria test and visit a health facility if symptoms are severe, persist, or last more than three days."
        },
        "Immunization": {
            "English": "Children should receive vaccines according to the national routine immunization schedule. For polio and other routine vaccines, visit a primary health centre to confirm the correct schedule for the child’s age.",
            "Yoruba": "Awọn ọmọ yẹ ki wọn gba ajesara gẹgẹ bi eto ajesara orilẹ-ede. Fun polio ati ajesara miiran, jọwọ lọ si ile-iwosan ilera akọkọ lati jẹrisi eto to tọ fun ọjọ-ori ọmọ naa.",
            "Igbo": "Ụmụaka kwesịrị ịnata ọgwụ mgbochi dịka usoro mba si dị. Maka polio na ọgwụ mgbochi ndị ọzọ, gaa na primary health centre iji chọpụta usoro kwesịrị ekwesị maka afọ nwa ahụ.",
            "Hausa": "Yara su karɓi rigakafi bisa jadawalin rigakafin ƙasa. Domin polio da sauran rigakafi, je cibiyar lafiya domin tabbatar da jadawalin da ya dace da shekarun yaron.",
            "Nigerian Pidgin": "Pikin suppose collect vaccine based on national routine immunization schedule. For polio and other vaccines, visit primary health centre to confirm the right schedule.",
            "source": "Source: National Primary Health Care Development Agency (NPHCDA) and Federal Ministry of Health routine immunization guidance. Full RAG implementation would retrieve exact passages from official immunization schedules.",
            "next": "Next step: Visit a primary health centre to confirm the correct immunization schedule."
        },
        "Family Planning": {
            "English": "Family planning methods include pills, implants, IUDs, condoms, and injectables. Side effects differ from person to person, so counselling from a trained healthcare provider is recommended before choosing or changing a method.",
            "Yoruba": "Awọn ọna ifetosomobibi ni pills, implant, IUD, condom ati injectable. Ipa ẹgbẹ le yato si eniyan kọọkan, nitorina o dara lati ba oniṣẹ ilera sọrọ ki o to yan tabi yi ọna kan pada.",
            "Igbo": "Ụzọ family planning gụnyere pills, implant, IUD, condom na injection. Mmetụta ya nwere ike ịdị iche n’ahụ mmadụ, ya mere gwa onye ọrụ ahụike okwu tupu ịhọrọ ma ọ bụ gbanwee ụzọ.",
            "Hausa": "Hanyoyin family planning sun haɗa da pills, implant, IUD, condom da allura. Tasirin gefe na iya bambanta daga mutum zuwa mutum, don haka ka tuntubi ma’aikacin lafiya kafin ka zabi ko canza hanya.",
            "Nigerian Pidgin": "Family planning methods include pills, implant, IUD, condom and injection. Side effects fit differ from person to person, so talk to health worker before you choose or change method.",
            "source": "Source: World Health Organization (WHO) and Federal Ministry of Health family planning guidance. Full RAG implementation would retrieve exact passages from approved family planning documents.",
            "next": "Next step: Speak with a trained healthcare provider for counselling before choosing a method."
        },
        "Medication Safety": {
            "English": "It is not advisable to take antibiotics without proper testing or medical advice. Wrong antibiotic use can be harmful and may contribute to antimicrobial resistance.",
            "Yoruba": "Ko dara lati lo antibiotics lai ṣe idanwo tabi lai gba imọran dokita. Lilo antibiotics lai tọ lewu, o si le fa iṣoro antimicrobial resistance.",
            "Igbo": "Ọ dịghị mma iji antibiotics n’enweghị ule ma ọ bụ ndụmọdụ dọkịta. Iji antibiotics n'ụzọ na-ezighi ezi nwere ike ibute nsogbu ma mee ka ọgwụ ghara ịrụ ọrụ nke ọma n’ọdịnihu.",
            "Hausa": "Bai dace a sha antibiotics ba tare da gwaji ko shawarar likita ba. Amfani da antibiotics ba daidai ba na iya kawo matsala kuma yana iya taimakawa wajen antimicrobial resistance.",
            "Nigerian Pidgin": "No take antibiotics without test or doctor advice. Wrong use of antibiotics fit cause problem and fit make medicine no work well later.",
            "source": "Source: World Health Organization (WHO) antimicrobial resistance and medication safety guidance. Full RAG implementation would retrieve exact passages from official medication safety resources.",
            "next": "Next step: Consult a healthcare professional before taking antibiotics or prescription medicines."
        },
        "General Health": {
            "English": "I could not clearly identify the health topic from the question. Please provide more details about the symptoms, duration, and severity.",
            "Yoruba": "Mi o le mọ koko ilera naa daradara. Jọwọ sọ aami ara rẹ, bi o ti pẹ to, ati bi o ṣe le to.",
            "Igbo": "Enweghị m ike ịmata okwu ahụike ahụ nke ọma. Biko kọwaa mgbaàmà gị, oge ọ malitere, na otú o siri dị njọ.",
            "Hausa": "Ban iya gane batun lafiyar sosai ba. Da fatan za a bayyana alamomi, tsawon lokaci, da tsanani.",
            "Nigerian Pidgin": "I no really understand the health issue well. Abeg explain your symptoms, how long e don start, and how serious e be.",
            "source": "Source: General health communication guidance. Full implementation would retrieve relevant information from verified medical documents.",
            "next": "Next step: Provide more details or speak with a healthcare professional."
        }
    }

    if intent == "Emergency":
        return {
            "response": emergency_response[lang],
            "source": KNOWLEDGE["Emergency"]["source_note"],
            "next": KNOWLEDGE["Emergency"]["next_step"],
        }

    response = responses[intent][lang]

    # Context-aware note
    context_notes = []

    if age is not None and age < 5:
        context_notes.append("Because the user is a young child, medical review is strongly advised if symptoms persist or worsen.")
    elif age is not None and age >= 60:
        context_notes.append("Because the user is an older adult, symptoms should be monitored carefully and medical review is advised if symptoms persist or worsen.")

    if sex == "Female" and intent in ["Malaria", "Medication Safety", "Family Planning"]:
        context_notes.append("For female users, pregnancy or reproductive health context may be relevant depending on the concern.")

    if duration:
        context_notes.append(f"Reported duration: {duration}.")

    if severity:
        context_notes.append(f"Reported severity: {severity}.")

    if extra_details:
        context_notes.append(f"Additional details provided: {extra_details}.")

    # Try LLM; fall back to hardcoded response if unavailable
    llm_response = ask_llm(
        intent=intent,
        language=lang,
        age=age,
        sex=sex,
        user_message=st.session_state.get("pending_question", ""),
        duration=duration,
        severity=severity,
        extra=extra_details,
    )

    if llm_response:
        return {
            "response": llm_response,
            "source": KNOWLEDGE[intent]["source_note"],
            "next": KNOWLEDGE[intent]["next_step"],
        }

    if context_notes:
        response += "\n\nContext-aware note: " + " ".join(context_notes)

    return {
        "response": response,
        "source": KNOWLEDGE[intent]["source_note"],
        "next": KNOWLEDGE[intent]["next_step"],
    }


# --------------------------------------------------
# Sidebar: Proposed framework mapping
# --------------------------------------------------
with st.sidebar:
    st.title("🧩 Framework Layers")

    st.markdown(
        """
        <div class="framework-box"><b>Layer 1:</b> User Access and Interface</div>
        <div class="framework-box"><b>Layer 2:</b> Language Management</div>
        <div class="framework-box"><b>Layer 3:</b> Multilingual Input Processing</div>
        <div class="framework-box"><b>Layer 4:</b> Context-Aware Intent Recognition and Triage</div>
        <div class="framework-box"><b>Layer 5:</b> Verified Medical Knowledge / RAG</div>
        <div class="framework-box"><b>Layer 6:</b> Response Generation and Safety</div>
        """,
        unsafe_allow_html=True
    )

    if st.button(t("reset")):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown('<div class="title">🩺 AI-Powered Multilingual Healthcare Chatbot</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Proof-of-Concept implementation for Nigerian multilingual healthcare communication</div>', unsafe_allow_html=True)

if st.session_state.language:
    st.markdown(
        f'<div style="display:inline-block;background:#0f766e;color:white;'
        f'padding:4px 14px;border-radius:20px;font-size:13px;margin-bottom:12px;">'
        f'🌐 {st.session_state.language}</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="notice">
    <b>Disclaimer:</b> This chatbot is for academic proof-of-concept demonstration only.
    It does not provide final medical diagnosis, prescribe medication, or replace healthcare professionals.
    </div>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# Step 1: Language selection
# --------------------------------------------------
if st.session_state.language is None:
    st.chat_message("assistant").write("Hello 👋 How may I help you today? First, please choose the language you want to use.")

    language_choice = st.selectbox(
        "Choose language",
        ["English", "Yoruba", "Igbo", "Hausa", "Nigerian Pidgin"]
    )

    if st.button("Continue"):
        st.session_state.language = language_choice
        st.rerun()

# --------------------------------------------------
# Step 2: Basic profile after language choice
# --------------------------------------------------
elif not st.session_state.profile_done:
    st.chat_message("assistant").write(t("welcome"))
    st.chat_message("assistant").write(t("profile_intro"))

    with st.form("profile_form"):
        name = st.text_input(t("name"))
        age = st.number_input(t("age"), min_value=1, max_value=120, value=25)
        sex = st.selectbox(t("sex"), ["Prefer not to say", "Female", "Male"])

        submitted = st.form_submit_button(t("continue"))

        if submitted:
            st.session_state.name = name
            st.session_state.age = age
            st.session_state.sex = sex
            st.session_state.profile_done = True

            display_name = name if name else "there"
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": f"{t('ask')} {display_name}."
                }
            )
            st.rerun()

# --------------------------------------------------
# Step 3: Chat and follow-up flow
# --------------------------------------------------
else:
    # Display previous messages
    for message in st.session_state.messages:
        st.chat_message(message["role"]).write(message["content"])

    # If follow-up is needed, show form
    if st.session_state.followup_needed:
        st.chat_message("assistant").write(t("followup_intro"))

        with st.form("followup_form"):
            duration = st.text_input(t("duration"), placeholder="Example: 2 days / since yesterday")
            severity = st.selectbox(t("severity"), ["Mild", "Moderate", "Severe", "Not sure"])
            extra = st.text_area(t("extra"), placeholder="Example: vomiting, weakness, sore throat, pregnancy possibility, etc.")

            submitted = st.form_submit_button(t("submit_followup"))

            if submitted:
                with st.spinner("Getting guidance..."):
                    final = get_final_response(
                        st.session_state.pending_intent,
                        duration,
                        severity,
                        extra
                    )

                source_text = final["source"].removeprefix("Source: ")
                next_text = final["next"].removeprefix("Next step: ")
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": (
                            f"{final['response']}\n\n"
                            f"**{t('source')}:** {source_text}\n\n"
                            f"**{t('next_step')}:** {next_text}"
                        ),
                    }
                )

                st.session_state.followup_needed = False
                st.session_state.pending_question = None
                st.session_state.pending_intent = None
                st.rerun()

    # Chat input
    else:
        user_question = st.chat_input(t("chat_placeholder"))

        if user_question:
            st.session_state.messages.append({"role": "user", "content": user_question})

            intent = detect_intent(user_question)

            # Emergency should respond immediately
            if intent == "Emergency":
                final = get_final_response(intent, "", "", "")
                source_text = final["source"].removeprefix("Source: ")
                next_text = final["next"].removeprefix("Next step: ")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": (
                        f"{final['response']}\n\n"
                        f"**{t('source')}:** {source_text}\n\n"
                        f"**{t('next_step')}:** {next_text}"
                    ),
                })
                st.rerun()

            # Non-emergency asks follow-up first
            st.session_state.pending_question = user_question
            st.session_state.pending_intent = intent
            st.session_state.followup_needed = True

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": f"I understand this as a {intent} related question. I need a few more details before giving guidance."
                }
            )
            st.rerun()