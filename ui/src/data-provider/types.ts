import { z } from "zod";

export const toolSchema = z.object({
  title: z.string(),
  properties: z.object({
    type: z.string(),
    name: z.string(),
    description: z.string(),
    multi_use: z.boolean(),
    config: z.object({}),
  }),
});

export const formSchema = z.object({
  public: z.boolean(),
  name: z.string().min(1, { message: "Name is required" }),
  config: z.object({
    configurable: z.object({
      interrupt_before_action: z.boolean(),
      type: z.string().nullable(),
      agent_type: z.string().optional(),
      llm_type: z.string(),
      retrieval_description: z.string().optional(),
      system_message: z.string(),
      tools: z.array(z.any()),
    }),
  }),
  file_ids: z.array(z.string()),
});

export type TRunInput = {
  content: string;
  role: string;
  additional_kwargs?: {};
  example: boolean;
};

export enum MessageType {
  AI = "ai",
  HUMAN = "human",
}

export type TConfigurable = {
  type: string | null;
  agent_type?: string | null;
  interrupt_before_action: boolean;
  retrieval_description: string;
  system_message: string;
  tools: string[];
  llm_type: string;
};

export type TConfigType = {
  enum: string[];
};

export type TStreamState = {
  status: "inflight" | "error" | "done";
  messages?: TMessage[] | Record<string, any>;
  run_id?: string;
};

export type TSchemaField = {
  type: string;
  title: string;
  description: string;
  enum?: string[];
  default?: string;
};

export type TConfigurableSchema = {
  properties: {
    [key: string]: TSchemaField;
  };
};

export type TConfigSchema = {
  definitions: {
    [key: string]: TSchemaField | TConfigurableSchema;
  };
};

export type TRunConfig = {
  tags: string[];
  metadata: {};
  callbacks: string[];
  run_name: string;
  max_concurrency: number;
  recursion_limit: number;
  configurable: TConfigurable;
  run_id: string;
};

export type TRunRequest = {
  assistant_id: string;
  thread_id?: string;
  input: TRunInput[];
  config?: TRunConfig;
};

// Not quite right... check when fix bug
export type TRunDetail = {
  loc: (string | number)[];
  msg: string;
  type: string;
};

export type TRunResponse = {
  detail: TRunDetail;
};

export type THistory = {
  id: string;
  thread_id: string;
  user_id: string;
  assistant_id: string;
  content: string;
  type: string;
  additional_kwargs: {};
  example: boolean;
  created_at: string;
  updated_at: string;
};

export type TTitleRequest = {
  thread_id: string;
  history: THistory[];
};

export type TUser = {
  user_id?: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  kwargs: {};
  created_at?: string;
  updated_at?: string;
};

export type TThread = {
  id?: string;
  user_id?: string;
  assistant_id?: string;
  name: string;
  kwargs?: {};
  created_at?: string;
  updated_at?: string;
};

export type TGroupedThreads = {
  Today?: TThread[];
  Yesterday?: TThread[];
  "Past 7 Days"?: TThread[];
  "Past 30 Days"?: TThread[];
  "This Year"?: TThread[];
  "Previous Years"?: TThread[];
};

export type TThreadRequest = {
  assistant_id: string;
  name: string;
  kwargs?: {};
};

export type TThreadState = {
  values: TMessage[];
  next: string[];
};

export type TToolCall = {
  name: string;
  args: {
    query: string;
  };
  id: string;
};

export type TMessage = {
  content: string;
  additional_kwargs?: {
    additional_kwargs?: {};
    example?: boolean;
  };
  responsoe_metadata?: {
    finish_reason?: boolean;
  };
  type: string;
  name?: string | null;
  id: string;
  example: boolean;
  tool_calls?: TToolCall[];
  invalid_tool_calls?: string[];
};

export type TUpdateMessageRequest = {
  assistant_id: string;
  content: string;
  additional_kwargs: {};
};

export interface TAssistant {
  id?: string;
  created_at?: string;
  updated_at?: string;
  user_id?: string;
  name: string;
  config: {
    configurable: TConfigurable;
  };
  kwargs?: {};
  file_ids?: string[];
  public?: boolean;
}

export type TCreateAssistantFileRequest = {
  file_id: string;
};

export type TAssistantFile = {
  file_id: string;
  asssistant_id: string;
};

export type TPurpose = "assistants" | "threads" | "personas";

export type TTool = {
  name: string;
  type: string;
  description: string;
  config: {};
  multi_use: boolean;
};

export type TConfigDefinitions = {
  title: string;
  properties: {
    type: {
      default: string;
    };
    name: {
      default: string;
    };
    description: {
      default: string;
    };
    multi_use: {
      default: boolean;
    };
  };
};

export type TFile = {
  id: string;
  user_id?: string;
  purpose: TPurpose;
  filename: string;
  bytes: number;
  mime_type: string;
  source: string;
  kwargs: {};
  created_at: string;
  updated_at: string;
};

export type TVectorDatabase = {
  type: string;
  config: {
    api_key: string;
    host: string;
  };
};

export type TEncoder = {
  dimensions: number;
  encoder_model: string;
  provider: string;
};

export type TUnstructured = {
  hi_res_model_name: string;
  partition_strategy: string;
  process_tables: boolean;
};

export type TSplitter = {
  max_tokens: number;
  min_tokens: number;
  name: string;
  prefix_summary: boolean;
  prefix_titles: boolean;
  rolling_window_size: number;
};

export type TIngestFileDataRequest = {
  files: string[];
  purpose: TPurpose;
  namespace: string;
  vector_database: TVectorDatabase;
  document_processor: {
    summarize: boolean;
    encoder: TEncoder;
    unstructured: TUnstructured;
    splitter: TSplitter;
  };
  webhook_url: string;
};

export type TQuery = {
  input: string;
  namespace: string;
  context: string;
  index_name: string;
  vector_database: TVectorDatabase;
  encoder: TEncoder;
  enable_rerank: boolean;
  interpreter_mode: boolean;
  exclude_fields: string[];
};

export type TQueryData = {
  id: string;
  document_id: string;
  page_content: string;
  file_id: string;
  namespace: string;
  source: string;
  source_type: string;
  chunk_index: number;
  title: string;
  purpose: TPurpose;
  token_count: number;
  page_number: number;
  metadata: {};
  dense_embedding: number[];
};

export type TQueryResponse = {
  success: boolean;
  data: TQueryData[];
};

export type TUploadFileRequest = {
  file: File;
  purpose: TPurpose;
  filename: string;
  kwargs: string;
};

export type TDeleteFileResponse = {
  file_id: string;
  num_of_deleted_chunks?: number;
  num_of_assistants: number;
  assistants: TAssistant[];
};

export type TGetFiles = {
  purpose?: string;
};

export type TGenerateTitle = {
  thread_id: string;
  history: THistory[];
};

export type TUpdateThread = {
  assistant_id: string;
  name: string;
  kwargs?: {};
};
