import { Book } from '../types/book';

export const fetchBooksFromAPI = async (): Promise<Book[]> => {
  const response = await fetch("http://127.0.0.1:8000/books");
  if (!response.ok) {
    throw new Error("Failed to fetch books");
  }
  return response.json();
};