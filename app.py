import os
import re
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

# ------------------- Config -------------------
LLM_MODEL = "mistral"
EMBED_MODEL = "bge-m3"
PDF_PATH = "pdfFiles/Physics-class10.pdf"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
PERSIST_DIR = "vectorDB"
RETRIEVER_K = 3
OLLAMA_BASE_URL = "http://localhost:11434"

# ------------------- Chat Styling -------------------
st.markdown("""
    <style>
    body { background: #f5f7fa; font-family: 'Poppins', sans-serif; }
    .user-msg { 
        background-color: #cce5ff; 
        padding: 10px; 
        border-radius: 12px; 
        margin-bottom:5px; 
        font-weight:bold; 
        color: black;   /* <-- added */
    }
    .assistant-msg { 
        background-color: #d4edda; 
        padding: 10px; 
        border-radius: 12px; 
        margin-bottom:5px; 
        font-weight:normal; 
        color: black;   /* <-- added */
    }
    .assistant-heading { font-size:18px; font-weight:bold; color:#1a7f37; }
    .assistant-text { font-size:16px; line-height:1.5; }
    .latex-block { background-color:#f0f0f0; padding:8px; border-radius:6px; margin:5px 0; font-family: 'Courier New', monospace; color:black; }
</style>

""", unsafe_allow_html=True)

# ------------------- Session Init -------------------
def init_session():
    os.makedirs(os.path.dirname(PDF_PATH), exist_ok=True)
    os.makedirs(PERSIST_DIR, exist_ok=True)

    st.session_state.setdefault("chat_history", [])
    st.session_state.setdefault("template", """You are a helpful assistant answering questions only based on the provided physics textbook.
If the answer is not directly found in the textbook context, respond with "I'm sorry, I can only answer based on the provided textbook content."

Context (from textbook only): {context}
User History: {history}

User: {question}
Chatbot (based on textbook content only):""")
    st.session_state.setdefault("prompt",
        PromptTemplate(
            input_variables=["history", "context", "question"],
            template=st.session_state.template,
        )
    )
    st.session_state.setdefault("memory",
        ConversationBufferMemory(
            memory_key="history",
            return_messages=True,
            input_key="question",
        )
    )

# ------------------- Vector Store -------------------
def load_vectorstore():
    if "vectorstore" in st.session_state:
        return

    needs_build = (not os.path.exists(PERSIST_DIR)) or (len(os.listdir(PERSIST_DIR)) == 0)

    if needs_build:
        if not os.path.exists(PDF_PATH):
            st.error(f"Missing PDF at {PDF_PATH}. Please add your textbook PDF.")
            st.stop()
        loader = PyPDFLoader(PDF_PATH)
        data = loader.load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len
        )
        splits = splitter.split_documents(data)
        st.session_state.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_BASE_URL),
            persist_directory=PERSIST_DIR
        )
        st.session_state.vectorstore.persist()
    else:
        st.session_state.vectorstore = Chroma(
            persist_directory=PERSIST_DIR,
            embedding_function=OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_BASE_URL)
        )

# ------------------- LLM and QA Chain -------------------
def load_llm_and_chain():
    if "llm" not in st.session_state:
        st.session_state.llm = Ollama(
            base_url=OLLAMA_BASE_URL,
            model=LLM_MODEL,
            verbose=False
        )
    if "qa_chain" not in st.session_state:
        st.session_state.retriever = st.session_state.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": RETRIEVER_K}
        )
        st.session_state.qa_chain = RetrievalQA.from_chain_type(
            llm=st.session_state.llm,
            chain_type="stuff",
            retriever=st.session_state.retriever,
            verbose=False,
            chain_type_kwargs={
                "prompt": st.session_state.prompt,
                "memory": st.session_state.memory
            }
        )

# ------------------- Chat UI -------------------
def run_chat_ui():
    st.title("🌟 PhyChat: Ask your Physics Query")
    st.markdown("---")

    # Display last 5 messages
    for msg in st.session_state.chat_history[-5:]:
        if msg["role"] == "user":
            st.markdown(f"<div class='user-msg'>👨‍💻 You: {msg['message']}</div>", unsafe_allow_html=True)
        else:
            # Detect and render LaTeX
            response_text = msg['message']
            latex_blocks = re.findall(r"\$.*?\$", response_text)
            clean_text = re.sub(r"\$.*?\$", "", response_text)
            st.markdown(f"<div class='assistant-msg'><span class='assistant-heading'>🎓 PhyChat:</span><br><span class='assistant-text'>{clean_text}</span></div>", unsafe_allow_html=True)
            for block in latex_blocks:
                st.markdown(f"<div class='latex-block'>{block}</div>", unsafe_allow_html=True)
                st.latex(block.strip("$"))

    # Input
    if user_input := st.chat_input("Ask your physics question..."):
        st.session_state.chat_history.append({"role":"user","message":user_input})
        st.markdown(f"<div class='user-msg'>👨‍💻 You: {user_input}</div>", unsafe_allow_html=True)

        # Fast response
        response_text = st.session_state.qa_chain(user_input)["result"]

        # Render LaTeX and text
        latex_blocks = re.findall(r"\$.*?\$", response_text)
        clean_text = re.sub(r"\$.*?\$", "", response_text)
        st.markdown(f"<div class='assistant-msg'><span class='assistant-heading'>🎓 PhyChat:</span><br><span class='assistant-text'>{clean_text}</span></div>", unsafe_allow_html=True)
        for block in latex_blocks:
            st.markdown(f"<div class='latex-block'>{block}</div>", unsafe_allow_html=True)
            st.latex(block.strip("$"))

        st.session_state.chat_history.append({"role":"assistant","message":response_text})

# ------------------- Main -------------------
def main():
    init_session()
    load_vectorstore()
    load_llm_and_chain()
    run_chat_ui()

if __name__ == "__main__":
    main()
