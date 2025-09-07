import {
  Controller,
  Post,
  Body,
  Headers,
  HttpException,
  HttpStatus,
} from "@nestjs/common";
import { HttpService } from "@nestjs/axios";
import { firstValueFrom } from "rxjs";
import { ChatService } from "./chat.service";

@Controller("chat")
export class ChatController {
  constructor(
    private readonly chatService: ChatService,
    private readonly httpService: HttpService
  ) {}

  @Post()
  async chat(
    @Body() body: { message: string },
    @Headers("authorization") auth: string
  ) {
    try {
      // 1. Validar autenticação
      if (!auth || !auth.startsWith("Bearer ")) {
        throw new HttpException("Unauthorized", HttpStatus.UNAUTHORIZED);
      }

      // 2. Validar mensagem
      if (!body.message || body.message.trim().length === 0) {
        throw new HttpException("Message is required", HttpStatus.BAD_REQUEST);
      }

      // 3. Log da requisição
      console.log(`[NestJS] Received message: ${body.message}`);

      // 4. Chamar o serviço Python
      const agentResponse = await this.chatService.sendToAgent(body.message);

      // 5. Retornar resposta
      return {
        success: true,
        message: agentResponse.response,
        timestamp: new Date().toISOString(),
        source: "langgraph-agent",
      };
    } catch (error) {
      console.error("[NestJS] Error:", error.message);

      if (error instanceof HttpException) {
        throw error;
      }

      throw new HttpException(
        "Internal server error",
        HttpStatus.INTERNAL_SERVER_ERROR
      );
    }
  }

  @Post("health")
  async healthCheck() {
    try {
      // Verificar se o serviço Python está funcionando
      const response = await firstValueFrom(
        this.httpService.get("http://python-agent:8000/health")
      );

      return {
        status: "healthy",
        services: {
          nestjs: "up",
          python_agent: response.data.status,
        },
      };
    } catch (error) {
      return {
        status: "unhealthy",
        services: {
          nestjs: "up",
          python_agent: "down",
        },
      };
    }
  }
}
