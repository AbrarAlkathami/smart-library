from common.database.chromaDB import *
from sentence_transformers import SentenceTransformer
from  sqlalchemy.orm import Session
from schemas.book import *
from common.database.models import*

def add_book_chromadb(book_id: str, authors: List[str], book_info : BookSchema ):
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Convert the authors list to a comma-separated string
    authors_str = ', '.join(authors)

    # Extract book information for embedding
    combined_text = f"{book_info.title} {book_info.subtitle or ''} " \
                    f"{authors_str} " \
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
        'title': book_info.title or '',
        'subtitle': book_info.subtitle or '',
        'authors': authors_str,  # Convert list to string
        'published_year': book_info.published_year or '',
        'average_rating': book_info.average_rating or '',
        'num_pages': book_info.num_pages or '',
        'ratings_count': book_info.ratings_count or '',
        'genre': book_info.genre or '',
        'description': book_info.description or ''
    }

    collection.add(
        documents=[{'book_info': combined_text}],  # Store combined text
        embeddings=[combined_embedding],
        ids=[str(book_id)],
        metadatas=[metadata]  # Metadata is now properly formatted
    )
    print("Documents added to the collection successfully.")
    return "Documents added to the collection successfully."


def get_similarity(query_text : str):
    results = collection.query(
        query_texts=[query_text]
    )
    return results['metadatas']


