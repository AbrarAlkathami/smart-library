import React, { useState, useEffect } from 'react';
import { signUpUser } from '../../../services/fetch_signup.ts';
import { RegisterResponse } from '../../../types/user.ts';
import styles from './signup_form.module.css';

type SignUpFormProps = {
  setCurrentPage: React.Dispatch<React.SetStateAction<string>>;
  setShowPreferences: React.Dispatch<React.SetStateAction<boolean>>;
};

const SignUpForm: React.FC<SignUpFormProps> = ({ setCurrentPage, setShowPreferences }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [user, setUser] = useState<RegisterResponse | null>(null);
  const [isLongEnough, setIsLongEnough] = useState(false);
  const [hasNumber, setHasNumber] = useState(false);
  const [noSymbols, setNoSymbols] = useState(true);
  const [hasStartedTyping, setHasStartedTyping] = useState(false);

  useEffect(() => {
    setIsLongEnough(password.length >= 8);
    setHasNumber(/\d/.test(password));
    setNoSymbols(/^[a-zA-Z0-9]*$/.test(password));
  }, [password]);

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(e.target.value);
    setHasStartedTyping(true);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      const data = await signUpUser(username, password);
      setUser(data);
      setError('');
      localStorage.setItem('token', data.access_token);
      setShowPreferences(true);
      setCurrentPage('preferences');
    } catch (err) {
      const errorMessage = (err as Error).message.startsWith('Registration failed:')
        ? JSON.parse((err as Error).message.replace('Registration failed: ', '')).detail
        : 'An unexpected error occurred';
      setError(errorMessage);
    }
  };

  return (
    <div className={styles.formContainerSignup}>
      <div className={styles.loginSignupName}>Sign Up</div>
      {user && <div className={styles.success}>Registered successfully!</div>}
      <form onSubmit={handleSubmit}>
        <div className={styles.formGroup}>
          <label htmlFor="username">Username</label>
          <input type="text" id="username" name="username" placeholder='Username' required value={username} onChange={(e) => setUsername(e.target.value)} />
        </div>
        <div className={styles.formGroup}>
          <label htmlFor="password">Password</label>
          <input type="password" id="password" name="password" placeholder='Password' required value={password} onChange={handlePasswordChange} />
        </div>
        <div className={styles.passwordInstructions}>
          Ensure password has:
          <ul>
            <li className={hasStartedTyping && isLongEnough ? styles.valid : ''}>8 characters or more</li>
            <li className={hasStartedTyping && hasNumber ? styles.valid : ''}>At least one number</li>
            <li className={hasStartedTyping && noSymbols ? styles.valid : ''}>No symbols</li>
          </ul>
        </div>
        {error && <div className={styles.error}>{error}</div>}
        <button type="submit">Sign Up</button>
      </form>
    </div>
  );
};

export default SignUpForm;
