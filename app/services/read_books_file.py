import pandas as pd
# from common.CRUD.book_crud import*
# from common.CRUD.author_crud import*

df = pd.read_csv('cleaned_books.csv' , usecols=['title', 'authors' , 'categories' , 'description'])

for index, row in df.iterrows():
     print(index, " ",row)
