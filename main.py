import os
import streamlit as st
import pickle
import time
from langchain_openai import  OpenAI
from langchain_classic.chains import RetrievalQAWithSourcesChain
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


from dotenv import load_dotenv
from numba.cuda.libdevice import llmax

load_dotenv()

st.title('🌐 News Research Tool')
st.sidebar.title('News Articles URLs')

urls = []
for i in range(3):
    url = st.sidebar.text_input(f"URL {i+1}")
    urls.append(url)
main_placefolder = st.empty()
llm = OpenAI(temperature=0.9, max_tokens=500)
process_url_clicked = st.sidebar.button('Process URLs')
file_path = 'faiss_store_openai.pkl'
embeddings = OpenAIEmbeddings()
if process_url_clicked:
    #load data
    loader  = UnstructuredURLLoader(urls=urls)
    main_placefolder.text('Data Loading......Started....')
    data = loader.load()

    #split  data
    text_splitter = RecursiveCharacterTextSplitter(
        separators= ['\n\n', '\n', '.', ','],
        chunk_size= 1000
         )

    main_placefolder.text('Text Splitter.... Started...')


    docs = text_splitter.split_documents(data)

    #create embeddings


    vectorstore_openai = FAISS.from_documents(docs, embeddings)
    main_placefolder.text('Embedding Vector Started Building...')
    time.sleep(2)

    vectorstore_openai.save_local(file_path)

query = main_placefolder.text_input("Question: ")
if query :
    if os.path.exists(file_path):
        vectorstore = FAISS.load_local(file_path, embeddings, allow_dangerous_deserialization=True)

        chain = RetrievalQAWithSourcesChain.from_chain_type(
            llm= llm,
            retriever = vectorstore.as_retriever() )
        result = chain({'question': query}, return_only_outputs = True)

        #{'answer': "", "sorces" : [])
        st.header("Answer")
        st.write(result['answer'])


        #Display sources, if available
        sources = result.get('sources', "")

        if sources:
            st.subheader("Sources:")
            sources_list = sources.split('\n') # split the sources by newlines

            for source in sources_list:
                st.write(source)






