import { Book } from '../types/book';

const getToken = () => localStorage.getItem('token');

export const fetchLikedBooksFromAPI = async (): Promise<Book[]> => {
  const token = getToken();
  if (!token) {
    console.log('User is not authenticated');
    return []; 
  }
  try {
    const response = await fetch("http://127.0.0.1:8000/liked-books", {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch liked books');
    }

    return response.json();
  } catch (error) {
    console.error('Error fetching liked books:', error);
    return []; 
  }
};