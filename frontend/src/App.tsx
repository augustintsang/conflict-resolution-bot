import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff } from 'lucide-react';
import { format } from 'date-fns';
import { Message, User } from './types';
import 'regenerator-runtime/runtime';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
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

  // Holds the real-time "Objective" fetched from /generate_objective
  const [objective, setObjective] = useState<string>('');

  // Track the last chat text we used to get knowledge-base data
  const [lastChatHistory, setLastChatHistory] = useState<string>('');

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

  // Cleanup: stop listening if component unmounts
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
          // We'll let addMessage handle fetching the Objective and knowledge
          addMessage(transcribedMessage);
        }
      }

      resetTranscript();
      accumulatedTranscriptRef.current = '';
    }
  };

  /** 
   * Fetches the "Objective" from /generate_objective endpoint
   * 
   * Accepts the updated messages array as a parameter so it includes the latest message.
   */
  const fetchObjective = async (currentMessages: Message[]) => {
    try {
      // Get all non-bot messages
      const conversationMessages = currentMessages.filter(msg => !msg.isBot);
      if (conversationMessages.length === 0) {
        setObjective("No conversation yet!");
        return;
      }

      // Prepare chat history
      const chatHistory = conversationMessages
        .map(msg => `${msg.user}: ${msg.content}`)
        .join('\n');

      // Call the new "/generate_objective" endpoint
      const response = await fetch('http://localhost:8000/generate_objective', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ conversation: chatHistory }),
      });

      if (!response.ok) {
        throw new Error(`Failed to get objective from server: ${await response.text()}`);
      }

      // The endpoint returns an array of objects, e.g.:
      // [
      //   {
      //     "Objective": "Decide on a tool for the hackathon"
      //   }
      // ]
      const data = await response.json();

      if (Array.isArray(data) && data.length > 0 && data[0].Objective) {
        // Merge all objectives (in case there's more than one item) into a single string
        const objectiveText = data
          .map((item: { Objective: string }) => item.Objective)
          .join('\n');
        setObjective(objectiveText);
      } else {
        setObjective("No objective found in response.");
      }

    } catch (error) {
      console.error('Error fetching Objective:', error);
      setObjective("Error fetching objective. Please try again later.");
    }
  };

  /**
   * Adds a message to the conversation state.
   * Also triggers fetchObjective() and generateBotResponse() if it's a human (non-bot) message.
   */
  const addMessage = (message: Message) => {
    setMessages((prevMessages) => {
      const updatedMessages = [...prevMessages, message];

      if (!message.isBot) {
        fetchObjective(updatedMessages);
        generateBotResponse(updatedMessages);
      }

      return updatedMessages;
    });
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

  /**
   * Generates knowledge-base results by calling /combined_insights
   * but only if there's new conversation text we haven't analyzed yet.
   */
  const generateBotResponse = async (currentMessages: Message[]) => {
    // Build conversation text from non-bot messages
    const conversationMessages = currentMessages.filter(msg => !msg.isBot);

    if (conversationMessages.length === 0) {
      // If there's no human conversation at all, do nothing
      return;
    }

    // Join them into a single string "signature"
    const chatHistory = conversationMessages
      .map(msg => `${msg.user}: ${msg.content}`)
      .join('\n');

    // If it's the same conversation we previously analyzed, skip
    if (chatHistory === lastChatHistory) {
      return;
    }

    // Otherwise update lastChatHistory
    setLastChatHistory(chatHistory);

    // Create "Analyzing..." placeholder
    const processingMessage: Message = {
      id: generateId(),
      user: 'Mody',
      content: "Analyzing the conversation...",
      timestamp: new Date(),
      isBot: true,
    };
    setMessages(prevMessages => [...prevMessages, processingMessage]);

    try {
      const response = await fetch('http://localhost:8000/combined_insights', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ conversation: chatHistory }),
      });

      if (!response.ok) {
        throw new Error(`Failed to get response from server: ${await response.text()}`);
      }

      const data = await response.json();

      // Format knowledge results
      const knowledgeBaseMarkdown = [
        '## Knowledge Base Results',
        data.knowledge.map((item: { question: string; results: Array<{ clean_line: string; citations: string[] }> }) =>
          `### ${item.question}\n${item.results.map(result =>
            `- ${result.clean_line}${result.citations.length ? `\n  *Sources: ${result.citations.join(', ')}*` : ''}`
          ).join('\n')}`
        ).join('\n\n')
      ].join('\n');

      // Remove the "Analyzing..." placeholder, then append the knowledge base message
      setMessages(prevMessages => {
        const filteredMessages = prevMessages.filter(
          msg => msg.id !== processingMessage.id
        );

        const botMessage: Message = {
          id: generateId(),
          user: 'Mody',
          content: knowledgeBaseMarkdown,
          timestamp: new Date(),
          isBot: true,
        };

        return [...filteredMessages, botMessage];
      });
    } catch (error) {
      console.error('Error generating bot response:', error);
      // Remove the "Analyzing..." placeholder, then append an error message
      setMessages(prevMessages => {
        const filteredMessages = prevMessages.filter(
          msg => msg.id !== processingMessage.id
        );

        const errorMessage: Message = {
          id: generateId(),
          user: 'Mody',
          content: "I apologize, but I'm having trouble analyzing the conversation right now. Please try again later.",
          timestamp: new Date(),
          isBot: true,
        };

        return [...filteredMessages, errorMessage];
      });
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h1 className="text-2xl font-bold mb-4">Mody Chat</h1>
          
          {/* Objectives Panel (populated from /generate_objective) */}
          <div className="bg-blue-50 rounded-lg p-4 mb-6">
            <h2 className="text-lg font-semibold mb-3">Objectives</h2>
            <div className="prose prose-sm max-w-none text-gray-700">
              {objective ? (
                <ReactMarkdown>{objective}</ReactMarkdown>
              ) : (
                <p className="text-gray-500">No objectives yet.</p>
              )}
            </div>
          </div>

          {/* User buttons */}
          <div className="flex space-x-4 mb-6">
            {users.map(user => (
              <button
                key={user.id}
                onClick={() => toggleUserActive(user.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  user.isActive ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
                }`}
              >
                {user.isActive ? <Mic size={20} /> : <MicOff size={20} />}
                <span>{user.name}</span>
              </button>
            ))}
          </div>

          <div className="grid grid-cols-2 gap-6">
            {/* Left Panel - Human Conversations */}
            <div className="bg-gray-50 rounded-lg p-4 h-[500px] overflow-y-auto">
              <h2 className="text-lg font-semibold mb-3">Conversation</h2>
              {messages.filter(msg => !msg.isBot).length === 0 ? (
                <div className="text-center text-gray-500 mt-4">
                  No messages yet. Start speaking to begin the conversation!
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.filter(msg => !msg.isBot).map(message => (
                    <div
                      key={message.id}
                      className="p-4 rounded-lg bg-white border border-gray-200"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-semibold">{message.user}</span>
                        <span className="text-sm text-gray-500">
                          {format(message.timestamp, 'HH:mm:ss')}
                        </span>
                      </div>
                      <p className="text-gray-700">{message.content}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Right Panel - Knowledge Base Results */}
            <div className="bg-gray-50 rounded-lg p-4 h-[500px] overflow-y-auto">
              <h2 className="text-lg font-semibold mb-3">Knowledge Base Results</h2>
              <div className="space-y-4">
                {/* 
                  We now show *all* bot messages. 
                  Each new knowledge chunk is appended in chronological order.
                */}
                {messages
                  .filter(msg => msg.isBot)
                  .map((message) => (
                    <div
                      key={message.id}
                      className="p-4 rounded-lg bg-blue-100"
                    >
                      <div className="prose prose-sm max-w-none text-gray-700">
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      </div>
                    </div>
                  ))
                }
              </div>
            </div>
          </div>

          {/* Listening indicator */}
          {listening && currentUser && (
            <div className="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
              <p className="text-sm text-green-700">
                Currently listening... {transcript}
              </p>
            </div>
          )}
        </div>

        {/* Always scrolls to the bottom of messages */}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}

export default App;
