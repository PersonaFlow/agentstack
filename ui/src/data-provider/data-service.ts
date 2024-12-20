import request from './requests'
import * as endpoints from './endpoints'
import * as t from './types'
import { z } from 'zod'

// --Runs--
export function run(payload: t.TRunRequest): Promise<t.TRunResponse> {
  return request.post(endpoints.runs, {
    ...payload,
  })
}

export function getRunnableInputSchema(): Promise<any> {
  return request.get(endpoints.runnableInputSchema)
}

export function getRunnableOutputSchema(): Promise<any> {
  return request.get(endpoints.runnableOutputSchema)
}

export function getRunnableConfigSchema(): Promise<t.TConfigSchema> {
  return request.get(endpoints.runnableConfigSchema)
}

export function generateTitle(payload: t.TGenerateTitle): Promise<t.TThread> {
  return request.post(endpoints.title, {
    ...payload,
  })
}

// -- Me --
export function getMe(): Promise<t.TUser> {
  return request.get(endpoints.me)
}

export function getMyThreads(grouped?: boolean): Promise<t.TThread[]> {
  return request.get(endpoints.myThreads(grouped))
}

export function updateMe(payload: t.TUser): Promise<t.TUser> {
  return request.patch(endpoints.me, {
    ...payload,
  })
}

// --Admin Users--
export function getUsers(): Promise<t.TUser[]> {
  return request.get(endpoints.users())
}

export function createUser(payload: t.TUser): Promise<t.TUser> {
  return request.post(endpoints.users(), {
    ...payload,
  })
}

export function getUser(userId: string): Promise<t.TUser> {
  return request.get(endpoints.users(userId))
}

export function updateUser(payload: t.TUser): Promise<t.TUser> {
  return request.patch(endpoints.users(payload.user_id), {
    ...payload,
  })
}

export function deleteUser(userId: string): Promise<void> {
  return request.delete(userId)
}

// --Threads--
export function getThreads(): Promise<t.TThread[]> {
  return request.get(endpoints.threads())
}

export function createThread(payload: t.TThreadRequest): Promise<t.TThread> {
  return request.post(endpoints.threads(), {
    ...payload,
  })
}

export function getThread(threadId: string): Promise<t.TThread> {
  return request.get(endpoints.threads(threadId))
}

export function updateThread(threadId: string, payload: t.TUpdateThread): Promise<t.TThread> {
  return request.patch(endpoints.threads(threadId), {
    ...payload,
  })
}

export function deleteThread(threadId: string) {
  return request.delete(endpoints.threads(threadId))
}

export function getThreadState(threadId: string): Promise<t.TThreadState> {
  return request.get(endpoints.threadState(threadId))
}

// --Messages--
export function createMessage(payload: t.TMessage): Promise<t.TMessage> {
  return request.post(endpoints.messages())
}

export function updateMessage(messageId: string, payload: t.TUpdateMessageRequest): Promise<t.TMessage> {
  return request.patch(endpoints.messages(messageId), {
    ...payload,
  })
}

export function deleteMessage(messageId: string): Promise<void> {
  return request.delete(endpoints.messages(messageId))
}

// --Assistants
export function getAssistants(): Promise<t.TAssistant[]> {
  return request.get(endpoints.assistants())
}

export function createAssistant(payload: t.TAssistant): Promise<t.TAssistant> {
  return request.post(endpoints.assistants(), {
    ...payload,
  })
}

export function getAssistant(assistantId: string): Promise<t.TAssistant> {
  return request.get(endpoints.assistants(assistantId))
}

export function updateAssistant(assistantId: string, payload: t.TAssistant): Promise<t.TAssistant> {
  return request.patch(endpoints.assistants(assistantId), {
    ...payload,
  })
}

export function deleteAssistant(assistantId: string): Promise<void> {
  return request.delete(endpoints.assistants(assistantId))
}

// Send fileId in url rather than in body?
export function createAssistantFile(
  assistantId: string,
  payload: t.TCreateAssistantFileRequest,
): Promise<t.TAssistantFile> {
  return request.post(endpoints.assistantFiles(assistantId), {
    ...payload,
  })
}

// payload should be in body rather than in url?
export function getAssistantFiles(
  assistantId: string,
  limit?: number,
  order?: string,
  before?: string,
  after?: string,
): Promise<t.TFile[]> {
  return request.get(endpoints.assistantFiles(assistantId, limit, order, before, after))
}

export function deleteAssistantFile(assistantId: string, fileId: string): Promise<t.TAssistant> {
  return request.delete(endpoints.assistantFile(assistantId, fileId))
}

// --RAG--
export function ingestFileData(payload: z.infer<typeof t.fileIngestSchema>): Promise<t.TFileIngest> {
  return request.post(endpoints.ingest(), {
    ...payload,
  })
}

export function queryData(payload: t.TQuery): Promise<t.TQueryResponse> {
  return request.post(endpoints.query(), {
    ...payload,
  })
}

// --Files--
export function uploadFile(payload: FormData): Promise<FormData> {
  return request.postMultiPart(endpoints.file(), payload)
}

export function getFiles(): Promise<t.TFile[]> {
  return request.get(endpoints.files)
}

export function getFile(fileId: string): Promise<t.TFile> {
  return request.get(endpoints.file('', fileId))
}

export function deleteFile(fileId: string): Promise<t.TDeleteFileResponse> {
  return request.delete(endpoints.deleteFile(fileId))
}

export function getFileContent(fileId: string): Promise<File> {
  return request.get(endpoints.fileContent(fileId))
}

// --Health Check--
export function healthCheck(): Promise<string> {
  return request.get(endpoints.healthCheck())
}
