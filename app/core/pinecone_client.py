import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

# Pinecone Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "documents")

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

# Get or create index
def get_or_create_index():
    """Get existing index or create a new one for document embeddings"""
    existing_indexes = [index.name for index in pc.list_indexes()]

    if PINECONE_INDEX_NAME not in existing_indexes:
        # Create index with serverless spec (free tier compatible)
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=384,  # dimension for sentence-transformers/all-MiniLM-L6-v2
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region=PINECONE_ENVIRONMENT
            )
        )

    return pc.Index(PINECONE_INDEX_NAME)

# Initialize the index
index = get_or_create_index()