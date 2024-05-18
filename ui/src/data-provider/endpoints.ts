const formatParam = (param?: string) => param ? param : ""

// --Runs--
const stream = "/api/v1/runs/stream"
const runs = "/api/v1/runs"
const inputSchema = "/api/v1/runs/input_schema"
const outputSchema = "/api/v1/runs/output_schema"
const configSchema = "/api/v1/runs/config_schema"
const title = "/api/v1/runs/title"

// --Users--
const users = (userId?: string) => `/api/v1/users/${formatParam(userId)}`
const userThreads = (userId: string) => `/api/v1/users/${userId}/threads`
const userStartup = (userId: string) => `/api/v1/users/${userId}/startup`

// --Threads--
const threads = (threadId?: string) => `/api/v1/threads/${formatParam(threadId)}`
const threadMessages = (threadId: string) => `/api/v1/threads/${threadId}/messages`
const threadCheckpoints = (threadId: string) => `/api/v1/threads/${threadId}/checkpoints`

// --Messages--
const messages = (messageId?: string) => `/api/v1/messages/${formatParam(messageId)}`

// --Assistants--
const assistants = (assistantId?: string) => `/api/v1/assistants/${formatParam(assistantId)}`
const assistantFiles = (assistantId: string, fileId?: string) => `/api/v1/assistants/${assistantId}/files/${formatParam(fileId)}`

// --RAG--
const ingest = () => "/api/v1/rag/ingest"
const query = () => "/api/v1/rag/query"
const queryLCRetriever = () => "/api/v1/rag/query-lc-retriever"

// --Files--
const files = (fileId?: string) => `/api/v1/files/${formatParam(fileId)}`
const fileContent = (fileId: string) => `/api/v1/files/${fileId}/content`

// --Health Check--
const healthCheck = () => "/api/v1/health_check"







