import { RegisterResponse } from '../types/user.ts';

export const signUpUser = async (username: string, password: string): Promise<RegisterResponse> => {
  const response = await fetch('http://127.0.0.1:8000/users/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Registration failed: ${errorText}`);
  }

  const data: RegisterResponse = await response.json();
  localStorage.setItem('token', data.access_token);
  return data;
};
