import request from "./requests"
import * as endpoints from "./endpoints"
import * as t from "./types"

// --Runs--
export function stream(payload: t.TRunRequest): Promise<t.TRunResponse> {
    return request.post(endpoints.stream, {
        ...payload
    })
}

export function run(payload: t.TRunRequest): Promise<t.TRunResponse> {
    return request.post(endpoints.runs, {
        ...payload
    })
}

export function getRunnableInputSchema(): Promise<any> {
    return request.get(endpoints.runnableInputSchema)
}

export function getRunnableOutputSchema(): Promise<any> {
    return request.get(endpoints.runnableOutputSchema)
}

export function getRunnableConfigSchema(): Promise<void> {
    return request.get(endpoints.runnableConfigSchema)
}

export function generateTitle(payload: t.TGenerateTitle): Promise<t.TThread> {
    return request.post(endpoints.title, {
        ...payload
    })
}

// --Users--
export function getUsers(): Promise<t.TUser[]> {
    return request.get(endpoints.users())
}

export function createUser(payload: t.TUser): Promise<t.TUser> {
    return request.post(endpoints.users(), {
        ...payload
    })
}

export function getUser(userId: string): Promise<t.TUser> {
    return request.get(endpoints.users(userId))
}

export function updateUser(payload: t.TUser): Promise<t.TUser> {
    return request.patch(endpoints.users(payload.user_id), {
        ...payload
    })
}

export function deleteUser(userId: string): Promise<void> {
    return request.delete(userId)
}

export function getUserThreads(userId: string, grouped?: boolean, timezoneOffset?: number): Promise<t.TThread[]> {
    return request.get(endpoints.userThreads(userId, grouped, timezoneOffset))
}

export function getUserStartup(userId: string): Promise<t.TUser> {
    return request.get(endpoints.userStartup(userId))
}

// --Threads--
export function getThreads(): Promise<t.TThread[]> {
    return request.get(endpoints.threads())
}

export function createThread(payload: t.TCreateThreadRequest): Promise<t.TThread> {
    return request.post(endpoints.threads(), {
        ...payload
    })
}

export function getThread(threadId: string): Promise<t.TThread> {
    return request.get(endpoints.threads(threadId))
}

export function updateThread(threadId: string): Promise<t.TThread> {
    return request.patch(endpoints.threads(threadId))
}

export function deleteThread(threadId: string): Promise<void> {
    return request.delete(endpoints.threads(threadId))
}

export function getMessagesByThread(threadId: string): Promise<t.TMessage[]> {
    return request.get(endpoints.threadMessages(threadId))
}

// Confirm this
export function getMessagesByCheckpoint(threadId: string): Promise<t.TMessage[]> {
    return request.get(endpoints.threadCheckpoints(threadId))
}

// --Messages--
export function createMessage(payload: t.TMessageRequest): Promise<t.TMessage> {
    return request.post(endpoints.messages())
}

export function updateMessage(messageId: string, payload: t.TUpdateMessageRequest): Promise<t.TMessage> {
    return request.patch(endpoints.messages(messageId), {
        ...payload
    })
}

export function deleteMessage(messageId: string): Promise<void> {
    return request.delete(endpoints.messages(messageId))
}

// --Assistants
export function getAssistants(): Promise<t.TAssistant[]> {
    return request.get(endpoints.assistants())
}

export function createAssistant(payload: t.TAssistantRequest): Promise<t.TAssistant> {
    return request.post(endpoints.assistants())
}

export function getAssistant(assistantId: string): Promise<t.TAssistant> {
    return request.get(endpoints.assistants(assistantId))
}

export function updateAssistant(assistantId: string, payload: t.TAssistantRequest): Promise<t.TAssistant> {
    return request.patch(endpoints.assistants(assistantId), {
        ...payload
    })
}

export function deleteAssistant(assistantId: string): Promise<void> {
    return request.delete(endpoints.assistants(assistantId))
}

// Send fileId in url rather than in body?
export function createAssistantFile(assistantId: string, payload: t.TCreateAssistantFileRequest): Promise<t.TAssistantFile> {
    return request.post(endpoints.assistantFiles(assistantId), {
        ...payload
    })
}

// payload should be in body rather than in url?
export function getAssistantFiles(assistantId: string, limit?: number, order?: string, before?: string, after?: string ): Promise<t.TFile[]> {
    return request.get(endpoints.assistantFiles(assistantId, limit, order, before, after ))
}

export function deleteAssistantFile(assistantId: string, fileId: string): Promise<t.TAssistant> {
    return request.delete(endpoints.assistantFile(assistantId, fileId))
}

// --RAG--
export function ingestFileData(payload: t.TIngestFileDataRequest): Promise<{}> {
    return request.post(endpoints.ingest(), {
        ...payload
    })
}

export function queryData(payload: t.TQuery): Promise<t.TQueryResponse> {
    return request.post(endpoints.query(), {
        ...payload
    })
}

export function queryLCRetriever(payload: t.TQuery): Promise<string> {
    return request.post(endpoints.queryLCRetriever(), {
        ...payload
    })
}

// --Files--
export function uploadFile(payload: FormData): Promise<t.TFile> {
    return request.postMultiPart(endpoints.files(), payload)
}

export function getFiles(userId: string, purpose?: t.TPurpose): Promise<t.TFile[]> {
    return request.get(endpoints.files(userId, purpose))
}

export function getFile(fileId: string): Promise<t.TFile> {
    return request.get(endpoints.files('', fileId))
}

export function deleteFile(fileId: string): Promise<t.TDeleteFileResponse> {
    return request.delete(fileId)
}

export function getFileContent(fileId: string): Promise<File> {
    return request.get(endpoints.fileContent(fileId))
}

// --Health Check--
export function healthCheck(): Promise<string> {
    return request.get(endpoints.healthCheck())
}

