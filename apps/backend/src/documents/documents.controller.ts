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
import { DocumentsService } from './documents.service';

interface DocumentQueryRequest {
  question: string;
  model_configuration?: {
    provider: string;
    model: string;
    api_key?: string;
  };
}

interface DocumentQueryResponse {
  success: boolean;
  response: string;
  model_config?: {
    provider: string;
    model: string;
    api_key?: string;
  };
  timestamp: string;
}

interface DocumentLoadRequest {
  model_configuration?: {
    provider: string;
    model: string;
    api_key?: string;
  };
}

interface DocumentLoadResponse {
  success: boolean;
  message: string;
  documents_count: number;
  model_config?: {
    provider: string;
    model: string;
    api_key?: string;
  };
  timestamp: string;
}

interface DocumentStatusResponse {
  success: boolean;
  status: {
    documents_loaded: boolean;
    documents_path: string;
    current_model?: {
      provider: string;
      model: string;
      api_key?: string;
    };
    available_models: any;
  };
  timestamp: string;
}

@Controller('documents')
export class DocumentsController {
  constructor(
    private readonly documentsService: DocumentsService,
    private readonly httpService: HttpService,
  ) {}

  @Post('query')
  async queryDocuments(
    @Body() body: DocumentQueryRequest,
    @Headers('authorization') auth: string,
  ) {
    try {
      // 1. Validate authentication
      if (!auth || !auth.startsWith('Bearer ')) {
        throw new HttpException('Unauthorized', HttpStatus.UNAUTHORIZED);
      }

      // 2. Validate question
      if (!body.question || body.question.trim().length === 0) {
        throw new HttpException('Question is required', HttpStatus.BAD_REQUEST);
      }

      // 3. Log the request
      console.log(`[NestJS] Received document query: ${body.question}`);

      // 4. Call the Python document service
      const documentResponse = (await this.documentsService.queryDocuments(
        body.question,
        body.model_configuration,
      )) as DocumentQueryResponse;

      // 5. Return response with the same structure as python-agent
      return {
        success: documentResponse.success,
        response: documentResponse.response,
        model_config: documentResponse.model_config || null,
        timestamp: documentResponse.timestamp,
      };
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      console.error('[NestJS] Document query error:', errorMessage);

      if (error instanceof HttpException) {
        throw error;
      }

      throw new HttpException(
        'Internal server error',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Post('load')
  async loadDocuments(
    @Body() body: DocumentLoadRequest,
    @Headers('authorization') auth: string,
  ) {
    try {
      // 1. Validate authentication
      if (!auth || !auth.startsWith('Bearer ')) {
        throw new HttpException('Unauthorized', HttpStatus.UNAUTHORIZED);
      }

      // 2. Log the request
      console.log('[NestJS] Loading documents...');

      // 3. Call the Python document service
      const documentResponse = (await this.documentsService.loadDocuments(
        body.model_configuration,
      )) as DocumentLoadResponse;

      // 4. Return response
      return {
        success: documentResponse.success,
        message: documentResponse.message,
        documents_count: documentResponse.documents_count,
        model_config: documentResponse.model_config || null,
        timestamp: documentResponse.timestamp,
      };
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      console.error('[NestJS] Document load error:', errorMessage);

      if (error instanceof HttpException) {
        throw error;
      }

      throw new HttpException(
        'Internal server error',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Get('status')
  async getDocumentStatus(@Headers('authorization') auth: string) {
    try {
      // 1. Validate authentication
      if (!auth || !auth.startsWith('Bearer ')) {
        throw new HttpException('Unauthorized', HttpStatus.UNAUTHORIZED);
      }

      // 2. Call the Python document service
      const documentResponse =
        (await this.documentsService.getDocumentStatus()) as DocumentStatusResponse;

      // 3. Return response
      return {
        success: documentResponse.success,
        status: documentResponse.status,
        timestamp: documentResponse.timestamp,
      };
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      console.error('[NestJS] Document status error:', errorMessage);

      if (error instanceof HttpException) {
        throw error;
      }

      throw new HttpException(
        'Internal server error',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Get('models')
  async getAvailableModels(@Headers('authorization') auth: string) {
    try {
      // 1. Validate authentication
      if (!auth || !auth.startsWith('Bearer ')) {
        throw new HttpException('Unauthorized', HttpStatus.UNAUTHORIZED);
      }

      // 2. Call the Python document service
      const documentResponse = await this.documentsService.getAvailableModels();

      // 3. Return response
      return documentResponse;
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      console.error('[NestJS] Document models error:', errorMessage);

      if (error instanceof HttpException) {
        throw error;
      }

      throw new HttpException(
        'Internal server error',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }
}
