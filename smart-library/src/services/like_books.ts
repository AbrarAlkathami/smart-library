const getToken = () => localStorage.getItem('token');

export const toggleLikeBook = async (bookId: number) => {
  const token = getToken();
  if (!token) {
    throw new Error('User is not authenticated');
  }

  try {
    const response = await fetch(`http://127.0.0.1:8000/toggle-like-book/${bookId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const data = await response.json();
    return data.message;
  } catch (error) {
    console.error('Error toggling like:', error);
    return 'Error toggling like';
  }
};