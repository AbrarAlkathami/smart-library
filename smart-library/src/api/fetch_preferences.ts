import { Preference } from '../types/user.ts'; // Make sure to define this type

export const createPreference = async (preference: Preference, token: string): Promise<Preference> => {
  const response = await fetch('http://127.0.0.1:8000/preferences', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`, // Include the token in the request
    },
    body: JSON.stringify(preference),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to add preference: ${errorText}`);
  }

  const data: Preference = await response.json();
  return data;
};

export const getPreferences = async (token: string): Promise<Preference[]> => {
  const response = await fetch('http://127.0.0.1:8000/api/preferences/', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`, // Include the token in the request
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to fetch preferences: ${errorText}`);
  }

  const data: Preference[] = await response.json();
  return data;
};