import React, { ReactNode } from 'react';
import './button.css';

type ButtonProps= {
  icon?: ReactNode;
  onClick: () => void;
  children: string;
}

const Button: React.FC<ButtonProps> = ({ icon, onClick, children }) => (
  <div id="button" onClick={onClick}>
    {icon && <span className="icon">{icon}</span>}
    {children}
  </div>
);

export default Button;
