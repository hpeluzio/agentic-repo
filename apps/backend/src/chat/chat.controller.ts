import {
  Controller,
  Post,
  Get,
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

interface RagResponse {
  success: boolean;
  response: string;
  timestamp: string;
  sources?: Array<{
    title: string;
    category: string;
    relevance_score: number;
  }> | null;
}

@Controller('chat')
export class ChatController {
  constructor(
    private readonly chatService: ChatService,
    private readonly httpService: HttpService,
  ) {}

  @Post('database')
  async chatDatabase(
    @Body() body: { message: string; user_role: string },
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

      // 3. User role validation is now handled by LLM in the Python agent
      // No need for rigid role checking here - let the intelligent LLM decide

      // 4. Log the request
      console.log(
        `[NestJS] Database query from ${body.user_role}: ${body.message}`,
      );

      // 5. Call the Python service
      const agentResponse = (await this.chatService.sendToAgent(
        body.message,
        body.user_role,
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
      console.error('[NestJS] Database Error:', errorMessage);

      if (error instanceof HttpException) {
        throw error;
      }

      throw new HttpException(
        'Internal server error',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Post('rag')
  async chatRag(
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
      console.log(`[NestJS] RAG query: ${body.message}`);

      // 4. Call the RAG service
      const ragResponse = (await this.chatService.sendToRag(
        body.message,
      )) as RagResponse;

      // 5. Return response with the same structure as RAG service
      return {
        success: ragResponse.success,
        response: ragResponse.response,
        timestamp: ragResponse.timestamp,
        sources: ragResponse.sources || null,
      };
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      console.error('[NestJS] RAG Error:', errorMessage);

      if (error instanceof HttpException) {
        throw error;
      }

      throw new HttpException(
        'Internal server error',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Get('health')
  async healthCheck() {
    try {
      // Check if the Python service is running
      const response = await firstValueFrom(
        this.httpService.get<HealthResponse>('http://localhost:8000/health'),
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
