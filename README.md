
# ⬡ Local ATS Resume Optimizer

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-FF4B4B)
![Chainlit](https://img.shields.io/badge/Chainlit-UI-2ECC71)
![Local AI](https://img.shields.io/badge/Local_LLM-Qwen-orange)

An end-to-end multi-agent AI web application that automates the resume rewriting pipeline, running **strictly on your local machine** for total privacy. 

"The ATS is a black box" is no longer an excuse. This tool uses a localized crew of AI agents to parse your existing resume, score its structure, rewrite bullet points with strong action verbs and metrics, and output a freshly formatted PDF—all without sending a single byte of your personal data to external APIs.

## ✨ Features

* **🔒 100% Local Processing:** Powered by local Qwen models running via port 8000. Zero data leakage.
* **📄 Smart PDF Extraction:** Handles raw text extraction directly from uploaded resumes, catching structural quirks before handing the data off to the agents.
* **🤖 Multi-Agent Orchestration:** A specialized 4-agent CrewAI pipeline:
    * **Parser Agent:** Extracts and structures the raw data.
    * **ATS Analyzer:** Scores your structure and identifies missing keywords.
    * **Resume Writer:** Rewrites bullets focusing on impact, metrics, and action verbs.
    * **PDF Validator:** Ensures the final JSON payload is perfectly structured.
* **🎯 Local Context Engineering:** Optimized prompt handling to keep the data payload dense (under ~1050 tokens) to prevent local LLM hallucination and context overflow.
* **💾 Auto-PDF Generator:** Automatically compiles the final JSON output into a beautifully styled, downloadable `.pdf` bundle.
* **💬 Streaming UI:** A sleek, conversational interface built with Chainlit.

## 🛠️ Tech Stack

* **Frontend:** Chainlit
* **Orchestration:** CrewAI
* **Local LLM Server:** Qwen (served locally)
* **PDF Processing:** PyPDF2 / ReportLab (or your specific PDF libraries)
* **Language:** Python

## 🚀 Getting Started

### Prerequisites
* Python 3.10+
* A local LLM server running Qwen on port `8000` (e.g., via LM Studio, Ollama, or vLLM).

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/SUFIYAN2004/local-ats-resume-optimizer.git](https://github.com/SUFIYAN2004/local-ats-resume-optimizer.git)
   cd local-ats-resume-optimizer


2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

```


3. **Install dependencies:**
```bash
pip install -r requirements.txt

```


4. **Ensure your local model is running:**
Verify that your local Qwen model is actively listening on `http://localhost:8000`.

### Running the App

Start the Chainlit interface:

```bash
chainlit run app.py -w

```

Navigate to `http://localhost:8000` (or the port Chainlit assigns) in your browser. Upload your PDF and watch the agents work!

## 📂 Project Structure

```text
├── app.py                 # Chainlit UI and main event loop
├── agents.py              # CrewAI agent definitions
├── tasks.py               # Task definitions for the crew
├── crew.py                # JSON parsing and cleaning utilities
├── pdf_generator.py       # Text extraction and final PDF compilation
├── requirements.txt       # Project dependencies
└── README.md              

```

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://www.google.com/search?q=https://github.com/SUFIYAN2004/local-ats-resume-optimizer/issues).
