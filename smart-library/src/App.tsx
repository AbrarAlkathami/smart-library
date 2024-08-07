import React, { useEffect, useState } from 'react';
import PageHeader from './components/header/header.tsx';
import SearchBar from './components/search_bar/search_bar.tsx';
import BookGallery from './components/book_card/book_card.tsx';
import LoginSignUpForms from './pages/login_signup_forms/login_signup_page.tsx'; 
import UserPreferencesForm from './components/user/user_pref_form/user_pref_form.tsx'; 
import ChatBotWindow from './components/chatbot/chatbot.tsx';
import ChatBotIcon from './components/icons/chatbot-icon.tsx';
import { fetchBooksFromAPI } from './services/fetch_books.ts';
import { searchBooksFromAPI } from './services/search_books.ts';
import { filterBooksFromAPI } from './services/filter_books.ts';
import { fetchLikedBooksFromAPI } from './services/fetch_liked_books.ts';
import { Book } from './types/book.ts';
import styles from './App.module.css';

const App: React.FC = () => {
  const [books, setBooks] = useState<Book[]>([]);
  const [likedBooks, setLikedBooks] = useState<number[]>([]);
  const [searchMessage, setSearchMessage] = useState<string>('');
  const [currentPage, setCurrentPage] = useState<string>('home');
  const [showPreferences, setShowPreferences] = useState<boolean>(false);
  const [showChatbot, setShowChatbot] = useState<boolean>(false);

  useEffect(() => {
    if (currentPage === 'home') {
      fetchBooks();
      fetchLikedBooks();
    }
  }, [currentPage]);

  const fetchBooks = async () => {
    try {
      const books: Book[] = await fetchBooksFromAPI();
      setBooks(books);
    } catch (error) {
      console.error("Error fetching books:", error);
      window.alert("Error fetching books: " + (error as Error).message);
    }
  };

  const fetchLikedBooks = async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const likedBooks = await fetchLikedBooksFromAPI();
        setLikedBooks(likedBooks.map(book => book.book_id));
      } catch (error) {
        console.error("Error fetching liked books:", error);
        window.alert("Error fetching liked books: " + (error as Error).message);
      }
    } else {
      const likedBooks = JSON.parse(localStorage.getItem('likedBooks') || '[]');
      setLikedBooks(likedBooks);
    }
  };

  const searchBooks = async (query: string) => {
    try {
      const books: Book[] = await searchBooksFromAPI(query);
      if (books.length === 0) {
        setSearchMessage("No books found");
      } else {
        setSearchMessage("");
      }
      setBooks(books);
    } catch (error) {
      console.error("Error searching books:", error);
      window.alert("Error searching books: " + (error as Error).message);
    }
  };

  const filterBooks = async (filter: string) => {
    try {
      const books: Book[] = await filterBooksFromAPI(filter);
      if (books.length === 0) {
        setSearchMessage("No books found");
      } else {
        setSearchMessage("");
      }
      setBooks(books);
    } catch (error) {
      console.error("Error filtering books:", error);
      window.alert("Error filtering books: " + (error as Error).message);
    }
  };

  const handleShowForm = () => {
    setCurrentPage('login');
  };

  return (
    <div className={styles.container}>
      <PageHeader handleShowForm={handleShowForm} setCurrentPage={setCurrentPage} />
      {currentPage === 'login' ? (
        <LoginSignUpForms setCurrentPage={setCurrentPage} setShowPreferences={setShowPreferences} />
      ) : currentPage === 'preferences' && showPreferences ? (
        <UserPreferencesForm setCurrentPage={setCurrentPage} />
      ) : (
        <>
          <SearchBar 
            searchBooks={searchBooks} 
            filterBooks={filterBooks} 
            fetchLikedBooks={fetchLikedBooks} 
          />
          <BookGallery books={books} likedBooks={likedBooks} /> {/* Pass likedBooks to BookGallery */}
        </> 
      )}
      <ChatBotIcon onClick={() => setShowChatbot(!showChatbot)} />
      {showChatbot && <ChatBotWindow />}
    </div>
  );
};

export default App;
