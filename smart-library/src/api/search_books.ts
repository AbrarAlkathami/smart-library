import { Book } from '../types/book.ts';

const getToken = () => localStorage.getItem('token');

export const searchBooksFromAPI = async (query: string): Promise<Book[]> => {
  const token = getToken();
  const response = await fetch(`http://127.0.0.1:8000/books/search/${encodeURIComponent(query)}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  if (!response.ok) {
    throw new Error("Failed to search books");
  }
  return response.json();
};