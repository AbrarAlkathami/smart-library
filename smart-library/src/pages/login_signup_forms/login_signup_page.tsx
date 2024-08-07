import React from 'react';
import LoginForm from '../../components/user/login_form/login_form.tsx';
import SignUpForm from '../../components/user/signup_form/signup_form.tsx';
import styles from './login_signup_forms.module.css';

type LoginSignUpFormsProps = {
  setCurrentPage: React.Dispatch<React.SetStateAction<string>>;
  setShowPreferences: React.Dispatch<React.SetStateAction<boolean>>;
};

const LoginSignUpForms: React.FC<LoginSignUpFormsProps> = ({ setCurrentPage, setShowPreferences }) => {
  return (
    <div className={styles.formContainer}>
      <LoginForm setCurrentPage={setCurrentPage} />
      <div className={styles.lineDiv}></div>
      <SignUpForm setCurrentPage={setCurrentPage} setShowPreferences={setShowPreferences} />
    </div>
  );
};

export default LoginSignUpForms;
