import {
  Controller,
  Get,
  Post,
  Body,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { AgentService } from './agent.service';

@Controller('agent')
export class AgentController {
  constructor(private readonly agentService: AgentService) {}

  @Post('query')
  async queryDocuments(@Body() body: { question: string }) {
    try {
      if (!body.question) {
        throw new HttpException('Question is required', HttpStatus.BAD_REQUEST);
      }

      const response = await this.agentService.queryDocuments(body.question);
      return {
        success: true,
        response,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      throw new HttpException(
        (error as Error).message || 'Failed to query documents',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Post('add-document')
  async addDocument(@Body() body: { filePath: string }) {
    try {
      if (!body.filePath) {
        throw new HttpException('File path is required', HttpStatus.BAD_REQUEST);
      }

      const response = await this.agentService.addDocument(body.filePath);
      return {
        success: true,
        response,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      throw new HttpException(
        (error as Error).message || 'Failed to add document',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Get('status')
  async getStatus() {
    try {
      const status = await this.agentService.getStatus();
      return {
        success: true,
        ...status,
      };
    } catch (error) {
      throw new HttpException(
        (error as Error).message || 'Failed to get status',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }
}
