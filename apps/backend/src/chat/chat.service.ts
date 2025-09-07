import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';

@Injectable()
export class ChatService {
  private readonly AGENT_URL =
    process.env.AGENT_URL || 'http://localhost:8000/chat';
  private readonly AGENT_HEALTH_URL =
    process.env.AGENT_HEALTH_URL || 'http://localhost:8000/health';

  constructor(private readonly httpService: HttpService) {}

  async sendToAgent(message: string): Promise<any> {
    try {
      console.log(`[ChatService] Routing message to python-agent: ${message}`);

      // Route all messages to python-agent (LangGraph agent with database tools)
      const response = await firstValueFrom(
        this.httpService.post(
          this.AGENT_URL,
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
