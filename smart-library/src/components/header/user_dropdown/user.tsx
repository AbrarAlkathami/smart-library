import React, { useState } from 'react';
import UserIcon from '../../icons/user-icon.tsx';
import styles from './user.module.css';
import {UserDropdownProps } from '../../../types/user.ts'


const UserDropdown: React.FC<UserDropdownProps> = ({ handleShowForm }) => {
  const [isDropdownVisible, setDropdownVisible] = useState(false);

  const toggleDropdown = () => {
    setDropdownVisible(!isDropdownVisible);
  };

  const handleOptionClick = (option: string) => {
    handleShowForm(option);
    setDropdownVisible(false);
  };

  return (
    <div className={styles.userDropdown}>
      <div className={styles.userIcon} onClick={toggleDropdown}>
        <UserIcon />
      </div>
      {isDropdownVisible && (
        <div className={styles.dropdownMenuUser}>
          <div className={styles.dropdownItem} onClick={() => handleOptionClick('login')}>Log In</div>
          <div className={styles.dropdownItem} onClick={() => handleOptionClick('signup')}>Sign Up</div>
        </div>
      )}
    </div>
  );
};

export default UserDropdown;
