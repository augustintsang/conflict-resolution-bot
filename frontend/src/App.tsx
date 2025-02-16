import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Bot } from 'lucide-react';
import { format } from 'date-fns';
import { Message, User } from './types';
import 'regenerator-runtime/runtime';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import { getGuidelines, MarkdownContent } from './utils/markdownReader';
import ReactMarkdown from 'react-markdown';

// Unique ID generator
const generateId = (() => {
  let counter = 0;
  return () => `${Date.now()}-${counter++}`;
})();

function App() {
  const [users, setUsers] = useState<User[]>([
    { id: '1', name: 'Jamy', isActive: false },
    { id: '2', name: 'Ravy', isActive: false },
    { id: '3', name: 'Aby', isActive: false },
  ]);

  const [messages, setMessages] = useState<Message[]>([]);
  const [currentUser, setCurrentUser] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const accumulatedTranscriptRef = useRef<string>('');

  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition
  } = useSpeechRecognition();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (listening && transcript) {
      accumulatedTranscriptRef.current = transcript;
    }
  }, [transcript, listening]);

  useEffect(() => {
    const cleanup = () => {
      if (listening) {
        SpeechRecognition.stopListening();
      }
    };
    
    return cleanup;
  }, [listening]);

  if (!browserSupportsSpeechRecognition) {
    return (
      <div className="min-h-screen bg-gray-100 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h1 className="text-2xl font-bold text-red-600">
              Browser Speech Recognition Not Supported
            </h1>
            <p className="mt-4">
              Your browser doesn't support speech recognition. Please try using a modern browser like Chrome.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const startRecording = async () => {
    try {
      resetTranscript();
      accumulatedTranscriptRef.current = '';
      await SpeechRecognition.startListening({ continuous: true });
    } catch (error) {
      console.error('Error starting speech recognition:', error);
      const errorMessage: Message = {
        id: generateId(),
        user: 'System',
        content: "Error starting speech recognition. Please try again.",
        timestamp: new Date(),
        isBot: true
      };
      addMessage(errorMessage);
    }
  };

  const stopRecording = () => {
    if (listening) {
      SpeechRecognition.stopListening();
      if (currentUser && accumulatedTranscriptRef.current.trim()) {
        const user = users.find(u => u.id === currentUser);
        if (user) {
          const transcribedMessage: Message = {
            id: generateId(),
            user: user.name,
            content: accumulatedTranscriptRef.current.trim(),
            timestamp: new Date(),
          };
          addMessage(transcribedMessage);
        }
      }
      resetTranscript();
      accumulatedTranscriptRef.current = '';
    }
  };

  const addMessage = (message: Message) => {
    setMessages(prevMessages => [...prevMessages, message]);
  };

  const toggleUserActive = (userId: string) => {
    setUsers(prevUsers => {
      const updatedUsers = prevUsers.map(u => ({
        ...u,
        isActive: u.id === userId ? !u.isActive : false
      }));
      
      const user = updatedUsers.find(u => u.id === userId);
      if (user) {
        if (user.isActive) {
          setCurrentUser(userId);
          startRecording();
        } else {
          stopRecording();
          setCurrentUser(null);
        }
      }
      
      return updatedUsers;
    });
  };

  const generateBotResponse = async () => {
    setIsProcessing(true);
    try {
      const processingMessage: Message = {
        id: generateId(),
        user: 'Mody',
        content: "Analyzing the conversation...",
        timestamp: new Date(),
        isBot: true,
      };
      addMessage(processingMessage);

      // Prepare chat history for the prompt
      const chatHistory = messages
        .filter(msg => !msg.isBot)
        .map(msg => `${msg.user}: ${msg.content}`)
        .join('\n');

      const response = await fetch('http://localhost:8000/combined_', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversation: chatHistory,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from server');
      }

      const data = await response.json();
      
      // Format the response array into a markdown string
      const formattedResponse = data.map((item: any) => (
        `## ${item.topic}\n\n${item.context}\n\n**Information Request:** ${item.Information_request}`
      )).join('\n\n');

      // Remove the processing message
      setMessages(prevMessages => {
        const filteredMessages = prevMessages.filter(msg => msg.id !== processingMessage.id);
        const botMessage: Message = {
          id: generateId(),
          user: 'Mody',
          content: formattedResponse,
          timestamp: new Date(),
          isBot: true,
        };
        return [...filteredMessages, botMessage];
      });
    } catch (error) {
      console.error('Error generating bot response:', error);
      const errorMessage: Message = {
        id: generateId(),
        user: 'Mody',
        content: "I apologize, but I'm having trouble analyzing the conversation right now. Please try again later.",
        timestamp: new Date(),
        isBot: true,
      };
      addMessage(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h1 className="text-2xl font-bold mb-4">Mody Chat</h1>
          
          <div className="flex space-x-4 mb-6">
            {users.map(user => (
              <button
                key={user.id}
                onClick={() => toggleUserActive(user.id)}
                disabled={isProcessing}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  user.isActive ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
                } ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {user.isActive ? <Mic size={20} /> : <MicOff size={20} />}
                <span>{user.name}</span>
              </button>
            ))}
            
            <button
              onClick={generateBotResponse}
              disabled={isProcessing || messages.length === 0}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600 transition-colors ${
                (isProcessing || messages.length === 0) ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              <Bot size={20} />
              <span>Call Mody</span>
            </button>
          </div>

          <div className="bg-gray-50 rounded-lg p-4 h-[500px] overflow-y-auto">
            {messages.length === 0 ? (
              <div className="text-center text-gray-500 mt-4">
                No messages yet. Start speaking to begin the conversation!
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map(message => (
                  <div
                    key={message.id}
                    className={`p-4 rounded-lg ${
                      message.isBot ? 'bg-blue-100' : 'bg-white border border-gray-200'
                    } ${message.content === "Analyzing the conversation..." ? 'animate-pulse' : ''}`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-semibold">{message.user}</span>
                      <span className="text-sm text-gray-500">
                        {format(message.timestamp, 'HH:mm:ss')}
                      </span>
                    </div>
                    {message.isBot ? (
                      <div className="prose prose-sm max-w-none text-gray-700">
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      </div>
                    ) : (
                      <p className="text-gray-700">{message.content}</p>
                    )}
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {listening && currentUser && (
            <div className="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
              <p className="text-sm text-green-700">
                Currently listening... {transcript}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;