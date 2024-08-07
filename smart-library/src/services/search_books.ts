import { Book } from '../types/book';

export const searchBooksFromAPI = async (query: string): Promise<Book[]> => {
  const response = await fetch(`http://127.0.0.1:8000/books/search/${encodeURIComponent(query)}`);
  if (!response.ok) {
    throw new Error("Failed to search books");
  }
  return response.json();
};