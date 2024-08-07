export type User = {
  username: string;
  password: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type RegisterResponse = {
  access_token: string;
  token_type: string;
  username: string;
  password: string; 
  role: string;    
};

export type UserDropdownProps = {
  handleShowForm: (form: string) => void;
};
