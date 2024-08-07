import React, { useState, useEffect } from 'react';
import LikeIcon from '../icons/like-icon.tsx';
import LikedIcon from '../icons/liked-icon.tsx';
import { toggleLikeBook } from '../../services/like_books.ts';
import styles from './book_card.module.css';
import { LikedBookProps } from '../../types/book.ts';

const LikedBook: React.FC<LikedBookProps> = ({ bookId, isLiked }) => {
  const [liked, setLiked] = useState<boolean>(() => {
    const savedState = localStorage.getItem(`liked_${bookId}`);
    return savedState !== null ? JSON.parse(savedState) : isLiked;
  });

  useEffect(() => {
    localStorage.setItem(`liked_${bookId}`, JSON.stringify(liked));
  }, [liked, bookId]);

  useEffect(() => {
    setLiked(isLiked);
  }, [isLiked]);

  const handleLikeClick = async () => {
    const message = await toggleLikeBook(bookId);
    console.log(message);
    setLiked(!liked);
  };

  return (
    <div className={styles.bookLike}>
      {liked ? <LikedIcon onClick={handleLikeClick} /> : <LikeIcon onClick={handleLikeClick} />}
    </div>
  );
};

export default LikedBook;
