import streamlit as st
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import HuggingFacePipeline
from transformers import pipeline
import hashlib

st.header("My First ChatBot")

# --- File Upload ---
with st.sidebar:
    st.title("Your Documents")
    file = st.file_uploader("Upload a PDF file", type="pdf")

# --- Helper: hash the uploaded file ---
def get_file_hash(uploaded_file):
    file_content = uploaded_file.read()
    uploaded_file.seek(0)  # Reset pointer
    return hashlib.md5(file_content).hexdigest()

# --- Vector Store Build: only if file is new ---
if file:
    file_hash = get_file_hash(file)

    # Only build vector store if new file or not cached
    if st.session_state.get("file_hash") != file_hash:
        st.session_state.file_hash = file_hash  # Update hash
        st.session_state.vector_store = None    # Clear previous cache if any

        # Extract text from PDF
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n"],
            chunk_size=1000,
            chunk_overlap=150,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        st.write("Chunks created:", len(chunks))

        # Generate embeddings and vector store
        with st.spinner("Loading embeddings and building vector store..."):
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            vector_store = FAISS.from_texts(chunks, embeddings)
            st.session_state.vector_store = vector_store
            st.success("Vector store ready!")

# --- Question Input + Answer Generation ---
if "vector_store" in st.session_state and st.session_state.vector_store is not None:
    user_question = st.text_input("Type your question here")

    if user_question:
        with st.spinner("Searching for relevant content and generating response..."):
            matches = st.session_state.vector_store.similarity_search(user_question, k=3)
            context = "\n\n".join([match.page_content for match in matches])

            hf_generator = pipeline(
                "text-generation",
                model="google/flan-t5-base",
                tokenizer="google/flan-t5-base",
                max_new_tokens=300,
                do_sample=True,
                temperature=0.7,
                top_k=50,
                top_p=0.95
            )

            llm = HuggingFacePipeline(pipeline=hf_generator)

            prompt = f"Answer the question based on the following context:\n\n{context}\n\nQuestion: {user_question}"

            try:
                response = llm.invoke(prompt)
                st.markdown("### Answer:")
                st.write(response if isinstance(response, str) else response[0]['generated_text'])
            except Exception as e:
                st.error(f"Error generating response: {e}")
