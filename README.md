# ChatCompanion 🛡️

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CodeQL](https://github.com/andreaseirich/ChatCompanion/workflows/CodeQL%20Analysis/badge.svg)](https://github.com/andreaseirich/ChatCompanion/actions/workflows/codeql-analysis.yml)
[![Privacy](https://img.shields.io/badge/Privacy-First%20Offline-green.svg)](docs/ETHICS.md)

**Privacy-first, offline assistant that empowers children and teenagers (ages 10-16) to recognize risky chat patterns themselves**

---

## The Challenge: When Silence Becomes Dangerous

Online grooming crimes have increased **89%** over six years (Source: NSPCC, 2024). **55%** of teens ages 13-17 have experienced cyberbullying in their lifetime (Source: Cyberbullying Research Center, 2023). Most young people don't tell an adult when something feels wrong online—**over half stay silent** (Source: NCES, 2022).

Existing solutions often require cloud uploads (someone else sees the conversations) or are designed for surveillance rather than empowerment. Children need a tool that helps them recognize risky patterns while maintaining their privacy and autonomy.

### Real Scenarios: Why Pattern Recognition Matters

**Scenario A: The Manipulated Trust**

In gaming environments, high-risk grooming can occur in as little as **45 minutes** from first contact (Source: WeProtect Global Alliance, 2023). A 15-year-old who feels isolated at school is approached online by someone who seems understanding and supportive. Over several days, this "friend" builds trust through kind words and empathy. Then the requests begin: first for personal photos, then with increasing pressure and secrecy demands ("don't tell anyone", "delete our messages"). When the teen hesitates, guilt-shifting kicks in ("if you really trusted me...").

**What ChatCompanion flags early:**
- Rapid trust-building from a stranger
- Secrecy demands ("don't tell anyone")
- Isolation tactics ("adults won't understand us")
- Pressure escalation ("you have to", "right now")
- Guilt-shifting ("if you cared about me...")

**Key insight:** These manipulation patterns often follow a predictable playbook. Recognizing them early—before a harmful decision is made—gives young people the chance to pause and reach out to someone they trust.

---

**Scenario B: The Relentless Campaign**

**55%** of teens ages 13-17 have experienced cyberbullying, with **26.5%** experiencing it in the past 30 days alone (Source: Cyberbullying Research Center, 2023). A 12-year-old receives cruel messages across multiple apps over many months. The messages are one-sided, escalating, and persistent: insults, social exclusion threats, and worse. The victim feels trapped because the harassment follows them everywhere online.

**What ChatCompanion flags:**
- One-sided hostility without repair markers (no "jk", no mutual teasing)
- Escalating severity of insults
- Pattern of repeated attacks (not isolated incidents)
- No joking context or friendship indicators

**Key insight:** Bullying campaigns often hide in the spaces adults don't see. A tool that helps the young person *recognize* the pattern—and see that this is NOT normal friendship conflict—can encourage them to seek help and set boundaries.

---

**Scenario C: The Rapid Trap**

Sextortion can progress from first contact to threats in **as little as 5 minutes** (Source: FBI, 2024). **1 in 5 teens (20%)** have experienced sextortion (Source: Thorn, 2025). A 16-year-old playing online games is contacted by someone claiming to be their age. After friendly conversation, they move to private messaging. Within minutes, the conversation escalates: first casual chat, then requests for photos, then—after compliance—immediate threats and demands. The teen feels trapped, ashamed, and afraid to tell anyone.

**What ChatCompanion flags:**
- Rapid escalation from friendly to demanding
- Pressure with time urgency ("right now", "immediately")
- Proof-of-compliance requests ("send a screenshot", "delete and prove it")
- Secrecy demands combined with threats
- Coercive control patterns ("you have to", "don't you dare tell")

**Key insight:** These situations can escalate in minutes. Pattern recognition during the conversation—before a point of no return—gives young people a chance to recognize what's happening as a known tactic, not a personal failing.

---

## The Problem: Why Existing Tools Fall Short

### What Risky Patterns Look Like

All three scenarios share common manipulation tactics that ChatCompanion is designed to detect:

1. **Secrecy Demands** — "Don't tell anyone", "This is just between us"
2. **Isolation Tactics** — "Adults don't understand", "I'm the only one who gets you"
3. **Pressure & Urgency** — "Right now", "You have to", time ultimatums
4. **Guilt-Shifting** — "If you cared about me", "This is your fault"
5. **Coercive Control** — Demanding proof, threatening consequences, removing autonomy

These patterns are NOT always obvious in the moment, especially to young people who may be experiencing them for the first time.

### The Reporting Gap: Why Empowerment Matters

**Over half of young people who experience online harm don't tell an adult:**
- **55.8%** of bullied students did NOT tell a trusted adult (Source: NCES, 2022)
- **63%** of 12-14 year-olds did not tell a parent when bothered by harmful content (Source: CyberSafeKids, 2024)
- **20%** of minors who experienced online sexual interactions told no one (Source: Thorn, 2024)
- Likelihood of turning to a trusted adult **dropped 10 percentage points since 2022** (Source: Thorn, 2024)

This is exactly why ChatCompanion exists: to help young people recognize concerning patterns *themselves*—so they can make informed decisions about seeking help.

### Why Surveillance Isn't the Answer

Most existing solutions are designed for surveillance: parents monitoring children's conversations, cloud-based analysis that requires uploading private chats, or automated reporting systems. These approaches can:
- Erode trust between children and adults
- Create a false sense of security
- Miss the patterns that matter most
- Violate privacy and autonomy

ChatCompanion takes a different approach: **privacy-first empowerment**. It gives children the tools to recognize risky patterns themselves, without anyone watching over their shoulder.

---

## The Solution: Privacy-First Pattern Recognition

ChatCompanion is a **local, fully offline tool** that helps children and teenagers (ages 10-16) recognize risky chat patterns through:

### Traffic Light System

- 🟢 **GREEN**: Safe conversation — "No warning signs detected"
- 🟡 **YELLOW**: Some concerning patterns — "Something feels a bit off" (mentions specific patterns detected)
- 🔴 **RED**: High-risk situation — "This is serious" + **"Need Immediate Help?"** section appears (only for RED, appears once)

### Evidence-Based Explanations

- **Observed behaviors are listed only when supported by matched patterns** — no false accusations
- **Threat language appears only when threat patterns are actually detected** (strict threat-gating)
- Clear, child-friendly explanations of what was detected and why
- Supportive, non-shaming tone suitable for ages 10-16

### Privacy-First Architecture

- **Fully offline**: All processing happens on your device—nothing is uploaded
- **No cloud uploads**: Your conversations never leave your device
- **No telemetry**: No tracking or analytics
- **No persistence**: Chat text is not saved by default

### Child-Friendly Language

- Simple, calm explanations that don't shame or scare
- Age-appropriate vocabulary (10-16)
- Supportive guidance on talking to trusted adults
- Encourages healthy boundaries and seeking help

---

## What ChatCompanion Can Do

✅ **Detect risky patterns** in chat conversations:
- Bullying patterns (one-sided hostility, escalating insults)
- Manipulation tactics (pressure, guilt-shifting, isolation)
- Secrecy demands ("don't tell anyone")
- Grooming indicators (rapid trust-building, inappropriate requests)
- Coercive control (proof-of-compliance demands, threats)

✅ **Explain what was detected** in simple, child-friendly language

✅ **Provide evidence-based results** — only shows observed behaviors when patterns actually match

✅ **Work completely offline** after initial setup — no internet required during analysis

✅ **Handle youth slang and obfuscation** — normalizes common abbreviations and detects masked attempts to hide hostile language

✅ **Respect privacy** — no data uploads, no cloud processing, no telemetry

---

## What ChatCompanion Cannot Do

❌ **Promise perfect detection** — The system is not 100% accurate. Some risky conversations may not be detected, and some safe conversations may be flagged incorrectly.

❌ **Make medical, psychological, or legal claims** — ChatCompanion is a supportive tool, not a medical, psychological, or legal instrument.

❌ **Replace trusted adults or professional help** — This tool helps awareness and encourages seeking help. It is not a replacement for talking to trusted adults, counselors, or professional support services.

❌ **Guarantee safety** — ChatCompanion is a tool to help awareness, not a definitive safety guarantee.

❌ **Monitor conversations automatically** — The tool requires the user to paste and analyze conversations manually.

❌ **Store chat data without consent** — Chat text is not saved by default. Any future storage features will require explicit opt-in.

**Important:** ChatCompanion is a **supportive tool, not decisive**. It helps identify patterns but doesn't replace human judgment. Always trust your instincts and seek help when something feels wrong.

---

## How It Works

ChatCompanion uses a hybrid detection approach that combines rule-based pattern matching (60%) with ML semantic analysis (40%), with a rules-only fallback for fully offline operation.

### High-Level Pipeline

1. **Normalization**: Handles slang, abbreviations, and obfuscation (e.g., "u" → "you", "r n" → "right now")
2. **Pattern Matching**: Rule-based detection of risky patterns (secrecy, pressure, threats, etc.)
3. **ML Analysis**: Semantic analysis using local NLP models (optional, ~80MB download)
4. **Context Gating**: Reduces false positives by analyzing context (e.g., "right now" in self-reports vs. demands)
5. **Threat-Gating**: Threat language appears only when threat patterns are actually detected
6. **Explanation Generation**: Creates child-friendly explanations with evidence from matched patterns
7. **UI Display**: Shows traffic light indicator, explanation, and help resources

For detailed technical documentation, see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## Quickstart

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Installation & Run

```bash
# Clone the repository
git clone https://github.com/andreaseirich/ChatCompanion.git
cd ChatCompanion

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app/main.py
```

The application will open in your default web browser at `http://localhost:8501`.

### Optional: Download ML Models

For enhanced detection (optional, ~80MB download):

```bash
python scripts/download_models.py
```

> **Note**: ML models are optional. The system works in rules-only mode if models are not downloaded.

### Optional: Developer Mode

For debug information:

```bash
CHATCOMPANION_DEV_MODE=1 streamlit run app/main.py
```

### Run Tests

```bash
pytest -q
```

For detailed installation instructions, see [`docs/INSTALL.md`](docs/INSTALL.md).

---

## Demo & Submission Assets

- **[Demo Script](docs/DEMO_SCRIPT.md)**: 3-minute demo video script showing ChatCompanion in action
- **[Devpost Submission](docs/DEVPOST_SUBMISSION.md)**: Content for CodeSpring Devpost submission
- **[Architecture](docs/ARCHITECTURE.md)**: Detailed technical architecture and design
- **[Ethics](docs/ETHICS.md)**: Ethics statement and privacy principles
- **[Installation Guide](docs/INSTALL.md)**: Detailed installation instructions
- **[Security Policy](SECURITY.md)**: Security reporting and best practices

---

## Limitations

### Detection Accuracy

- The system is not 100% accurate
- Some risky conversations may not be detected
- Some safe conversations may be flagged incorrectly
- Slang and irony may be ambiguous and could lead to false positives or negatives
- The system is a **tool to help awareness**, not a definitive safety guarantee

### Scope

- Designed for text-based chat conversations
- Not designed for live monitoring or OS-level integration
- Not a replacement for parental supervision or professional help
- Not a therapy or legal tool
- Currently designed for English as the primary language

### What This Means

ChatCompanion is a **supportive tool, not decisive**. It helps identify patterns but doesn't replace human judgment, trusted adult guidance, or professional support. Always trust your instincts and seek help when something feels wrong.

For detailed limitations and ethical considerations, see [`docs/ETHICS.md`](docs/ETHICS.md).

---

## Sources & References

All statistics cited in this README are from authoritative sources. Full citations and URLs are provided below for verification.

### Online Grooming

- **89% increase in online grooming crimes over six years (UK)**: NSPCC (National Society for the Prevention of Cruelty to Children), November 2024. [https://www.nspcc.org.uk/about-us/news-opinion/2024/online-grooming-crimes-increase/](https://www.nspcc.org.uk/about-us/news-opinion/2024/online-grooming-crimes-increase/)
- **7,062 grooming offences recorded in 2023/24 (UK)**: NSPCC, 2024. [https://www.nspcc.org.uk/about-us/news-opinion/2024/online-grooming-crimes-increase/](https://www.nspcc.org.uk/about-us/news-opinion/2024/online-grooming-crimes-increase/)
- **45 minutes average time to high-risk grooming in gaming environments**: WeProtect Global Alliance, Global Threat Assessment, 2023. [https://www.weprotect.org/global-threat-assessment-23/](https://www.weprotect.org/global-threat-assessment-23/)
- **546,000+ online enticement reports in 2024 (194% increase from 2023)**: NCMEC CyberTipline, 2024. [https://www.missingkids.org/gethelpnow/cybertipline/cybertiplinedata](https://www.missingkids.org/gethelpnow/cybertipline/cybertiplinedata)
- **89% of groomers introduced sexual content in the first conversation**: Winters, Kaylor & Jeglic (academic research), 2017. Referenced in WeProtect Global Threat Assessment.

### Sextortion

- **1 in 5 teens (20%) reported experiencing sextortion**: Thorn, "Sexual Extortion & Young People", June 2025. [https://www.thorn.org/blog/the-state-of-sextortion-in-2025/](https://www.thorn.org/blog/the-state-of-sextortion-in-2025/)
- **Sextortion can progress from first contact to threats in as little as 5 minutes**: FBI, 2024. [https://www.fbi.gov/how-we-can-help-you/scams-and-safety/common-frauds-and-scams/sextortion](https://www.fbi.gov/how-we-can-help-you/scams-and-safety/common-frauds-and-scams/sextortion)
- **30% of victims experienced demands within 24 hours of first contact**: Thorn, 2025. [https://www.thorn.org/blog/the-state-of-sextortion-in-2025/](https://www.thorn.org/blog/the-state-of-sextortion-in-2025/)
- **~100 financial sextortion reports per day to NCMEC**: NCMEC CyberTipline, 2024. [https://www.missingkids.org/blog/2024/ncmec-releases-new-sextortion-data](https://www.missingkids.org/blog/2024/ncmec-releases-new-sextortion-data)
- **149% increase in sextortion reports (2022 to 2023)**: NCMEC, 2024. [https://www.missingkids.org/blog/2024/ncmec-releases-new-sextortion-data](https://www.missingkids.org/blog/2024/ncmec-releases-new-sextortion-data)
- **90% of financial sextortion victims are males aged 14-17**: NCMEC, 2024. [https://www.missingkids.org/blog/2024/ncmec-releases-new-sextortion-data](https://www.missingkids.org/blog/2024/ncmec-releases-new-sextortion-data)
- **36+ suicides linked to sextortion since 2021**: FBI/HSI, 2023. [https://www.fbi.gov/contact-us/field-offices/nashville/news/sextortion-a-growing-threat-targeting-minors](https://www.fbi.gov/contact-us/field-offices/nashville/news/sextortion-a-growing-threat-targeting-minors)

### Cyberbullying

- **55% of teens (13-17) have experienced cyberbullying in their lifetime**: Cyberbullying Research Center (Dr. Hinduja & Dr. Patchin), 2023. [https://cyberbullying.org/2023-cyberbullying-data](https://cyberbullying.org/2023-cyberbullying-data)
- **26.5% experienced cyberbullying in the past 30 days (up from 17.2% in 2019)**: Cyberbullying Research Center, 2023. [https://cyberbullying.org/2023-cyberbullying-data](https://cyberbullying.org/2023-cyberbullying-data)
- **46% of teens experienced at least one cyberbullying behavior**: Pew Research Center, 2022. [https://www.pewresearch.org/](https://www.pewresearch.org/)
- **~2 million German students have been cyberbullying victims**: Cyberlife V Study (Germany), 2024. Referenced in JIM-Studie reporting.

### Reporting Gaps

- **55.8% of bullied students did NOT tell a trusted adult**: National Center for Education Statistics (NCES), 2022. [https://nces.ed.gov/](https://nces.ed.gov/)
- **63% of 12-14 year-olds did not tell a parent when bothered by harmful content**: CyberSafeKids Ireland, 2023-24. [https://www.cybersafekids.ie/](https://www.cybersafekids.ie/)
- **20% of minors who experienced online sexual interactions told no one**: Thorn, Youth Perspectives Report, 2024. [https://www.thorn.org/blog/2024-youth-perspectives/](https://www.thorn.org/blog/2024-youth-perspectives/)
- **Likelihood of turning to a trusted adult dropped 10 percentage points since 2022**: Thorn, 2024. [https://www.thorn.org/blog/2024-youth-perspectives/](https://www.thorn.org/blog/2024-youth-perspectives/)
- **74% of boys didn't fully understand what sextortion was**: UK National Crime Agency CEOP Command, 2024. [https://www.nationalcrimeagency.gov.uk/](https://www.nationalcrimeagency.gov.uk/)
- **65% of children aged 8-12 were contacted by a stranger during online gaming**: CyberSafeKids Ireland, 2023-24. [https://www.cybersafekids.ie/](https://www.cybersafekids.ie/)

---

## Safety Note

ChatCompanion is designed to help young people recognize risky patterns and encourage seeking help. If you see a **RED** indicator, the "Need Immediate Help?" section will appear with resources for immediate support.

**Important:** ChatCompanion is a supportive tool, not a replacement for trusted adults or professional help. Always trust your instincts and seek help when something feels wrong. Talk to a trusted adult, counselor, or professional support service if you need help.

For immediate help resources, see the "Need Immediate Help?" section that appears for RED risk levels, or contact:
- A trusted adult (parent, teacher, counselor)
- A professional support service (see resources in-app for RED)
- Emergency services if you are in immediate danger

---

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

---

**Remember**: ChatCompanion is a tool to help awareness and encourage seeking help. It is not a replacement for talking to trusted adults or professional support. Always trust your instincts and seek help when something feels wrong.
