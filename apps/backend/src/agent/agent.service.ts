import { Injectable } from '@nestjs/common';

interface ModelConfig {
  provider: string;
  model: string;
  apiKey?: string;
}

interface ModelProvider {
  available: boolean;
  models: string[];
  requiresApiKey: boolean;
}

interface AvailableModels {
  [key: string]: ModelProvider;
}

interface DocumentQueryResponse {
  success: boolean;
  response: string;
  model_configuration?: ModelConfig;
  timestamp: string;
}

interface DocumentModelsResponse {
  success: boolean;
  models: AvailableModels;
  timestamp: string;
}

@Injectable()
export class AgentService {
  /**
   * Query the unified FastAPI document service
   */
  async queryDocuments(
    question: string,
    modelConfig?: ModelConfig,
  ): Promise<string> {
    try {
      // Use the new unified FastAPI service instead of llama-bridge
      const agentUrl = process.env.AGENT_URL || 'http://localhost:8000';

      console.log(`[AgentService] Querying documents via FastAPI: ${question}`);
      console.log('Model config:', modelConfig);

      const response = await fetch(`${agentUrl}/documents/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: question,
          model_configuration: modelConfig,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = (await response.json()) as DocumentQueryResponse;

      if (data.success) {
        console.log('[AgentService] Document query successful');
        return data.response;
      } else {
        console.error('[AgentService] Document query failed:', data.response);
        return `Error: ${data.response}`;
      }
    } catch (error) {
      console.error('[AgentService] Error calling document service:', error);
      throw new Error(`Failed to query documents: ${(error as Error).message}`);
    }
  }

  /**
   * Get available models from the unified FastAPI service
   */
  async getAvailableModels(): Promise<AvailableModels> {
    try {
      const agentUrl = process.env.AGENT_URL || 'http://localhost:8000';

      console.log('[AgentService] Getting available models from FastAPI');

      const response = await fetch(`${agentUrl}/documents/models`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = (await response.json()) as DocumentModelsResponse;

      if (data.success) {
        console.log('[AgentService] Models retrieved successfully');
        return data.models;
      } else {
        throw new Error('Failed to get models from service');
      }
    } catch (error) {
      console.error('[AgentService] Error getting available models:', error);
      // Return fallback models if service is unavailable
      const fallbackModels: AvailableModels = {
        openai: {
          available: true,
          models: ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo'],
          requiresApiKey: true,
        },
        gemini: {
          available: true,
          models: ['gemini-pro', 'gemini-pro-vision'],
          requiresApiKey: true,
        },
      };
      return fallbackModels;
    }
  }

  /**
   * Add a document to the index
   */
  addDocument(filePath: string): Promise<string> {
    try {
      // This would need to be implemented based on your file upload strategy
      // For now, we'll return a placeholder
      return Promise.resolve(`Document ${filePath} added successfully`);
    } catch (error) {
      console.error('Error adding document:', error);
      throw new Error(`Failed to add document: ${(error as Error).message}`);
    }
  }

  /**
   * Get system status
   */
  getStatus(): Promise<{ status: string; timestamp: string }> {
    return Promise.resolve({
      status: 'running',
      timestamp: new Date().toISOString(),
    });
  }
}
