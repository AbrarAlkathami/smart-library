import React from 'react';
import './form.css';
import LoginForm from './login_form.tsx';
import SignUpForm from './signup_form.tsx';

type LoginSignUpFormsProps = {
    setCurrentPage: React.Dispatch<React.SetStateAction<string>>;
    setShowPreferences: React.Dispatch<React.SetStateAction<boolean>>;
  };
  
  const LoginSignUpForms: React.FC<LoginSignUpFormsProps> = ({ setCurrentPage, setShowPreferences }) => {
    return (
      <div className="form-container">
        <LoginForm setCurrentPage={setCurrentPage} />
        <div className='line-div'></div>
        <SignUpForm setCurrentPage={setCurrentPage} setShowPreferences={setShowPreferences} />
      </div>
    );
  };
  
  export default LoginSignUpForms;
