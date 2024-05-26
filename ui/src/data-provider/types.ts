export type TRunInput = {
  content: string;
  role: string;
  additional_kwargs: {};
  example: boolean;
};

export type TBotType = "chatbot" | "chat_retrieval" | "agent";

export type TAgentType =
  | "GPT 3.5 Turbo"
  | "GPT 4 Turbo"
  | "GPT 4 (Azure OpenAI)"
  | "Claude 2"
  | "Claude 2 (Amazon Bedrock)"
  | "GEMINI"
  | "Ollama";

export type TConfigurableTool =
  | "DDG Search"
  | "Search (Tavily)"
  | "Search (short answer, Tavily)"
  | "Retrieval"
  | "Arxiv"
  | "PubMed"
  | "Wikipedia";

export type TLLMType =
  | "GPT 3.5 Turbo"
  | "GPT 4"
  | "GPT 4 (Azure OpenAI)"
  | "Claude 2"
  | "Claude 2 (Amazon Bedrock)"
  | "GEMINI"
  | "Mixtral"
  | "Ollama";

export type TConfigurable = {
  type: TBotType;
  agent_type: TAgentType;
  interrupt_before_action: boolean;
  retrieval_description: string;
  system_message: string;
  tools: TConfigurableTool[];
  llm_type: TLLMType;
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
  user_id: string;
  assistant_id: string;
  thread_id: string;
  input: TRunInput[];
  config: TRunConfig;
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
  id: string;
  user_id: string;
  assistant_id: string;
  name: string;
  kwargs: {};
  created_at: string;
  updated_at?: string;
};

export type TThreadRequest = {
  assistant_id: string;
  name: string;
  kwargs: {};
};

export interface TCreateThreadRequest extends TThreadRequest {
  user_id: string;
}

export interface TMessage extends TMessageRequest {
  id: string;
  created_at: string;
  updated_at: string;
}

export type TMessageRequest = {
  thread_id: string;
  user_id: string;
  assistant_id: string;
  content: string;
  type: string;
  additional_kwargs: {};
  example: boolean;
};

export type TUpdateMessageRequest = {
  assistant_id: string;
  content: string;
  additional_kwargs: {};
};

export type TAssistantRequest = {
  user_id: string;
  name: string;
  config: {
    configurable: TConfigurable;
  };
  kwargs: {};
  file_ids: string[];
  public: boolean;
};

export interface TAssistant extends TAssistantRequest {
  id: string;
  created_at: string;
  updated_at: string;
}

export type TCreateAssistantFileRequest = {
  file_id: string;
};

export type TAssistantFile = {
  file_id: string;
  asssistant_id: string;
};

export type TPurpose = "assistants" | "threads" | "personas";

export type TFile = {
  id: string;
  user_id: string;
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
  user_id: string;
  filename: string;
  kwargs: string;
};

export type TDeleteFileResponse = {
  file_id: string;
  num_of_deleted_chunks: number;
  num_of_assistants: number;
  assistants: TAssistant[];
};

export type TGenerateTitle = {
  thread_id: string;
  history: THistory[];
};
