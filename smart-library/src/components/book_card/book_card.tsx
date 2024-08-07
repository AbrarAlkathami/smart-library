import React from 'react';
import StarIcon from '../icons/star-icon.tsx';
import { Book } from '../../types/book.ts';
import styles from './book_card.module.css';
import LikedBook from './liked_book.tsx';

type BookGalleryProps = {
  books: Book[];
  likedBooks: number[];
};

const BookGallery: React.FC<BookGalleryProps> = ({ books, likedBooks }) => {
  if (books.length === 0) {
    return <div>No books available</div>;
  }

  return (
    <div className={styles.bookGalleryContainer}>
      <div className={styles.bookGallery} id="bookGallery">
        {books.map(book => (
          <div className={styles.bookItem} key={book.book_id}>
            <div className={styles.titleLikeContainer}>
              <div className={styles.bookTitle}>{book.title}</div>
              <LikedBook
                bookId={book.book_id}
                isLiked={likedBooks.includes(book.book_id)}
              />
            </div>
            <div className={styles.bookAuthorPublishContainer}>
              <div className={styles.bookAuthors}>{book.authors.map(author => author.name).join(", ")}</div>
              <div className={styles.bookPublishedYear}>{book.published_year}</div>
            </div>
            <div className={styles.coverPhoto}>
              <img
                className={styles.imgPhoto}
                src={book.thumbnail && book.thumbnail.trim() !== '' ? book.thumbnail : ""}
                alt={`${book.title}`}
              />
            </div>
            <div className={styles.bookGenreRatingContainer}>
              <div className={styles.bookGenre} data-tooltip={book.genre}>{book.genre}</div>
              <div className={styles.bookAverageRating}>
                <div className={styles.starIcon}>
                  <StarIcon avrgRating={(book.average_rating !== null ? Math.round(book.average_rating) : 0) / 5} />
                </div>
                <span className={styles.ratingNumber}>{book.average_rating !== null ? book.average_rating.toFixed(0) : 0}</span>
              </div>
            </div>
            <div className={styles.bookDescription}>
              {book.description}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BookGallery;
