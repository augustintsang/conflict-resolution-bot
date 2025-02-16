export interface Message {
  id: string;
  user: string;
  content: string;
  timestamp: Date;
  isBot?: boolean;
}

export interface User {
  id: string;
  name: string;
  isActive: boolean;
}