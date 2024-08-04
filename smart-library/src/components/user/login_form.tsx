import React, { useState } from 'react';
import './form.css';
import { loginUser } from '../../api/fetch_login.ts';
import { TokenResponse } from '../../types/user.ts';

type LoginFormProps = {
  setCurrentPage: React.Dispatch<React.SetStateAction<string>>;
}

const LoginForm: React.FC<LoginFormProps> = ({ setCurrentPage }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [token, setToken] = useState<TokenResponse | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      const data = await loginUser(username, password);
      setToken(data);
      setError('');
      // Store the token in local storage
      localStorage.setItem('token', data.access_token);
      // Handle successful login (e.g., navigate to home)
      setCurrentPage('home');
    } catch (err) {
      setError('Invalid username or password. Please try again.');
    }
  };

  return (
    <div className="form-container-login">
      <div className='login-signup-name'>Log In</div>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input type="text" id="username" name="username" placeholder='Username' required value={username} onChange={(e) => setUsername(e.target.value)} />
        </div>
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input type="password" id="password" name="password" placeholder='Password' required value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        {error && <div className="error">{error}</div>}
        <button type="submit">Log In</button>
      </form>
    </div>
  );
};

export default LoginForm;