import React, { useState } from 'react';
import { sendMessageToChatBot } from '../../services/chat.ts';
import styles from './chatbot.module.css'; 
import {Message} from '../../types/message.ts'


const ChatBotWindow: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>('');

  const handleSend = async () => {
    if (input.trim()) {
      const newMessage: Message = { text: input, sender: 'user' };
      setMessages([...messages, newMessage]);
      setInput('');

      try {
        const data = await sendMessageToChatBot('your_session_id', input); 
        const botResponse: Message = { text: data.response, sender: 'bot' };
        setMessages((prevMessages) => [...prevMessages, botResponse]);
      } catch (error) {
        console.error('Error:', error);
        const errorResponse: Message = { text: 'Sorry, something went wrong.', sender: 'bot' };
        setMessages((prevMessages) => [...prevMessages, errorResponse]);
      }
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <div className={styles.chatbotWindow}>
      AI ChatBot
      <div className={styles.chatbotContainer}>
        <div className={styles.chatbotContent}>
          <div className={styles.messages}>
            {messages.map((message, index) => (
              <div key={index} className={`${styles.message} ${message.sender === 'user' ? styles.messageUser : styles.messageBot}`}>
                {message.text}
              </div>
            ))}
          </div>
        </div>
        <input
          type="text"
          className={styles.query}
          id="query"
          name="query"
          placeholder="Insert text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
        />
      </div>
    </div>
  );
};

export default ChatBotWindow;
