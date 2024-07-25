from common.database.chromaDB import *
from sentence_transformers import SentenceTransformer
from  sqlalchemy.orm import Session
from schemas.book import *

def add_book_chromadb(book_id: str, book_info : BookSchema):
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Extract book information for embedding
    combined_text = f"{book_info.title} {book_info.subtitle or ''} " \
                    f"{book_info.published_year or ''} " \
                    f"{book_info.average_rating or ''} " \
                    f"{book_info.num_pages or ''} " \
                    f"{book_info.ratings_count or ''} " \
                    f"{book_info.genre or ''} " \
                    f"{book_info.description or ''}"

    # Encode book information using the model
    combined_embedding = model.encode(combined_text).tolist()

    # Prepare metadata dictionary
    metadata = {
        'title': book_info.title,
        'subtitle': book_info.subtitle,
        'published_year': book_info.published_year,
        'average_rating': book_info.average_rating,
        'num_pages': book_info.num_pages,
        'ratings_count': book_info.ratings_count,
        'genre': book_info.genre,
        'description': book_info.description
    }

    collection.add(
        documents=[{'book_info': book_info.dict()}],  # Store entire BookSchema object as book_info
        embeddings=[combined_embedding],
        ids=[str(book_id)],
        metadatas=[metadata]  # Store metadata separately for querying
    )
    print("Documents added to the collection successfully.")
    return "Documents added to the collection successfully."



def get_similarity(query_text : str):
    results = collection.query(
        query_texts=[query_text],
        n_results=2
    )
    return results['documents']


