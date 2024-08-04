import React, { useEffect, useState } from 'react';
import PageHeader from './components/header/header.tsx';
import SearchBar from './components/search_bar/search_bar.tsx';
import BookGallery from './components/book_card/book_card.tsx';
import LoginSignUpForms from './components/user/login_signup_page.tsx'; 
import UserPreferencesForm from './components/user/user_pref_form.tsx'; 
import ChatBotWindow from './components/chatbot/chatbot.tsx'
import ChatBotIcon from './components/icons/chatbot-icon.tsx'
import { fetchBooksFromAPI } from './api/fetch_books.ts';
import { searchBooksFromAPI } from './api/search_books.ts';
import { filterBooksFromAPI } from './api/filter_books.ts';
import { Book } from './types/book.ts';
import './App.css';

const App: React.FC = () => {
  const [books, setBooks] = useState<Book[]>([]);
  const [searchMessage, setSearchMessage] = useState<string>('');
  const [currentPage, setCurrentPage] = useState<string>('home');
  const [showPreferences, setShowPreferences] = useState<boolean>(false);
  const [showChatbot, setShowChatbot] = useState<boolean>(false);

  useEffect(() => {
    if (currentPage === 'home') {
      fetchBooks();
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
    <div className="container">
      <PageHeader handleShowForm={handleShowForm} setCurrentPage={setCurrentPage} />
      {currentPage === 'login' ? (
        <LoginSignUpForms setCurrentPage={setCurrentPage} setShowPreferences={setShowPreferences} />
      ) : currentPage === 'preferences' && showPreferences ? (
        <UserPreferencesForm setCurrentPage={setCurrentPage} />
      ) : (
        <>
          <SearchBar searchBooks={searchBooks} filterBooks={filterBooks} />
          <BookGallery books={books} searchMessage={searchMessage} />
        </>
      )}
      <ChatBotIcon onClick={() => setShowChatbot(!showChatbot)} />
      {showChatbot && <ChatBotWindow />}
    </div>
  );
};

export default App;
