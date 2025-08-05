import { Injectable } from '@nestjs/common';
import { spawn } from 'child_process';
import { promisify } from 'util';
import { exec } from 'child_process';

const execAsync = promisify(exec);

@Injectable()
export class AgentService {
  /**
   * Query the Python LlamaIndex engine
   */
  async queryDocuments(question: string): Promise<string> {
    try {
      // Path to the Python script
      const scriptPath = '../llama-bridge/query_engine.py';
      
      // Execute the Python script with the question
      const { stdout, stderr } = await execAsync(`python3 ${scriptPath} "${question}"`, {
        cwd: process.cwd(),
        env: {
          ...process.env,
          PYTHONPATH: '../llama-bridge'
        }
      });

      if (stderr) {
        console.error('Python script stderr:', stderr);
      }

      return stdout.trim();
    } catch (error) {
      console.error('Error executing Python script:', error);
      throw new Error(`Failed to query documents: ${error.message}`);
    }
  }

  /**
   * Add a document to the index
   */
  async addDocument(filePath: string): Promise<string> {
    try {
      // This would need to be implemented based on your file upload strategy
      // For now, we'll return a placeholder
      return `Document ${filePath} added successfully`;
    } catch (error) {
      console.error('Error adding document:', error);
      throw new Error(`Failed to add document: ${error.message}`);
    }
  }

  /**
   * Get system status
   */
  async getStatus(): Promise<{ status: string; timestamp: string }> {
    return {
      status: 'running',
      timestamp: new Date().toISOString()
    };
  }
}
