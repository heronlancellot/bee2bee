import React from 'react';
import { MainLayout } from '@/components/main-layout';
import SupremeOrchestratorInterface from '@/components/supreme-orchestrator-interface';

export default function SupremeOrchestratorPage() {
  return (
    <MainLayout>
      <div className="container mx-auto py-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Supreme Unified Orchestrator
          </h1>
          <p className="text-gray-600">
            Intelligent agent coordination with AgentVerse integration, real conversations, and AI synthesis.
          </p>
        </div>
        
        <SupremeOrchestratorInterface />
      </div>
    </MainLayout>
  );
}



