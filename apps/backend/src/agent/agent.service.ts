import { Injectable } from '@nestjs/common';
import { promisify } from 'util';
import { exec } from 'child_process';
import { join } from 'path';

const execAsync = promisify(exec);

interface ExecError extends Error {
  stdout?: string;
  stderr?: string;
}

@Injectable()
export class AgentService {
  /**
   * Query the Python LlamaIndex engine
   */
  async queryDocuments(question: string): Promise<string> {
    try {
      // Path to the Python script and virtual environment
      const scriptPath = join(process.cwd(), '../llama-bridge/query_engine.py');
      const venvPath = join(process.cwd(), '../llama-bridge/venv/bin/python');
      const workingDir = join(process.cwd(), '../llama-bridge');

      console.log('Executing Python script with:');
      console.log('Script path:', scriptPath);
      console.log('Venv path:', venvPath);
      console.log('Working dir:', workingDir);
      console.log('Question:', question);

      // Execute the Python script with the virtual environment
      const { stdout, stderr } = await execAsync(
        `${venvPath} ${scriptPath} "${question}"`,
        {
          cwd: workingDir,
          env: {
            ...process.env,
            PYTHONPATH: workingDir,
            OPENAI_API_KEY: process.env.OPENAI_API_KEY,
          },
        },
      );

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
