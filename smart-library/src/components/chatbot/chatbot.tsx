import React, {useState} from 'react';
import { sendMessageToChatBot } from '../../api/chat.ts';
import './chatbot.css'; 

type Message = {
    text: string;
    sender: 'user' | 'bot';
  };
  
  const ChatBotWindow: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState<string>('');
  
    const handleSend = async () => {
      if (input.trim()) {
        const newMessage: Message = { text: input, sender: 'user' };
        setMessages([...messages, newMessage]);
        setInput('');
  
        try {
          const data = await sendMessageToChatBot('your_session_id', input); // replace with actual session id
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
      <div className="chatbot-window">
        AI ChatBot
        <div className='chatbot-container'>
        <div className="chatbot-content">
          <div className="messages">
            {messages.map((message, index) => (
              <div key={index} className={`message ${message.sender}`}>
                {message.text}
              </div>
            ))}
          </div>
        </div>
        <input
          type="text"
          className="query"
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