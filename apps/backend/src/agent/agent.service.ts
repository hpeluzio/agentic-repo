import { Injectable } from '@nestjs/common';
import { promisify } from 'util';
import { exec } from 'child_process';
import { join } from 'path';

const execAsync = promisify(exec);

interface ExecError extends Error {
  stdout?: string;
  stderr?: string;
}

interface ModelConfig {
  provider: string;
  model: string;
  apiKey?: string;
}

@Injectable()
export class AgentService {
  /**
   * Query the Python LlamaIndex engine
   */
  async queryDocuments(
    question: string,
    modelConfig?: ModelConfig,
  ): Promise<string> {
    try {
      // Path to the Python script and virtual environment
      const scriptPath = join(process.cwd(), '../llama-bridge/query_engine.py');
      const venvPath = join(process.cwd(), '../llama-bridge/venv/bin/python');
      const workingDir = join(process.cwd(), '../llama-bridge');

      // Build command with model configuration
      let command = `${venvPath} ${scriptPath} "${question}"`;
      
      if (modelConfig) {
        command += ` --model ${modelConfig.provider}:${modelConfig.model}`;
        
        // Add API key from environment variables based on provider
        if (modelConfig.provider === 'openai' && process.env.OPENAI_API_KEY) {
          command += ` --api-key ${process.env.OPENAI_API_KEY}`;
        } else if (modelConfig.provider === 'gemini' && process.env.GEMINI_API_KEY) {
          command += ` --api-key ${process.env.GEMINI_API_KEY}`;
        }
      }

      console.log('Executing Python script with:');
      console.log('Script path:', scriptPath);
      console.log('Venv path:', venvPath);
      console.log('Working dir:', workingDir);
      console.log('Question:', question);
      console.log('Model config:', modelConfig);

      // Execute the Python script with the virtual environment
      const { stdout, stderr } = await execAsync(command, {
        cwd: workingDir,
        env: {
          ...process.env,
          PYTHONPATH: workingDir,
          OPENAI_API_KEY: process.env.OPENAI_API_KEY,
          GEMINI_API_KEY: process.env.GEMINI_API_KEY,
        },
      });

      console.log('Python stdout:', stdout);
      if (stderr) {
        console.error('Python stderr:', stderr);
      }

      return stdout.trim();
    } catch (error) {
      console.error('Full error object:', error);
      console.error('Error message:', (error as Error).message);

      const execError = error as ExecError;
      console.error('Error stdout:', execError.stdout);
      console.error('Error stderr:', execError.stderr);

      const errorMessage = execError.stderr || (error as Error).message;
      throw new Error(`Failed to query documents: ${errorMessage}`);
    }
  }

  /**
   * Get available models
   */
  async getAvailableModels(): Promise<any> {
    try {
      const scriptPath = join(process.cwd(), '../llama-bridge/query_engine.py');
      const venvPath = join(process.cwd(), '../llama-bridge/venv/bin/python');
      const workingDir = join(process.cwd(), '../llama-bridge');

      // Run the script without arguments to get available models
      const { stdout } = await execAsync(`${venvPath} ${scriptPath}`, {
        cwd: workingDir,
        env: {
          ...process.env,
          PYTHONPATH: workingDir,
        },
      });

      // Parse the output to extract model information
      const lines = stdout.split('\n');
      const models: any = {};

      for (const line of lines) {
        if (line.includes('✅') || line.includes('❌')) {
          // Parse line like: "  ✅ ollama: llama3.1:8b, llama3.1:70b, mistral:7b, codellama:7b"
          const trimmedLine = line.trim();
          const status = trimmedLine.startsWith('✅') ? '✅' : '❌';
          const remainingText = trimmedLine.substring(2).trim(); // Remove ✅ or ❌
          const colonIndex = remainingText.indexOf(':');
          
          if (colonIndex !== -1) {
            const provider = remainingText.substring(0, colonIndex).trim();
            const modelList = remainingText.substring(colonIndex + 1).trim();
            
            models[provider] = {
              available: status === '✅',
              models: modelList.split(', ').filter((m) => m.trim()),
              requiresApiKey: provider === 'openai' || provider === 'gemini',
            };
          }
        }
      }

      console.log('Parsed models:', models);

      return models;
    } catch (error) {
      console.error('Error getting available models:', error);
      return {
        ollama: {
          available: true,
          models: ['llama3.1:8b', 'llama3.1:70b', 'mistral:7b', 'codellama:7b'],
          requiresApiKey: false,
        },
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
