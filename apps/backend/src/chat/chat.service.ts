import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';

interface UploadedFile {
  originalname?: string;
  mimetype?: string;
  size?: number;
  buffer?: Buffer;
}

@Injectable()
export class ChatService {
  private readonly AGENT_URL =
    process.env.AGENT_URL || 'http://localhost:8000/chat';
  private readonly AGENT_HEALTH_URL =
    process.env.AGENT_HEALTH_URL || 'http://localhost:8000/health';
  private readonly RAG_URL = process.env.RAG_URL || 'http://localhost:8000/rag';

  constructor(private readonly httpService: HttpService) {}

  async sendToAgent(message: string, userRole?: string): Promise<any> {
    try {
      console.log(
        `[ChatService] Routing message to python-agent: ${message} (Role: ${userRole})`,
      );

      // Route all messages to python-agent (LangGraph agent with database tools)
      const response = await firstValueFrom(
        this.httpService.post(
          this.AGENT_URL,
          {
            message: message,
            user_role: userRole,
            timestamp: new Date().toISOString(),
          },
          {
            timeout: 30000, // 30 seconds timeout
            headers: {
              'Content-Type': 'application/json',
            },
          },
        ),
      );

      console.log(`[ChatService] Agent response received`);
      return response.data;
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      console.error('[ChatService] Error calling agent:', errorMessage);

      if (error && typeof error === 'object' && 'code' in error) {
        if (error.code === 'ECONNREFUSED') {
          throw new HttpException(
            'Agent service is unavailable',
            HttpStatus.SERVICE_UNAVAILABLE,
          );
        }

        if (error.code === 'ECONNABORTED') {
          throw new HttpException(
            'Agent service timeout',
            HttpStatus.REQUEST_TIMEOUT,
          );
        }
      }

      throw new HttpException(
        'Failed to communicate with agent',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  async sendToRag(message: string): Promise<any> {
    try {
      console.log(
        `[ChatService] Routing RAG query to python-agent: ${message}`,
      );

      // Route RAG queries to python-agent RAG endpoint
      const response = await firstValueFrom(
        this.httpService.post(
          this.RAG_URL,
          {
            message: message,
            timestamp: new Date().toISOString(),
          },
          {
            timeout: 30000, // 30 seconds timeout
            headers: {
              'Content-Type': 'application/json',
            },
          },
        ),
      );

      console.log(`[ChatService] RAG response received`);
      return response.data;
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      console.error('[ChatService] Error calling RAG agent:', errorMessage);

      if (error && typeof error === 'object' && 'code' in error) {
        if (error.code === 'ECONNREFUSED') {
          throw new HttpException(
            'RAG service is unavailable',
            HttpStatus.SERVICE_UNAVAILABLE,
          );
        }

        if (error.code === 'ECONNABORTED') {
          throw new HttpException(
            'RAG service timeout',
            HttpStatus.REQUEST_TIMEOUT,
          );
        }
      }

      throw new HttpException(
        'Failed to communicate with RAG agent',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  async sendToSmartAgent(message: string, userRole?: string): Promise<any> {
    try {
      console.log(
        `[ChatService] Routing message to smart-agent: ${message} (Role: ${userRole})`,
      );

      // Route all messages to smart-agent (LLM router)
      const response = await firstValueFrom(
        this.httpService.post(
          'http://localhost:8000/smart',
          {
            message: message,
            user_role: userRole,
            timestamp: new Date().toISOString(),
          },
          {
            timeout: 30000, // 30 seconds timeout
            headers: {
              'Content-Type': 'application/json',
            },
          },
        ),
      );

      console.log(`[ChatService] Smart agent response received`);
      return response.data;
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      console.error('[ChatService] Error calling smart agent:', errorMessage);

      if (error && typeof error === 'object' && 'code' in error) {
        if (error.code === 'ECONNREFUSED') {
          throw new HttpException(
            'Smart agent service is unavailable',
            HttpStatus.SERVICE_UNAVAILABLE,
          );
        }

        if (error.code === 'ECONNABORTED') {
          throw new HttpException(
            'Smart agent service timeout',
            HttpStatus.REQUEST_TIMEOUT,
          );
        }
      }

      throw new HttpException(
        'Failed to communicate with smart agent',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  async sendToOCRAgent(file: UploadedFile): Promise<any> {
    try {
      const fileName = file.originalname || 'unknown';
      console.log(`[ChatService] Sending file to OCR agent: ${fileName}`);

      const fileDetails = {
        originalname: file.originalname,
        mimetype: file.mimetype,
        size: file.size,
        bufferLength: file.buffer?.length,
      };
      console.log(`[ChatService] File details:`, fileDetails);

      // Create FormData for file upload
      const formData = new FormData();

      // Ensure we have a proper buffer
      if (!file.buffer || file.buffer.length === 0) {
        throw new Error('File buffer is empty or invalid');
      }

      formData.append(
        'file',
        new Blob([file.buffer as unknown as ArrayBuffer], {
          type: file.mimetype || 'application/octet-stream',
        }),
        fileName,
      );

      // Call FastAPI OCR endpoint
      const response = await firstValueFrom(
        this.httpService.post('http://localhost:8000/ocr', formData, {
          timeout: 120000, // 2 minutes timeout for file processing
          // Don't set Content-Type manually - let the HTTP client handle it with proper boundary
        }),
      );

      console.log(`[ChatService] OCR response received`);
      return response.data;
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      console.error('[ChatService] Error calling OCR agent:', errorMessage);

      if (error && typeof error === 'object' && 'code' in error) {
        if (error.code === 'ECONNREFUSED') {
          throw new HttpException(
            'OCR service is unavailable',
            HttpStatus.SERVICE_UNAVAILABLE,
          );
        }

        if (error.code === 'ECONNABORTED') {
          throw new HttpException(
            'OCR service timeout',
            HttpStatus.REQUEST_TIMEOUT,
          );
        }
      }

      throw new HttpException(
        'Failed to communicate with OCR agent',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  async getAgentStatus(): Promise<any> {
    try {
      const response = await firstValueFrom(
        this.httpService.get(this.AGENT_HEALTH_URL),
      );
      return response.data;
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      return { status: 'down', error: errorMessage };
    }
  }
}
