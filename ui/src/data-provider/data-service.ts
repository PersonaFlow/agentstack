import request from "./requests"
import * as endpoints from "./endpoints"
import * as t from "./types"

// --Runs--
export function stream(params: t.TRunRequest): Promise<t.TRunResponse> {
    return request.post(endpoints.stream, {
        ...params
    })
}

export function run(params: t.TRunRequest): Promise<t.TRunResponse> {
    return request.post(endpoints.runs, {
        ...params
    })
}

export function getRunnableInputSchema(): Promise<void> {
    return request.get(endpoints.runnableInputSchema)
}

export function getRunnableOutputSchema(): Promise<void> {
    return request.get(endpoints.runnableOutputSchema)
}

export function getRunnableConfigSchema(): Promise<void> {
    return request.get(endpoints.runnableConfigSchema)
}

export function createTitle(): Promise<void> {
    return request.post(endpoints.title)
}

// --Users--
export function getUsers(): Promise<t.TUser[]> {
    return request.get(endpoints.users())
}

export function createUser(params: t.TUser): Promise<t.TUser> {
    return request.post(endpoints.users(), {
        ...params
    })
}

export function getUser(userId: string): Promise<t.TUser> {
    return request.get(endpoints.users(userId))
}

export function updateUser(params: t.TUser): Promise<t.TUser> {
    return request.patch(endpoints.users(params.user_id), {
        ...params
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

export function createThread(params: t.TCreateThreadRequest): Promise<t.TThread> {
    return request.post(endpoints.threads(), {
        ...params
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
export function createMessage(params: t.TMessageRequest): Promise<t.TMessage> {
    return request.post(endpoints.messages())
}

export function updateMessage(messageId: string, params: t.TUpdateMessageRequest): Promise<t.TMessage> {
    return request.patch(endpoints.messages(messageId), {
        ...params
    })
}

export function deleteMessage(messageId: string): Promise<void> {
    return request.delete(endpoints.messages(messageId))
}








