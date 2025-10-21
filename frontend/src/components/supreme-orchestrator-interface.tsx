'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Bot, User, Loader2, Brain, MessageSquare, Database, Zap } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  agent_id?: string;
  intent?: string;
  timestamp: string;
  confidence?: number;
  conversations_count?: number;
  ai_synthesis_used?: boolean;
}

interface SupremeOrchestratorResponse {
  response: string;
  intent: string;
  confidence: number;
  session_id: string;
  agent_conversations_count: number;
  agent_responses_count: number;
  database_queries_count: number;
  ai_synthesis_used: boolean;
  timestamp: string;
  agent_id: string;
  conversation_id: string;
}

const AGENT_ICONS = {
  supreme_orchestrator: Brain,
  user_profile: User,
  skill_matcher: Bot,
  bounty_estimator: Bot,
  default: Bot,
};

const AGENT_COLORS = {
  supreme_orchestrator: 'bg-purple-100 text-purple-800',
  user_profile: 'bg-blue-100 text-blue-800',
  skill_matcher: 'bg-green-100 text-green-800',
  bounty_estimator: 'bg-yellow-100 text-yellow-800',
  default: 'bg-gray-100 text-gray-800',
};

export default function SupremeOrchestratorInterface() {
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
      const response = await fetch('/api/supreme-orchestrator', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input.trim(),
          user_id: 'frontend_user',
          conversation_id: conversationId || undefined,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from Supreme Orchestrator');
      }

      const data: SupremeOrchestratorResponse = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        agent_id: data.agent_id,
        intent: data.intent,
        timestamp: data.timestamp,
        confidence: data.confidence,
        conversations_count: data.agent_conversations_count,
        ai_synthesis_used: data.ai_synthesis_used,
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
        agent_id: 'supreme_orchestrator',
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
    <div className="flex flex-col h-full max-w-4xl mx-auto">
      {/* Header */}
      <Card className="mb-4">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="w-6 h-6 text-purple-600" />
            Supreme Unified Orchestrator
            <Badge variant="secondary" className="ml-auto">
              <Zap className="w-3 h-3 mr-1" />
              AI Powered
            </Badge>
          </CardTitle>
          <div className="flex gap-2 text-sm text-gray-600">
            <Badge variant="outline" className="text-xs">
              <MessageSquare className="w-3 h-3 mr-1" />
              Real Conversations
            </Badge>
            <Badge variant="outline" className="text-xs">
              <Database className="w-3 h-3 mr-1" />
              Database Integration
            </Badge>
            <Badge variant="outline" className="text-xs">
              <Brain className="w-3 h-3 mr-1" />
              AgentVerse AI
            </Badge>
          </div>
        </CardHeader>
      </Card>

      {/* Messages */}
      <Card className="flex-1 mb-4">
        <CardContent className="p-4 h-full">
          <div className="space-y-4 h-full overflow-y-auto">
            {messages.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <Brain className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p className="text-lg font-medium">Supreme Unified Orchestrator</p>
                <p className="text-sm">Ask me anything! I'll coordinate my intelligent agents to help you.</p>
                <div className="mt-4 text-xs text-gray-400">
                  <p>🧠 Context Analysis with AgentVerse</p>
                  <p>💬 Real Agent Conversations</p>
                  <p>🎭 Agent Personalities</p>
                  <p>🗄️ Intelligent Database Interaction</p>
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.role === 'assistant' && (
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
                        {getAgentIcon(message.agent_id || 'supreme_orchestrator')}
                      </div>
                    </div>
                  )}
                  
                  <div
                    className={`max-w-[80%] rounded-lg px-4 py-2 ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{message.content}</div>
                    
                    {message.role === 'assistant' && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {message.intent && (
                          <Badge variant="outline" className="text-xs">
                            {message.intent}
                          </Badge>
                        )}
                        {message.confidence && (
                          <Badge variant="outline" className="text-xs">
                            {Math.round(message.confidence * 100)}% confidence
                          </Badge>
                        )}
                        {message.conversations_count && (
                          <Badge variant="outline" className="text-xs">
                            {message.conversations_count} conversations
                          </Badge>
                        )}
                        {message.ai_synthesis_used && (
                          <Badge variant="outline" className="text-xs text-green-600">
                            AI Synthesis
                          </Badge>
                        )}
                      </div>
                    )}
                  </div>

                  {message.role === 'user' && (
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
                        <User className="w-4 h-4 text-white" />
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
            
            {isLoading && (
              <div className="flex gap-3 justify-start">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
                    <Brain className="w-4 h-4" />
                  </div>
                </div>
                <div className="bg-gray-100 rounded-lg px-4 py-2">
                  <div className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-sm text-gray-600">
                      Supreme Orchestrator is thinking...
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Input */}
      <Card>
        <CardContent className="p-4">
          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask the Supreme Orchestrator anything..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button 
              onClick={sendMessage} 
              disabled={!input.trim() || isLoading}
              className="px-6"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                'Send'
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}



