import React from 'react';
import './header.css';
import UserDropdown from './user_dropdown/user.tsx';

type PageHeaderProps = {
  handleShowForm: (form: string) => void;
  setCurrentPage: React.Dispatch<React.SetStateAction<string>>;
};

const PageHeader: React.FC<PageHeaderProps> = ({ handleShowForm, setCurrentPage }) => {
  const handleLibraryClick = () => {
    setCurrentPage('home');
  };

  return (
    <div>
      <div className="page-header">
        <div className="header-left" onClick={handleLibraryClick} >
          Library
        </div>
        <div className="header-right">
          <UserDropdown handleShowForm={handleShowForm} />
        </div>
      </div>
      <div className="div-line"></div>
    </div>
  );
};

export default PageHeader;
