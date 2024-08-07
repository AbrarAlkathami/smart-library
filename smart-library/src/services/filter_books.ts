import { Book } from '../types/book';

const getToken = () => localStorage.getItem('token');

export const filterBooksFromAPI = async (filter: string): Promise<Book[]> => {
  const token = getToken();
  const response = await fetch(`http://127.0.0.1:8000/books/${filter}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  if (!response.ok) {
    throw new Error("Failed to filter books");
  }
  return response.json();
};