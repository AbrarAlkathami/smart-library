import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings

client = chromadb.PersistentClient(
    path="/Users/aalkathami001/Desktop/3rd week/Mon/task2/app/books_vector_db",
    settings=Settings(),
    tenant=DEFAULT_TENANT,
    database=DEFAULT_DATABASE,
)
collection = client.get_or_create_collection(name="books_collection")

# client.delete_collection(name="books_collection")
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
