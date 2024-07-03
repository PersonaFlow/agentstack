const formatParam = (param?: any) => (param ? param : "");

const BASE_PATH = "/api/v1";

// --Runs--
export const runs = `${BASE_PATH}/runs`;
export const runnableInputSchema = `${BASE_PATH}/runs/input_schema`;
export const runnableOutputSchema = `${BASE_PATH}/runs/output_schema`;
export const runnableConfigSchema = `${BASE_PATH}/runs/config_schema`;
export const title = `${BASE_PATH}/runs/title`;

// -- Me --
export const me = `${BASE_PATH}/users/me`;

export const myThreads = `${BASE_PATH}/users//me/threads`;


// --Admin Users--
export const users = (userId?: string) =>
  `${BASE_PATH}/admin/users/${formatParam(userId)}`;

export const userThreads = (userId: string, grouped?: boolean) => {
  const timezoneOffset = new Date().getTimezoneOffset();
  return `${BASE_PATH}/admin/users/${userId}/threads?grouped=${grouped}&timezoneOffset=${timezoneOffset}`;
};

// --Threads--
export const threads = (threadId?: string) =>
  `${BASE_PATH}/threads/${formatParam(threadId)}`;

export const threadState = (threadId: string) =>
  `${BASE_PATH}/threads/${threadId}/state`;

// --Messages--
export const messages = (messageId?: string) =>
  `${BASE_PATH}/messages/${formatParam(messageId)}`;

// --Assistants--
export const assistants = (assistantId?: string) =>
  `${BASE_PATH}/assistants/${formatParam(assistantId)}`;

export const assistantFiles = (
  assistantId: string,
  limit?: number,
  order?: string,
  before?: string,
  after?: string,
) =>
  `${BASE_PATH}/assistants/${assistantId}/files/${formatParam(limit)}/${formatParam(order)}/${formatParam(before)}/${formatParam(after)}`;
export const assistantFile = (assistantId: string, fileId?: string) =>
  `${BASE_PATH}/assistants/${assistantId}/files/${formatParam(fileId)}`;

// --RAG--
export const ingest = () => `${BASE_PATH}/rag/ingest`;
export const query = () => `${BASE_PATH}/rag/query`;

// --Files--
export const files = (purpose?: string) =>
  `${BASE_PATH}/files`;

export const file = (fileId?: string, purpose?: string) =>
  `${BASE_PATH}/files/${formatParam(fileId)}`;

export const fileContent = (fileId: string) =>
  `${BASE_PATH}/files/${fileId}/content`;

export const deleteFile = (fileId: string) => `${BASE_PATH}files/${fileId}`;

// --Health Check--
export const healthCheck = () => `${BASE_PATH}/health_check`;
