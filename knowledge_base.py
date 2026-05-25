"""
Verified knowledge base for the Nigerian Healthcare Chatbot PoC.

Each entry contains a factual summary drawn from official Nigerian and
international public health sources. The summary is injected directly into
the LLM system prompt so the model answers from verified content only.

Day 2 note: In a full RAG implementation these summaries would be retrieved
dynamically from indexed source documents. For this PoC they are curated
static summaries.
"""

KNOWLEDGE = {
    "Malaria": {
        "summary": (
            "Malaria is a life-threatening disease transmitted through the bites of infected female Anopheles mosquitoes. "
            "Nigeria carries one of the highest malaria burdens globally. Common symptoms include fever, headache, chills, "
            "sweating, body pain, and vomiting. The Nigeria Centre for Disease Control and Prevention (NCDC) and the Federal "
            "Ministry of Health mandate that a malaria rapid diagnostic test (RDT) or microscopy must confirm infection "
            "before any antimalarial treatment is given. Artemisinin-based combination therapies (ACTs), such as "
            "Artemether-Lumefantrine, are the recommended first-line treatment in Nigeria and must only be taken after a "
            "confirmed positive test. Self-medication with antimalarials before testing is strongly discouraged because "
            "symptoms overlap with many other common infections. Severe malaria — marked by very high fever, convulsions, "
            "difficulty breathing, or altered consciousness — requires immediate hospital admission."
        ),
        "source_name": "Nigeria Centre for Disease Control and Prevention (NCDC) and Federal Ministry of Health",
        "source_note": "Nigeria Centre for Disease Control and Prevention (NCDC) — Malaria Treatment Guidelines; Federal Ministry of Health Nigeria",
        "next_step": "Do a malaria rapid diagnostic test (RDT) at the nearest health facility. If symptoms are severe, include convulsions or breathing difficulty, or last more than three days, seek immediate hospital care.",
    },

    "Immunization": {
        "summary": (
            "Nigeria's National Primary Health Care Development Agency (NPHCDA) maintains a routine immunization schedule "
            "for all children. Key vaccines and timings: BCG and Oral Polio Vaccine (OPV0) are given at birth; Pentavalent "
            "(DPT-HepB-Hib), OPV, and Pneumococcal Conjugate Vaccine (PCV) at 6, 10, and 14 weeks; Inactivated Polio "
            "Vaccine (IPV) at 14 weeks; Measles-Rubella (MR), Yellow Fever, and Meningococcal A vaccines at 9 months; "
            "and a second MR dose at 15 months. All vaccines are provided free of charge at government primary health "
            "centres. Missing a vaccine dose does not require restarting the entire schedule — a healthcare provider can "
            "advise on catch-up vaccinations. Timely immunization protects children from polio, measles, meningitis, "
            "hepatitis B, and other preventable diseases."
        ),
        "source_name": "National Primary Health Care Development Agency (NPHCDA)",
        "source_note": "National Primary Health Care Development Agency (NPHCDA) — Nigeria Routine Immunization Schedule",
        "next_step": "Visit the nearest government primary health centre with the child's immunization card to receive any due or missed vaccines free of charge.",
    },

    "Family Planning": {
        "summary": (
            "Family planning allows individuals and couples to choose the number, timing, and spacing of pregnancies. "
            "The WHO and Federal Ministry of Health Nigeria recognise the following contraceptive methods: combined oral "
            "contraceptive pills (taken daily), progestogen-only pills, injectable contraceptives such as DMPA (given "
            "every three months), hormonal implants (effective for 3–5 years), intrauterine devices (copper IUD effective "
            "up to 10 years; hormonal IUD up to 5 years), male and female condoms, and emergency contraception (effective "
            "within 72 hours of unprotected intercourse). All methods carry potential side effects that vary by individual "
            "and medical history. Hormonal methods are not recommended in certain conditions such as suspected pregnancy, "
            "unexplained vaginal bleeding, or active liver disease. WHO Medical Eligibility Criteria guide safe method "
            "selection. Counselling from a trained provider before starting or changing a method is strongly advised."
        ),
        "source_name": "World Health Organization (WHO) and Federal Ministry of Health Nigeria",
        "source_note": "WHO Medical Eligibility Criteria for Contraceptive Use (5th Ed.); Federal Ministry of Health Nigeria — Family Planning Guidelines",
        "next_step": "Visit a family planning clinic or primary health centre for personalised counselling before starting or changing any contraceptive method.",
    },

    "Medication Safety": {
        "summary": (
            "The World Health Organization (WHO) identifies antimicrobial resistance (AMR) as one of the greatest global "
            "health threats. Antibiotics must only be taken when prescribed by a qualified healthcare professional after "
            "proper clinical assessment or laboratory testing. Self-medicating with antibiotics for fever, typhoid, or "
            "other infections without a confirmed diagnosis is harmful: it may not treat the actual illness and accelerates "
            "antibiotic resistance, making future bacterial infections much harder to treat. Typhoid fever specifically "
            "should be confirmed by a Widal test or blood culture before antibiotics are started. Once prescribed, the "
            "full course of antibiotics must always be completed even if symptoms improve early, to prevent relapse and "
            "resistance. Any known drug allergies or other medications currently being taken must be disclosed to the "
            "prescribing healthcare provider to avoid dangerous interactions."
        ),
        "source_name": "World Health Organization (WHO)",
        "source_note": "WHO Global Action Plan on Antimicrobial Resistance; WHO Medication Safety in High-Risk Situations",
        "next_step": "Visit a healthcare professional for proper testing and a valid prescription before taking any antibiotic or prescription medicine.",
    },

    "General Health": {
        "summary": (
            "When a specific health concern cannot be clearly identified from the information provided, additional detail "
            "is needed before guidance can be given. Helpful information includes: the exact symptoms experienced, how "
            "long they have been present, their severity, and any associated symptoms. For any concern that is persistent, "
            "worsening, or causing significant discomfort, a visit to the nearest primary health centre or clinic is the "
            "safest course of action. Healthcare professionals can carry out a proper assessment, request relevant tests, "
            "and provide appropriate treatment or referral. Self-diagnosis and self-medication should be avoided, "
            "particularly for symptoms that could indicate infections, chronic conditions, or complications that require "
            "laboratory confirmation before treatment."
        ),
        "source_name": "Federal Ministry of Health Nigeria",
        "source_note": "Federal Ministry of Health Nigeria — Primary Healthcare Guidelines",
        "next_step": "Provide more details about your symptoms, or visit the nearest primary health centre for a proper assessment.",
    },

    "Emergency": {
        "summary": (
            "Symptoms such as chest pain, difficulty breathing, severe or uncontrolled bleeding, loss of consciousness, "
            "convulsions, seizures, or blue lips are signs of a potential medical emergency. These symptoms require "
            "immediate hospital attention and must not be managed at home. Time is critical — delays in reaching emergency "
            "care significantly worsen outcomes."
        ),
        "source_name": "Standard Emergency Triage Guidance",
        "source_note": "Standard Emergency Triage Protocols",
        "next_step": "Go to the nearest hospital emergency unit immediately or call emergency services. Do not delay.",
    },
}
