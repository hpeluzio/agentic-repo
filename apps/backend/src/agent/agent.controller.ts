import {
  Controller,
  Post,
  Get,
  Body,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { AgentService } from './agent.service';

interface QueryRequest {
  question: string;
  modelConfig?: {
    provider: string;
    model: string;
  };
}

@Controller('agent')
export class AgentController {
  constructor(private readonly agentService: AgentService) {}

  @Post('query')
  async queryDocuments(
    @Body() body: QueryRequest,
  ): Promise<{ success: boolean; response: string }> {
    try {
      const response = await this.agentService.queryDocuments(
        body.question,
        body.modelConfig,
      );
      return { success: true, response };
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      throw new HttpException(
        {
          success: false,
          message: errorMessage,
        },
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Get('models')
  async getAvailableModels(): Promise<{
    success: boolean;
    models: Record<
      string,
      { available: boolean; models: string[]; requiresApiKey: boolean }
    >;
  }> {
    try {
      const models = await this.agentService.getAvailableModels();
      return { success: true, models };
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      throw new HttpException(
        {
          success: false,
          message: errorMessage,
        },
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Post('add-document')
  async addDocument(@Body() body: { filePath: string }) {
    try {
      const response = await this.agentService.addDocument(body.filePath);
      return { success: true, message: response };
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      throw new HttpException(
        {
          success: false,
          message: errorMessage,
        },
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Get('status')
  async getStatus() {
    try {
      const status = await this.agentService.getStatus();
      return { success: true, ...status };
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      throw new HttpException(
        {
          success: false,
          message: errorMessage,
        },
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }
}
