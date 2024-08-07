import { Author } from './author';

export type Book = {
  book_id: number;
  title: string;
  authors: Author[];
  published_year: number;
  thumbnail: string;
  genre: string;
  average_rating: number | null;
  description: string;
};


export type BookGalleryProps = {
  books: Book[];
  likedBooks: number[];

}

export type LikedBookProps = {
  bookId: number;
  isLiked: boolean;
};