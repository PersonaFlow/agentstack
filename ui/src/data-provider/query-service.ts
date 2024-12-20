import {
  Query,
  QueryObserverResult,
  QueryOptions,
  UseQueryOptions,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'
import * as dataService from './data-service'
import * as t from './types'
import { z } from 'zod'

export enum QueryKeys {
  stream = 'stream',
  run = 'run',
  inputSchema = 'inputSchema',
  outputSchema = 'outputSchema',
  configSchema = 'configSchema',
  users = 'users',
  user = 'user',
  userThreads = 'userThreads',
  userStartup = 'userStartup',
  threads = 'threads',
  createThread = 'createThread',
  thread = 'thread',
  messagesByThread = 'messagesByThread',
  messages = 'messages',
  messagesByCheckpoint = 'messagesByCheckpoint',
  assistants = 'assistants',
  assistant = 'assistant',
  assistantFiles = 'assistantFiles',
  files = 'files',
  file = 'file',
  healthCheck = 'healthCheck',
  fileContent = 'fileContent',
  conversation = 'conversation',
}

// --Runs--
export const useRun = (payload: t.TRunRequest) => {
  return useQuery<t.TRunResponse, Error>({
    queryKey: [QueryKeys.run],
    queryFn: async () => await dataService.run(payload),
  })
}

export const useRunnableInputSchema = () => {
  return useQuery<any, Error>({
    queryKey: [QueryKeys.inputSchema],
    queryFn: async () => await dataService.getRunnableInputSchema(),
  })
}

export const useRunnableOutputSchema = () => {
  return useQuery<any, Error>({
    queryKey: [QueryKeys.outputSchema],
    queryFn: async () => await dataService.getRunnableOutputSchema(),
  })
}

export const useRunnableConfigSchema = () => {
  return useQuery<t.TConfigSchema, Error>({
    queryKey: [QueryKeys.configSchema],
    queryFn: async (): Promise<t.TConfigSchema> => await dataService.getRunnableConfigSchema(),
  })
}

export const useGenerateTitle = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: t.TGenerateTitle): Promise<t.TThread> =>
      await dataService.generateTitle(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: [QueryKeys.userThreads] }),
  })
}

// --Me--
export const useGetMe = () => {
  return useQuery<t.TUser, Error>({
    queryKey: [QueryKeys.user],
    queryFn: async () => await dataService.getMe(),
  })
}

export const useUpdateMe = (payload: t.TUser) => {
  const queryClient = useQueryClient()
  return useMutation<t.TUser, Error>({
    mutationFn: async (): Promise<t.TUser> => {
      return await dataService.updateMe(payload)
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: [QueryKeys.user] }),
  })
}

export const useGetMyThreads = (grouped: boolean) => {
  return useQuery<t.TThread[] | t.TGroupedThreads, Error>({
    queryKey: [QueryKeys.userThreads],
    queryFn: async () => await dataService.getMyThreads(grouped),
  })
}

// --Admin Users--
export const useUsers = () => {
  return useQuery<t.TUser[], Error>({
    queryKey: [QueryKeys.users],
    queryFn: async () => await dataService.getUsers(),
  })
}

export const useCreateUser = (payload: t.TUser) => {
  const queryClient = useQueryClient()
  return useMutation<t.TUser, Error>({
    mutationFn: async (): Promise<t.TUser> => {
      return await dataService.createUser(payload)
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: [[QueryKeys.users]] }),
  })
}

export const useUser = (userId: string) => {
  return useQuery<t.TUser, Error>({
    queryKey: [QueryKeys.user, userId],
    queryFn: async () => await dataService.getUser(userId),
  })
}

export const useUpdateUser = (payload: t.TUser) => {
  const queryClient = useQueryClient()
  return useMutation<t.TUser, Error>({
    mutationFn: async (): Promise<t.TUser> => {
      return await dataService.updateUser(payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QueryKeys.users] })
      queryClient.invalidateQueries({ queryKey: [payload.user_id] })
    },
  })
}

export const useDeleteUser = (userId: string) => {
  const queryClient = useQueryClient()
  return useMutation<void, Error>({
    mutationFn: async (): Promise<void> => {
      return await dataService.deleteUser(userId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QueryKeys.users] })
      queryClient.invalidateQueries({ queryKey: [userId] })
    },
  })
}

export const useThreads = () => {
  return useQuery<t.TThread[], Error>({
    queryKey: [QueryKeys.threads],
    queryFn: async () => await dataService.getThreads(),
  })
}

export const useCreateThread = () => {
  const queryClient = useQueryClient()
  return useMutation<t.TThread, Error, t.TThreadRequest>({
    mutationFn: async (payload: t.TThreadRequest): Promise<t.TThread> => {
      return await dataService.createThread(payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QueryKeys.threads] })
      queryClient.invalidateQueries({ queryKey: [QueryKeys.userThreads] })
    },
  })
}

export const useThread = (threadId: string, enabled?: { enabled?: boolean }) => {
  return useQuery<t.TThread, Error>({
    queryKey: [QueryKeys.thread, threadId],
    queryFn: async () => await dataService.getThread(threadId),
    ...enabled,
  })
}

export const useUpdateThread = (threadId: string) => {
  const queryClient = useQueryClient()
  return useMutation<t.TThread, Error, t.TUpdateThread>({
    mutationFn: async (payload: t.TUpdateThread) => await dataService.updateThread(threadId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QueryKeys.threads] })
      queryClient.invalidateQueries({ queryKey: [QueryKeys.userThreads] })
      queryClient.invalidateQueries({ queryKey: [threadId] })
    },
    onSettled: async () => {
      return await Promise.all([
        queryClient.invalidateQueries({ queryKey: [QueryKeys.threads] }),
        queryClient.invalidateQueries({ queryKey: [QueryKeys.userThreads] }),
        queryClient.invalidateQueries({ queryKey: [threadId] }),
      ])
    },
  })
}

export const useDeleteThread = (threadId: string) => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async () => await dataService.deleteThread(threadId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QueryKeys.threads] })
      queryClient.invalidateQueries({ queryKey: [QueryKeys.userThreads] })
      queryClient.invalidateQueries({ queryKey: [threadId] })
    },
  })
}

export const useThreadState = (threadId: string, enabled?: { enabled?: boolean }) => {
  return useQuery<t.TThreadState, Error>({
    queryKey: [QueryKeys.conversation, threadId],
    queryFn: async (): Promise<t.TThreadState> => await dataService.getThreadState(threadId),
    ...enabled,
  })
}

// --Messages--
export const useCreateMessage = (payload: t.TMessage) => {
  return useQuery<t.TMessage, Error>({
    queryKey: [],
    queryFn: async (): Promise<t.TMessage> => await dataService.createMessage(payload),
  })
}

export const useUpdateMessage = (messageId: string, payload: t.TUpdateMessageRequest) => {
  const queryClient = useQueryClient()
  return useMutation<t.TMessage, Error>({
    mutationFn: async (): Promise<t.TMessage> => await dataService.updateMessage(messageId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QueryKeys.messages] })
      queryClient.invalidateQueries({ queryKey: [messageId] })
    },
  })
}

export const useDeleteMessage = (messageId: string) => {
  const queryClient = useQueryClient()
  return useMutation<void, Error>({
    mutationFn: async (): Promise<void> => await dataService.deleteMessage(messageId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QueryKeys.messages] })
      queryClient.invalidateQueries({ queryKey: [messageId] })
    },
  })
}

// --Assistants--
export const useAssistants = () => {
  return useQuery<t.TAssistant[], Error>({
    queryKey: [QueryKeys.assistants],
    queryFn: async (): Promise<t.TAssistant[]> => await dataService.getAssistants(),
  })
}

export const useCreateAssistant = () => {
  const queryClient = useQueryClient()
  return useMutation<t.TAssistant, Error, t.TAssistant>({
    mutationFn: async (payload: t.TAssistant): Promise<t.TAssistant> =>
      await dataService.createAssistant(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: [QueryKeys.assistants] }),
  })
}

export const useAssistant = (assistantId: string, enabled?: { enabled?: boolean }) => {
  return useQuery<t.TAssistant, Error>({
    queryKey: [QueryKeys.assistant, assistantId],
    queryFn: async (): Promise<t.TAssistant> => await dataService.getAssistant(assistantId),
    ...enabled,
  })
}

export const useUpdateAssistant = (assistantId: string) => {
  const queryClient = useQueryClient()
  return useMutation<t.TAssistant, Error, t.TAssistant>({
    mutationFn: async (payload: t.TAssistant): Promise<t.TAssistant> =>
      await dataService.updateAssistant(assistantId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QueryKeys.configSchema] })
      queryClient.invalidateQueries({ queryKey: [QueryKeys.assistants] })
      queryClient.invalidateQueries({ queryKey: [QueryKeys.assistant, assistantId] })
    },
  })
}

export const useDeleteAssistant = (assistantId: string) => {
  const queryClient = useQueryClient()
  return useMutation<void, Error>({
    mutationFn: async (): Promise<void> => await dataService.deleteAssistant(assistantId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QueryKeys.assistants] })
      queryClient.invalidateQueries({ queryKey: [assistantId] })
    },
  })
}

export const useCreateAssistantFile = (assistantId: string, payload: t.TCreateAssistantFileRequest) => {
  const queryClient = useQueryClient()
  return useMutation<t.TAssistantFile, Error>({
    mutationFn: async (): Promise<t.TAssistantFile> =>
      await dataService.createAssistantFile(assistantId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [assistantId] })
    },
  })
}

export const useAssistantFiles = (
  assistantId: string,
  limit?: number,
  order?: string,
  before?: string,
  after?: string,
) => {
  return useQuery<t.TFile[], Error>({
    queryKey: [QueryKeys.assistantFiles, assistantId],
    queryFn: async (): Promise<t.TFile[]> =>
      dataService.getAssistantFiles(assistantId, limit, order, before, after),
  })
}

export const useDeleteAssistantFile = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({
      assistantId,
      fileId,
    }: {
      assistantId: string
      fileId: string
    }): Promise<t.TAssistant> => dataService.deleteAssistantFile(assistantId, fileId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QueryKeys.assistantFiles] })
      // @ts-ignore to be able to build
      queryClient.invalidateQueries({ queryKey: [assistantId] })
      // @ts-ignore to be able to build
      queryClient.invalidateQueries({ queryKey: [fileId] })
    },
  })
}

// --RAG--

export const useIngestFileData = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: z.infer<typeof t.fileIngestSchema>): Promise<t.TFileIngest> =>
      await dataService.ingestFileData(payload),
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: [QueryKeys.assistantFiles, QueryKeys.assistant],
      }),
  })
}

export const useQueryData = (payload: t.TQuery) => {
  return useMutation<t.TQueryResponse, Error>({
    mutationFn: async (): Promise<t.TQueryResponse> => await dataService.queryData(payload),
  })
}

// --Files--
export const useUploadFile = () => {
  const queryClient = useQueryClient()
  return useMutation<t.TFile, Error, FormData>({
    //    @ts-ignore to be able to build
    mutationFn: async (payload: FormData) => await dataService.uploadFile(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QueryKeys.files] })
    },
  })
}

export const useFiles = () => {
  return useQuery<t.TFile[], Error>({
    queryKey: [QueryKeys.files],
    queryFn: async (): Promise<t.TFile[]> => await dataService.getFiles(),
  })
}

export const useFile = (fileId: string) => {
  return useQuery<t.TFile, Error>({
    queryKey: [QueryKeys.file, fileId],
    queryFn: async (): Promise<t.TFile> => await dataService.getFile(fileId),
  })
}

export const useDeleteFile = () => {
  const queryClient = useQueryClient()
  return useMutation<t.TDeleteFileResponse, Error>({
    //    @ts-ignore to be able to build
    mutationFn: async (fileId: string): Promise<t.TDeleteFileResponse> =>
      await dataService.deleteFile(fileId),
    onSuccess: () => {
      //      @ts-ignore to be able to build
      queryClient.invalidateQueries({ queryKey: [fileId] })
      queryClient.invalidateQueries({ queryKey: [QueryKeys.files] })
    },
  })
}

export const useFileContent = (fileId: string) => {
  return useQuery<File, Error>({
    queryKey: [QueryKeys.fileContent, fileId],
    queryFn: async (): Promise<File> => await dataService.getFileContent(fileId),
  })
}

// this seems a bit excessive but.. might as well
export const useHealthCheck = () => {
  return useQuery<string, Error>({
    queryKey: [QueryKeys.healthCheck],
    queryFn: async (): Promise<string> => await dataService.healthCheck(),
  })
}
