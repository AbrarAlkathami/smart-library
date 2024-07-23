import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings

client = chromadb.PersistentClient(
    path="test",
    settings=Settings(),
    tenant=DEFAULT_TENANT,
    database=DEFAULT_DATABASE,
)
collection = client.get_or_create_collection(name="collection_name")

def store_books_in_vectorDB():
    # Check if the collection is empty before adding documents
    existing_documents = collection.count()
    if existing_documents > 0:
        print("Collection already populated with documents.")
        return "Documents already exist in the collection."

    # Load the CSV file
    df = pd.read_csv("cleaned_books.csv", usecols=['title', 'authors', 'categories', 'description'])

    # Initialize the sentence transformer model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Generate embeddings and prepare documents and IDs
    documents = []
    embeddings_list = []
    IDs = []
    for index, row in df.iterrows():
        text = ' '.join(row.astype(str).values)
        documents.append(text)
        embedding = model.encode(text).tolist()
        embeddings_list.append(embedding)
        IDs.append(str(index))

    # Add documents and embeddings to the collection
    collection.add(
        documents=documents,
        embeddings=embeddings_list,
        ids=IDs
    )
    return "Documents added to the collection successfully."

# Run this once to store documents in the collection
def similarity_text(query_text : str):
    results = collection.query(
        query_texts=query_text,
        n_results=2
    )
    return results['documents']
# print(similarity_text("what are the harry potter books?"))

# chroma_client = chromadb.Client()
# collection = chroma_client.create_collection(name="my_collection")
# df = pd.read_csv("cleaned_books.cvs", usecols=['title', 'authors', 'categories', 'description'])
# transformers_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
# for index, row in df.iterrows():
#     embeddings = transformers_model.encode(row)
#     # add the embedding here then use it instead of row 
#     collection.add(
#         embeddings,
#         index
#     )

# results = collection.query(
#     query_texts=["This is a query document about hawaii"], # Chroma will embed this for you
#     n_results=2 # how many results to return
# )
# print(results)

