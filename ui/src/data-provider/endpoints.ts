const formatParam = (param?: any) => (param ? param : "");

// --Runs--
export const stream = "/api/v1/runs/stream";
export const runs = "/api/v1/runs";
export const runnableInputSchema = "/api/v1/runs/input_schema";
export const runnableOutputSchema = "/api/v1/runs/output_schema";
export const runnableConfigSchema = "/api/v1/runs/config_schema";
export const title = "/api/v1/runs/title";

// --Users--
export const users = (userId?: string) =>
  `/api/v1/users/${formatParam(userId)}`;
export const userThreads = (
  userId: string,
  grouped?: boolean,
  timezoneOffset?: number,
) =>
  `/api/v1/users/${userId}/threads/${formatParam(grouped) / formatParam(timezoneOffset)}`;
export const userStartup = (userId: string) =>
  `/api/v1/users/${userId}/startup`;

// --Threads--
export const threads = (threadId?: string) =>
  `/api/v1/threads/${formatParam(threadId)}`;
export const threadMessages = (threadId: string) =>
  `/api/v1/threads/${threadId}/messages`;
export const threadCheckpoints = (threadId: string) =>
  `/api/v1/threads/${threadId}/checkpoints`;

// --Messages--
export const messages = (messageId?: string) =>
  `/api/v1/messages/${formatParam(messageId)}`;

// --Assistants--
export const assistants = (assistantId?: string) =>
  `/api/v1/assistants/${formatParam(assistantId)}`;
export const assistantFiles = (
  assistantId: string,
  limit?: number,
  order?: string,
  before?: string,
  after?: string,
) =>
  `/api/v1/assistants/${assistantId}/files/${formatParam(limit)}/${formatParam(order)}/${formatParam(before)}/${formatParam(after)}`;
export const assistantFile = (assistantId: string, fileId?: string) =>
  `/api/v1/assistants/${assistantId}/files/${formatParam(fileId)}`;

// --RAG--
export const ingest = () => "/api/v1/rag/ingest";
export const query = () => "/api/v1/rag/query";
export const queryLCRetriever = () => "/api/v1/rag/query-lc-retriever";

// --Files--
export const files = (fileId?: string, userId?: string, purpose?: string) =>
  `/api/v1/files/${formatParam(fileId)}`;
export const fileContent = (fileId: string) =>
  `/api/v1/files/${fileId}/content`;

// --Health Check--
export const healthCheck = () => "/api/v1/health_check";