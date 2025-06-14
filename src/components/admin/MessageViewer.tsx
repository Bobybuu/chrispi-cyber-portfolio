
import { useState } from "react";
import { Card } from "../ui/card";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { Mail, Clock, User, Trash2, Reply } from "lucide-react";

interface Message {
  id: string;
  name: string;
  email: string;
  message: string;
  timestamp: Date;
  status: 'unread' | 'read' | 'replied';
}

const MessageViewer = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      name: "John Doe",
      email: "john@example.com",
      message: "Hi Chrispin, I'm interested in discussing a DevOps consulting opportunity for our startup. We're looking to implement CI/CD pipelines and improve our deployment process. Would you be available for a call this week?",
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
      status: "unread"
    },
    {
      id: "2",
      name: "Sarah Chen",
      email: "sarah.chen@techcorp.com",
      message: "Hello! I saw your portfolio and I'm impressed with your infrastructure automation work. We have a project involving Kubernetes migration that we'd like to discuss. Can we schedule a meeting?",
      timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000), // 5 hours ago
      status: "read"
    },
    {
      id: "3",
      name: "Michael Rodriguez",
      email: "m.rodriguez@innovate.io",
      message: "Great work on the microservices architecture project! We're looking for similar solutions for our platform. Would love to chat about potential collaboration opportunities.",
      timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1 day ago
      status: "replied"
    }
  ]);

  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'unread': return 'bg-red-500/20 text-red-400 border-red-400/30';
      case 'read': return 'bg-yellow-500/20 text-yellow-400 border-yellow-400/30';
      case 'replied': return 'bg-green-500/20 text-green-400 border-green-400/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-400/30';
    }
  };

  const formatTimestamp = (date: Date) => {
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours} hours ago`;
    return `${Math.floor(diffInHours / 24)} days ago`;
  };

  const handleMarkAsRead = (id: string) => {
    setMessages(prev => prev.map(msg => 
      msg.id === id ? { ...msg, status: 'read' as const } : msg
    ));
  };

  const handleMarkAsReplied = (id: string) => {
    setMessages(prev => prev.map(msg => 
      msg.id === id ? { ...msg, status: 'replied' as const } : msg
    ));
  };

  const handleDeleteMessage = (id: string) => {
    setMessages(prev => prev.filter(msg => msg.id !== id));
    if (selectedMessage?.id === id) {
      setSelectedMessage(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">Contact Messages</h2>
        <div className="flex space-x-4">
          <div className="flex items-center space-x-2">
            <Badge className="bg-red-500/20 text-red-400 border-red-400/30">
              Unread: {messages.filter(m => m.status === 'unread').length}
            </Badge>
            <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-400/30">
              Read: {messages.filter(m => m.status === 'read').length}
            </Badge>
            <Badge className="bg-green-500/20 text-green-400 border-green-400/30">
              Replied: {messages.filter(m => m.status === 'replied').length}
            </Badge>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Messages List */}
        <div className="space-y-4">
          {messages.length === 0 ? (
            <Card className="p-8 bg-white/5 border-white/10 text-center">
              <Mail className="w-16 h-16 text-white/30 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-white/70 mb-2">No Messages</h3>
              <p className="text-white/50">Contact messages will appear here</p>
            </Card>
          ) : (
            messages.map((message) => (
              <Card
                key={message.id}
                className={`p-4 bg-white/5 border-white/10 cursor-pointer transition-all hover:bg-white/10 ${
                  selectedMessage?.id === message.id ? 'ring-2 ring-cyan-400/50' : ''
                }`}
                onClick={() => {
                  setSelectedMessage(message);
                  if (message.status === 'unread') {
                    handleMarkAsRead(message.id);
                  }
                }}
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-full flex items-center justify-center border border-cyan-400/30">
                      <User className="w-5 h-5 text-cyan-400" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-white">{message.name}</h4>
                      <p className="text-sm text-white/60">{message.email}</p>
                    </div>
                  </div>
                  <Badge className={getStatusColor(message.status)}>{message.status}</Badge>
                </div>
                
                <p className="text-white/70 text-sm mb-2 line-clamp-2">{message.message}</p>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-1 text-white/50 text-xs">
                    <Clock className="w-3 h-3" />
                    <span>{formatTimestamp(message.timestamp)}</span>
                  </div>
                  <div className="flex space-x-1">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteMessage(message.id);
                      }}
                      className="border-red-500/50 text-red-400 hover:bg-red-500/10 h-6 w-6 p-0"
                    >
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>

        {/* Message Detail */}
        <div>
          {selectedMessage ? (
            <Card className="p-6 bg-white/5 border-white/10 h-fit">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-1">{selectedMessage.name}</h3>
                  <p className="text-white/60">{selectedMessage.email}</p>
                  <p className="text-white/50 text-sm">{formatTimestamp(selectedMessage.timestamp)}</p>
                </div>
                <Badge className={getStatusColor(selectedMessage.status)}>{selectedMessage.status}</Badge>
              </div>

              <div className="mb-6">
                <h4 className="text-white/80 font-medium mb-2">Message:</h4>
                <p className="text-white/70 leading-relaxed">{selectedMessage.message}</p>
              </div>

              <div className="flex space-x-3">
                {selectedMessage.status !== 'replied' && (
                  <Button
                    onClick={() => handleMarkAsReplied(selectedMessage.id)}
                    className="bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-cyan-400/50 text-white hover:from-cyan-500/30 hover:to-purple-500/30"
                  >
                    <Reply className="w-4 h-4 mr-2" />
                    Mark as Replied
                  </Button>
                )}
                <Button
                  variant="outline"
                  onClick={() => handleDeleteMessage(selectedMessage.id)}
                  className="border-red-500/50 text-red-400 hover:bg-red-500/10"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete
                </Button>
              </div>
            </Card>
          ) : (
            <Card className="p-8 bg-white/5 border-white/10 text-center h-fit">
              <Mail className="w-16 h-16 text-white/30 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-white/70 mb-2">Select a Message</h3>
              <p className="text-white/50">Choose a message from the list to view details</p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageViewer;
