import React from 'react';
import styles from './header.module.css';
import UserDropdown from './user_dropdown/user.tsx';
import {PageHeaderProps} from '../../types/header.ts'

const PageHeader: React.FC<PageHeaderProps> = ({ handleShowForm, setCurrentPage }) => {
  const handleLibraryClick = () => {
    setCurrentPage('home');
  };

  return (
    <div>
      <div className={styles.pageHeader}>
        <div className={styles.headerLeft} onClick={handleLibraryClick}>
          Library
        </div>
        <div className={styles.headerRight}>
          <UserDropdown handleShowForm={handleShowForm} />
        </div>
      </div>
      <div className={styles.divLine}></div>
    </div>
  );
};

export default PageHeader;
