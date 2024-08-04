import React, { useState, ChangeEvent, KeyboardEvent } from 'react';
import './search_bar.css';
import SearchIcon from '../icons/search-icon.tsx';
import FilterIcon from '../icons/filter-icon.tsx';
import LikeSearchBarIcon from '../icons/search-bar-like.tsx';

type SearchBarProps = {
  searchBooks: (query: string) => void;
  filterBooks: (filter: string) => void;
};

const SearchBar: React.FC<SearchBarProps> = ({ searchBooks, filterBooks }) => {
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
    setDropdownVisible(false); // Close the dropdown after selecting a filter
  };

  return (
    <div className="search-bar" id="poda">
      <div className="search-icon" onClick={handleSearchClick}>
        <SearchIcon />
      </div>
      <div className='search-input-container'>
        <input
          placeholder="Type book title"
          type="text"
          name="text"
          className="input"
          id="searchInput"
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyPress}
        />
      </div>
      <div className="filter-icon" onClick={toggleDropdown}>
        <FilterIcon />
        {isDropdownVisible && (
          <div className="dropdown-menu-filter">
            <div className="dropdown-most-trending" onClick={() => handleFilterClick('mostTrending')}>Most Trending</div>
            <div className="dropdown-most-recently-added" onClick={() => handleFilterClick('recentlyAdded')}>Most Recently Added</div>
            <div className="dropdown-recommended" onClick={() => handleFilterClick('recommended')}>Recommended</div>
            <div className="dropdown-most-recent-published-year" onClick={() => handleFilterClick('recentPublishedYear')}>Most Recent Published Year</div>
            <div className="dropdown-earliest-published-year" onClick={() => handleFilterClick('earliestPublishedYear')}>Earliest Published Year</div>
            <div className="dropdown-top-rated" onClick={() => handleFilterClick('topRated')}>Top Rated</div>
            <div className="dropdown-least-rated" onClick={() => handleFilterClick('leastRated')}>Least Rated</div>
          </div>
        )}
      </div>
      <div className="like-icon">
        <LikeSearchBarIcon onClick={handleSearchClick} />
      </div>
    </div>
  );
};

export default SearchBar;
