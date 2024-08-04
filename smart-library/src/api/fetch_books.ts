import { Book } from '../types/book';

const getToken = () => localStorage.getItem('token');

export const fetchBooksFromAPI = async (): Promise<Book[]> => {
  const token = getToken();
  const response = await fetch("http://127.0.0.1:8000/books", {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  if (!response.ok) {
    throw new Error("Failed to fetch books");
  }
  return response.json();
};
