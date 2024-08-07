import React, { useState, ChangeEvent, KeyboardEvent } from 'react';
import styles from './search_bar.module.css';
import SearchIcon from '../icons/search-icon.tsx';
import FilterIcon from '../icons/filter-icon.tsx';
import LikeSearchBarIcon from '../icons/search-bar-like.tsx';
import { Book } from '../../types/book.ts';

type SearchBarProps = {
  searchBooks: (query: string) => void;
  filterBooks: (filter: string) => void;
  fetchLikedBooks: () => Promise<void>;
};

const SearchBar: React.FC<SearchBarProps> = ({ searchBooks, filterBooks, fetchLikedBooks }) => {
  const [query, setQuery] = useState<string>('');
  const [isDropdownVisible, setDropdownVisible] = useState<boolean>(false);

  const handleInputChange = (event: ChangeEvent<HTMLInputElement>) => {
    setQuery(event.target.value);
  };

  const handleSearchClick = () => {
    searchBooks(query);
  };

  const handleKeyPress = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      searchBooks(query);
    }
  };

  const toggleDropdown = () => {
    setDropdownVisible(!isDropdownVisible);
  };

  const handleFilterClick = (filter: string) => {
    filterBooks(filter);
    setDropdownVisible(false);
  };

  const handleLikedBooksClick = async () => {
    try {
      await fetchLikedBooks();
    } catch (error) {
      console.error("Error fetching liked books:", error);
      window.alert("Error fetching liked books: " + (error as Error).message);
    }
  };

  return (
    <div className={styles.searchBar}>
      <div className={styles.searchIcon} onClick={handleSearchClick}>
        <SearchIcon />
      </div>
      <div className={styles.searchInputContainer}>
        <input
          placeholder="Type book title"
          type="text"
          className={styles.input}
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyPress}
        />
      </div>
      <div className={styles.filterIcon} onClick={toggleDropdown}>
        <FilterIcon />
        {isDropdownVisible && (
          <div className={styles.dropdownMenuFilter}>
            <div className={styles.dropdownMostTrending} onClick={() => handleFilterClick('mostTrending')}>Most Trending</div>
            <div className={styles.dropdownMostRecentlyAdded} onClick={() => handleFilterClick('recentlyAdded')}>Most Recently Added</div>
            <div className={styles.dropdownRecommended} onClick={() => handleFilterClick('recommended')}>Recommended</div>
            <div className={styles.dropdownMostRecentPublishedYear} onClick={() => handleFilterClick('recentPublishedYear')}>Most Recent Published Year</div>
            <div className={styles.dropdownEarliestPublishedYear} onClick={() => handleFilterClick('earliestPublishedYear')}>Earliest Published Year</div>
            <div className={styles.dropdownTopRated} onClick={() => handleFilterClick('topRated')}>Top Rated</div>
            <div className={styles.dropdownLeastRated} onClick={() => handleFilterClick('leastRated')}>Least Rated</div>
          </div>
        )}
      </div>
      <div className={styles.likeIcon}>
        <LikeSearchBarIcon onClick={handleLikedBooksClick} />
      </div>
    </div>
  );
};

export default SearchBar;
