import {
  Controller,
  Post,
  Body,
  Headers,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { ChatService } from './chat.service';

interface AgentResponse {
  success: boolean;
  response: string;
  timestamp: string;
  sql_info?: {
    queries_executed: Array<{
      type: string;
      description: string;
      sql_query: string | null;
    }>;
    total_execution_time: number;
    queries_count: number;
  } | null;
}

interface HealthResponse {
  status: string;
  timestamp: string;
  agent_loaded: boolean;
}

@Controller('chat')
export class ChatController {
  constructor(
    private readonly chatService: ChatService,
    private readonly httpService: HttpService,
  ) {}

  @Post()
  async chat(
    @Body() body: { message: string },
    @Headers('authorization') auth: string,
  ) {
    try {
      // 1. Validate authentication
      if (!auth || !auth.startsWith('Bearer ')) {
        throw new HttpException('Unauthorized', HttpStatus.UNAUTHORIZED);
      }

      // 2. Validate message
      if (!body.message || body.message.trim().length === 0) {
        throw new HttpException('Message is required', HttpStatus.BAD_REQUEST);
      }

      // 3. Log the request
      console.log(`[NestJS] Received message: ${body.message}`);

      // 4. Call the Python service
      const agentResponse = (await this.chatService.sendToAgent(
        body.message,
      )) as AgentResponse;

      // 5. Return response with the same structure as python-agent
      return {
        success: agentResponse.success,
        response: agentResponse.response,
        timestamp: agentResponse.timestamp,
        sql_info: agentResponse.sql_info || null,
      };
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      console.error('[NestJS] Error:', errorMessage);

      if (error instanceof HttpException) {
        throw error;
      }

      throw new HttpException(
        'Internal server error',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Post('health')
  async healthCheck() {
    try {
      // Check if the Python service is running
      const response = await firstValueFrom(
        this.httpService.get<HealthResponse>('http://python-agent:8000/health'),
      );

      return {
        status: 'healthy',
        services: {
          nestjs: 'up',
          python_agent: response.data.status || 'unknown',
        },
      };
    } catch {
      return {
        status: 'unhealthy',
        services: {
          nestjs: 'up',
          python_agent: 'down',
        },
      };
    }
  }
}
