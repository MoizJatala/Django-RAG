from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.faiss import InMemoryDocstore
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from transformers import pipeline
from langchain_community.llms import HuggingFacePipeline
from sentence_transformers import SentenceTransformer
from faiss import IndexFlatL2
import numpy as np
import os
from scipy.spatial import distance
import pandas as pd

app = FastAPI()

# In-memory vector database (use persistent storage for production)
vectorstore = None

class QueryInput(BaseModel):
    question: str

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    global vectorstore

    # Step 1: Save the uploaded file temporarily
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await file.read())

    try:
        if file.content_type == "application/pdf":
            from PyPDF2 import PdfReader
            reader = PdfReader(temp_file_path)
            content = "\n".join(page.extract_text() for page in reader.pages)
        elif file.content_type == "text/plain":
            with open(temp_file_path, "r") as text_file:
                content = text_file.read()
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")
    finally:
        os.remove(temp_file_path)

    # Step 2: Process the document
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_text(content)

    # Step 3: Generate embeddings using SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = np.array([model.encode(text) for text in texts])

    # Step 4: Create FAISS index
    index = IndexFlatL2(embeddings.shape[1])  # Initialize FAISS index
    index.add(embeddings)  # Add embeddings to the index

    # Step 5: Create InMemoryDocstore
    docstore = InMemoryDocstore({str(i): Document(page_content=texts[i]) for i in range(len(texts))})

    # Step 6: Create index_to_docstore_id mapping
    index_to_docstore_id = {i: str(i) for i in range(len(texts))}

    # Step 7: Store the FAISS vectorstore
    vectorstore = FAISS(
        index=index,
        docstore=docstore,
        index_to_docstore_id=index_to_docstore_id,
        embedding_function=model.encode
    )

    return {"message": "Document uploaded and processed successfully."}

from scipy.spatial import distance
import pandas as pd

@app.post("/query")
async def query_document(query: QueryInput):
    if vectorstore is None:
        raise HTTPException(status_code=400, detail="No document uploaded yet.")

    # Step 1: Embed the query
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = model.encode(query.question)

    # Step 2: Retrieve all document chunks and calculate relatedness
    embeddings = vectorstore.index.reconstruct_n(0, vectorstore.index.ntotal)
    texts = [vectorstore.docstore.search(str(i)).page_content for i in range(len(embeddings))]

    # Create a DataFrame for storing embeddings and texts
    df = pd.DataFrame({"text": texts, "embeddings": embeddings.tolist()})

    # Define relatedness function
    def relatedness_fn(x, y):
        return 1 - distance.cosine(x, y)

    # Calculate relatedness scores
    strings_and_relatednesses = [
        (row["text"], relatedness_fn(query_embedding, row["embeddings"]))
        for _, row in df.iterrows()
    ]
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)

    # Filter by threshold (e.g., 0.7)
    threshold = 0.1
    related_texts = [(text, score) for text, score in strings_and_relatednesses if score >= threshold]

    # Return "no answer" if no chunks meet the threshold
    if not related_texts:
        return {"answer": "The document does not contain relevant information."}

    # Step 3: Use top related text as context for the Hugging Face LLM
    hf_pipeline = pipeline("text2text-generation", model="google/flan-t5-base")
    hf_llm = HuggingFacePipeline(pipeline=hf_pipeline)

    # Combine the top related chunks into a single context
    context = "\n".join([text for text, _ in related_texts[:3]])  # Top 3 chunks as context
    prompt = f"Context: {context}\n\nQuestion: {query.question}\n\nAnswer:"
    answer = hf_llm(prompt)

    return {
        "answer": answer,
        "relatedness_scores": [score for _, score in related_texts]
    }
