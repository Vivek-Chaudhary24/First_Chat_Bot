# import streamlit as st
# from PyPDF2 import PdfReader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# #from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.vectorstores import FAISS
# from langchain.llms import HuggingFacePipeline
# from transformers import pipeline
#
# OPENAI_API_KEY = ""
# st.header("My First ChatBot")
#
# with st.sidebar:
#  st.title("Your Documents")
#
#  file = st.file_uploader("Upload a PDF file", type="pdf")
#
#  #extract the text
# if file is not None:
#  pdf_reader = PdfReader(file)
#  text=""
#  for page in pdf_reader.pages:
#    text+=page.extract_text()
#    #st.write(text)
# #Break it into chunks
#  text_splitter= RecursiveCharacterTextSplitter(
#   separators="\n",
#   chunk_size=1000,
#   chunk_overlap=150,
#   length_function=len
#  )
#  chunks=text_splitter.split_text(text)
#  st.write(chunks)
#
#  #generate Embeddings
#  #embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
#  with st.spinner("Loading embeddings..."):
#   embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
#
#  #creating vector store
#   vector_store = FAISS.from_texts(chunks,embeddings)
#   st.session_state.vector_store = vector_store
#   st.success("Vector store ready")
#
# if "vector_store" in st.session_state:
#  #get user question
#   user_question = st.text_input("Type your question here")
#  #do similiarity search
#   if user_question:
#    with st.spinner("Searching for relevant content"):
#     matches = vector_store.similarity_search(user_question,k=1)
#  #output results
#     context="\n\n".join([match.page_content if hasattr(match,"page_content") else match for match in matches])
#
#     hf_pipeline=pipeline(
#        "text-generation",
#        model="tiiuae/falcon-7b-instruct",
#        tokenizer="tiiuae/falcon-7b-instruct",
#        max_new_tokens=300,
#        do_sample=True,
#        temperature=0.7,
#        top_k=50,
#        top_p=0.95
#    )
#     llm=HuggingFacePipeline(pipeline=hf_pipeline)
#
#     prompt=f"Answer the question based on following context:\n\n{context}\n\nQuestion:{user_question}"
#     try:
#        response = llm.invoke(prompt)
#        st.markdown("### Answer:")
#        st.write(response)
#     except Exception as e:
#      st.error(f"Error generating response: {e}")
#      st.stop()