<div align="center">

# 🎓 PhyChat — Local RAG Physics Chatbot

<!-- Add a demo screenshot or GIF here later -->

**Ask a physics question. Get an answer grounded in the textbook — not a guess.**

100% local RAG chatbot. No API key, no cloud cost, no internet required at inference time — the LLM, the embeddings, and the vector store all run on your own machine via [Ollama](https://ollama.com/).

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-RAG-1C3C3C)](https://www.langchain.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-000000?logo=ollama&logoColor=white)](https://ollama.com/)

</div>

---

## Why this exists

Most chatbots answer physics questions whether or not they actually know the syllabus — a confident wrong answer is worse than no answer. PhyChat's prompt hard-constrains the model: if the answer isn't in the textbook chunks it retrieved, it says so instead of guessing from general knowledge.

## How it works

```
PDF → split into chunks → embed (bge-m3) → Chroma vector store (persisted once)
                                                      │
question → MMR retrieve top-3 chunks → prompt (context + memory) → Ollama (mistral) → answer
                                                                          │
                                                          LaTeX in $...$ rendered as real math
```

The vector store is built **once** and cached to disk in `vectorDB/` — a fresh clone of this repo already includes a prebuilt index, so it works immediately.

## Features

- 🔒 Refuses to answer outside the textbook's content
- 🖥️ Fully local — zero API key, zero per-token cost
- 🧠 Conversational memory within a session
- 💾 Persistent vector index — instant startup after the first run
- 🧮 Renders LaTeX formulas as real math, not raw text

## Setup

```bash
git clone https://github.com/Iman-Howlader/LLM-RAG-Based-Physics-Chatbot-CSE299.git
cd LLM-RAG-Based-Physics-Chatbot-CSE299
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt langchain-community pypdf   # both needed, missing from requirements.txt
```

Pull the models and make sure Ollama is running:
```bash
ollama pull mistral
ollama pull bge-m3
ollama serve
```

## Run it

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`. Try: *"What is Newton's second law of motion?"*

## Using your own PDF

Replace `pdfFiles/Physics-class10.pdf` (or change `PDF_PATH` in `app.py`), then **delete the `vectorDB/` folder** — it only rebuilds when that folder is missing/empty, so skipping this step silently keeps querying the old textbook.

## Known limitations

- One PDF at a time, no multi-document ingestion
- No source citations shown in the UI (chain supports it, just not wired in)
- No streaming responses; memory resets on restart
- `requirements.txt` is missing `langchain-community` and `pypdf` (see Setup above)
- PDF + Chroma DB committed directly to git, no `.gitignore`, no license file

## License

None yet — [MIT](https://choosealicense.com/licenses/mit/) is a reasonable default to add.

---

<div align="center">
A CSE299 project — proving an LLM can be useful for studying <em>without</em> making things up.
</div>
