import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';

@Injectable()
export class DocumentsService {
  private readonly DOCUMENT_QUERY_URL =
    process.env.DOCUMENT_QUERY_URL || 'http://localhost:8000/documents/query';
  private readonly DOCUMENT_LOAD_URL =
    process.env.DOCUMENT_LOAD_URL || 'http://localhost:8000/documents/load';
  private readonly DOCUMENT_STATUS_URL =
    process.env.DOCUMENT_STATUS_URL || 'http://localhost:8000/documents/status';
  private readonly DOCUMENT_MODELS_URL =
    process.env.DOCUMENT_MODELS_URL || 'http://localhost:8000/documents/models';

  constructor(private readonly httpService: HttpService) {}

  async queryDocuments(question: string, modelConfig?: any): Promise<any> {
    try {
      console.log(`[DocumentsService] Querying documents: ${question}`);

      const response = await firstValueFrom(
        this.httpService.post(
          this.DOCUMENT_QUERY_URL,
          {
            question: question,
            model_config: modelConfig,
          },
          {
            timeout: 30000, // 30 seconds timeout
            headers: {
              'Content-Type': 'application/json',
            },
          },
        ),
      );

      console.log(`[DocumentsService] Document query response received`);
      return response.data;
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      console.error(
        '[DocumentsService] Error querying documents:',
        errorMessage,
      );

      if (error && typeof error === 'object' && 'code' in error) {
        if (error.code === 'ECONNREFUSED') {
          throw new HttpException(
            'Document service is unavailable',
            HttpStatus.SERVICE_UNAVAILABLE,
          );
        }

        if (error.code === 'ECONNABORTED') {
          throw new HttpException(
            'Document service timeout',
            HttpStatus.REQUEST_TIMEOUT,
          );
        }
      }

      throw new HttpException(
        'Failed to communicate with document service',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  async loadDocuments(modelConfig?: any): Promise<any> {
    try {
      console.log(`[DocumentsService] Loading documents...`);

      const response = await firstValueFrom(
        this.httpService.post(
          this.DOCUMENT_LOAD_URL,
          {
            model_config: modelConfig,
          },
          {
            timeout: 30000, // 30 seconds timeout
            headers: {
              'Content-Type': 'application/json',
            },
          },
        ),
      );

      console.log(`[DocumentsService] Document load response received`);
      return response.data;
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      console.error(
        '[DocumentsService] Error loading documents:',
        errorMessage,
      );

      if (error && typeof error === 'object' && 'code' in error) {
        if (error.code === 'ECONNREFUSED') {
          throw new HttpException(
            'Document service is unavailable',
            HttpStatus.SERVICE_UNAVAILABLE,
          );
        }

        if (error.code === 'ECONNABORTED') {
          throw new HttpException(
            'Document service timeout',
            HttpStatus.REQUEST_TIMEOUT,
          );
        }
      }

      throw new HttpException(
        'Failed to communicate with document service',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  async getDocumentStatus(): Promise<any> {
    try {
      const response = await firstValueFrom(
        this.httpService.get(this.DOCUMENT_STATUS_URL),
      );
      return response.data;
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      return {
        success: false,
        status: {
          documents_loaded: false,
          documents_path: '',
          available_models: {},
        },
        error: errorMessage,
      };
    }
  }

  async getAvailableModels(): Promise<any> {
    try {
      const response = await firstValueFrom(
        this.httpService.get(this.DOCUMENT_MODELS_URL),
      );
      return response.data;
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      return {
        success: false,
        models: {},
        error: errorMessage,
      };
    }
  }
}
