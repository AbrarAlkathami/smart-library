import { TokenResponse } from '../types/user';

export const loginUser = async (username: string, password: string): Promise<TokenResponse> => {

  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  
  const response = await fetch('http://127.0.0.1:8000/users/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData.toString(),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Login failed: ${errorText}`);
  }

  const data: TokenResponse = await response.json();
  return data;
};
