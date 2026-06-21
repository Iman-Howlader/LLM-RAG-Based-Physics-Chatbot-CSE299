# Document Q&A Website

This repository contains a FastAPI backend and a simple frontend for uploading documents and asking questions about them.

## Features

- Upload multiple documents at once
- Support for PDF, TXT, MD, HTML, DOCX, CSV, XLSX, and PPTX
- Stores documents in-memory per browser session using a session ID
- Uses embeddings and similarity search to answer questions from uploaded content
- Returns a polite fallback response when the answer is not found in uploaded documents

## Files

- `app.py` - FastAPI backend that loads documents, builds a Chroma vector store, and serves the chatbot API
- `index.html` - Frontend interface for uploading files, entering the Groq API key, and chatting
- `requirements.txt` - Python dependencies

## Setup

1. Create and activate a Python virtual environment.

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies.

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

## Run the app

```powershell
.\.venv\Scripts\python.exe -m uvicorn app:app --reload
```

Open your browser and go to:

- `http://127.0.0.1:8000`

or

- `http://localhost:8000`

## Usage

1. Enter your Groq API key in the sidebar.
2. Upload one or more supported documents.
3. Ask a question in the chat input.
4. If the question is not covered by uploaded documents, the app will respond with a fallback message.
## Login Portal

- Use the sidebar to register a new email and password.
- Log in to get a session token that keeps your uploads and chat history separate.
- Uploads and chat are protected per account.
- Use `Logout` to end the session.
## Notes

- The app currently uses an in-memory storage approach. Restarting the backend clears all uploaded data.
- In production, update CORS origins and do not allow `*` for security.
- If you add more file formats, update `app.py` in `load_single_file()`.

## Troubleshooting

- If files fail to upload, check the browser console and backend logs.
- Ensure your Groq API key is valid and entered correctly.
- Make sure `uvicorn` is running before using the frontend.
- If package install fails on Python 3.14, remove `pysqlite3-binary` from `requirements.txt` (already removed in this repo).
