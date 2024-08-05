import React,{useState} from 'react';
import UserIcon from '../../icons/user-icon.tsx'; 
import './user.css'; 

type UserDropdownProps = {
  handleShowForm: (form: string) => void;
};

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
    <div className="user-dropdown">
      <div className="user-icon" onClick={toggleDropdown}>
        <UserIcon />
      </div>
      {isDropdownVisible && (
        <div className="dropdown-menu-user">
          <div className="dropdown-item" onClick={() => handleOptionClick('login')}>Log In</div>
          <div className="dropdown-item" onClick={() => handleOptionClick('signup')}>Sign Up</div>
        </div>
      )}
    </div>
  );
};

export default UserDropdown;
