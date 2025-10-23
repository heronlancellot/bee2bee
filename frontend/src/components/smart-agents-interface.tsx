'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, Bot, Code, Users, DollarSign, User } from 'lucide-react';

interface SmartAgentResponse {
  response: string;
  intent: string;
  intent_confidence: number;
  agent_id: string;
  conversation_id: string;
  metadata: any;
  timestamp: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  agent_id?: string;
  intent?: string;
  timestamp: string;
}

const AGENT_ICONS = {
  repo_analyzer: Code,
  skill_matcher: Users,
  bounty_estimator: DollarSign,
  user_profile_agent: User,
  orchestrator: Bot,
};

const AGENT_COLORS = {
  repo_analyzer: 'bg-blue-100 text-blue-800',
  skill_matcher: 'bg-green-100 text-green-800',
  bounty_estimator: 'bg-yellow-100 text-yellow-800',
  user_profile_agent: 'bg-purple-100 text-purple-800',
  orchestrator: 'bg-gray-100 text-gray-800',
};

export default function SmartAgentsInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/smart-agents', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input.trim(),
          user_id: 'demo_user',
          conversation_id: conversationId || undefined,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from smart agents');
      }

      const data: SmartAgentResponse = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        agent_id: data.agent_id,
        intent: data.intent,
        timestamp: data.timestamp,
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      if (!conversationId) {
        setConversationId(data.conversation_id);
      }

    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        agent_id: 'orchestrator',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const getAgentIcon = (agentId: string) => {
    const IconComponent = AGENT_ICONS[agentId as keyof typeof AGENT_ICONS] || Bot;
    return <IconComponent className="w-4 h-4" />;
  };

  const getAgentBadgeColor = (agentId: string) => {
    return AGENT_COLORS[agentId as keyof typeof AGENT_COLORS] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">Smart Agents Interface</h1>
        <p className="text-gray-600">
          Interact with AI agents specialized in repository analysis, skill matching, bounty estimation, and user profiles.
        </p>
      </div>

      {/* Messages */}
      <Card className="h-96 overflow-y-auto">
        <CardContent className="p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              <Bot className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <p>Start a conversation with the smart agents!</p>
              <div className="mt-4 space-y-2 text-sm">
                <p><strong>Try:</strong> "Analyze this repository: https://github.com/microsoft/vscode"</p>
                <p><strong>Try:</strong> "I need a developer who knows Python and React"</p>
                <p><strong>Try:</strong> "How much should I pay for a React component?"</p>
                <p><strong>Try:</strong> "Show my profile"</p>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    message.role === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    {message.role === 'assistant' && message.agent_id && (
                      <>
                        {getAgentIcon(message.agent_id)}
                        <Badge className={getAgentBadgeColor(message.agent_id)}>
                          {message.agent_id.replace('_', ' ')}
                        </Badge>
                        {message.intent && (
                          <Badge variant="outline" className="text-xs">
                            {message.intent.replace('_', ' ')}
                          </Badge>
                        )}
                      </>
                    )}
                  </div>
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  <div className="text-xs opacity-70 mt-1">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-lg p-3 flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Processing...</span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Input */}
      <div className="flex gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask the smart agents anything..."
          disabled={isLoading}
          className="flex-1"
        />
        <Button onClick={sendMessage} disabled={isLoading || !input.trim()}>
          {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Send'}
        </Button>
      </div>

      {/* Agent Capabilities */}
      <Card>
        <CardHeader>
          <CardTitle>Available Agents</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center gap-3">
              <Code className="w-5 h-5 text-blue-600" />
              <div>
                <h3 className="font-semibold">Repository Analyzer</h3>
                <p className="text-sm text-gray-600">Analyzes GitHub repositories for code quality and health</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Users className="w-5 h-5 text-green-600" />
              <div>
                <h3 className="font-semibold">Skill Matcher</h3>
                <p className="text-sm text-gray-600">Matches developers with required skills</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <DollarSign className="w-5 h-5 text-yellow-600" />
              <div>
                <h3 className="font-semibold">Bounty Estimator</h3>
                <p className="text-sm text-gray-600">Estimates project costs and bounty values</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <User className="w-5 h-5 text-purple-600" />
              <div>
                <h3 className="font-semibold">User Profile Agent</h3>
                <p className="text-sm text-gray-600">Manages user profiles and preferences</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
