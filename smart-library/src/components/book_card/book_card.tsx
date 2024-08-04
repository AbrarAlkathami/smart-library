import React, { useState } from 'react';
import './book_card.css';
import StarIcon from '../icons/star-icon.tsx';
import LikeIcon from '../icons/like-icon.tsx';
import LikedIcon from '../icons/liked-icon.tsx';
import { BookGalleryProps }  from '../../types/book.ts'



const LikedBook: React.FC<{ bookId: number }> = ({ bookId }) => {
  const [liked, setLiked] = useState(false);

  const handleLikeClick = () => {
    setLiked(!liked);
    console.log(`Book ID ${bookId} liked status: ${!liked}`);
    // Optionally, send the bookId to the server to update the liked status
  };

  return (
    <div className='book-like'>
      {liked ? <LikedIcon onClick={handleLikeClick} /> : <LikeIcon onClick={handleLikeClick} />}
    </div>
  );
};

const BookGallery: React.FC<BookGalleryProps> = ({ books, searchMessage }) => {
  return (
    <div className='book-gellery-container'>
    <div className="book-gallery" id="bookGallery">
      
      {searchMessage && <div className="search-message">{searchMessage}</div>}
      {books.map(book => (
        <div className="book-item" key={book.id}>
          <div className='title-like-container'>
            <div className="book-title">{book.title}</div>
            <LikedBook bookId={book.id} />
          </div>
          <div className='book-author-publish-container'>
            <div className="book-authors">{book.authors.map(author => author.name).join(", ")}</div>
            <div className="book-published-year">{book.published_year}</div>
          </div>
          <div className="cover-photo">
            <img
              className="img-photo"
              src={book.thumbnail && book.thumbnail.trim() !== '' ? book.thumbnail : ""}
              alt={`${book.title}`}
            />
          </div>
          <div className='book-genre-rating-container'>
            <div className="book-genre" data-tooltip={book.genre}>{book.genre}</div>
            <div className="book-average-rating">
                <div className='star-icon'>
                    <StarIcon 
                        avrgRating={(book.average_rating !== null ? book.average_rating : 0) / 6} 
                    />
                </div>
                <span className="rating-number">{book.average_rating !== null ? book.average_rating.toFixed(0) : 0}</span>
            </div>
          </div>
          <div className='book-description'>
            {book.description}
          </div>
          </div>
      ))}
    </div>
    </div>
  );
};

export default BookGallery;
