import React, { useState , useEffect} from 'react';
import './form.css';
import { signUpUser } from '../../api/fetch_signup.ts';
import { RegisterResponse } from '../../types/user.ts';

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
      // Store the token in local storage
      localStorage.setItem('token', data.access_token);
      // Navigate to preferences form after successful registration
      setShowPreferences(true);
      setCurrentPage('preferences'); // Set the current page to 'preferences'
    } catch (err) {
      const errorMessage = err.message.startsWith('Registration failed:')
        ? JSON.parse(err.message.replace('Registration failed: ', '')).detail
        : 'An unexpected error occurred';
      setError(errorMessage);
    }
  };

  return (
    <div className="form-container-signup">
      <div className='login-signup-name'>Sign Up</div>
      {user && <div className="success">Registered successfully!</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input type="text" id="username" name="username" placeholder='Username' required value={username} onChange={(e) => setUsername(e.target.value)} />
        </div>
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input type="password" id="password" name="password" placeholder='Password' required value={password} onChange={handlePasswordChange} />
        </div>
        <div className='password-instructions'>
          Ensure password has:
          <ul>
            <li className={hasStartedTyping && isLongEnough ? 'valid' : ''}>8 characters or more</li>
            <li className={hasStartedTyping && hasNumber ? 'valid' : ''}>At least one number</li>
            <li className={hasStartedTyping && noSymbols ? 'valid' : ''}>No symbols</li>
          </ul>
        </div>
        {error && <div className="error">{error}</div>}
        <button type="submit">Sign Up</button>
      </form>
    </div>
  );
};

export default SignUpForm;