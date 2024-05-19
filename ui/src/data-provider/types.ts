export type TRunInput = {
    content: string;
    role: string;
    additional_kwargs: {};
    example: boolean;
}

export type TConfigurable = {}

export type TRunConfig = {
    tags: string[];
    metadata: {};
    callbacks: string[];
    run_name: string;
    max_concurrency: number;
    recursion_limit: number;
    configurable: TConfigurable;
    run_id: string;
}

export type TRunRequest = {
    user_id: string;
    assistant_id: string;
    thread_id: string;
    input: TRunInput[];
    config: TRunConfig;
}

// Not quite right... check when fix bug
export type TRunDetail = {
    loc: (string | number)[];
    msg: string;
    type: string;
}

export type TRunResponse = {
    detail: TRunDetail;
}

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
}

export type TTitleRequest = {
    thread_id: string;
    history: THistory[];
}

export type TUser = {
    user_id?: string;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    kwargs: {};
    created_at?: string;
    updated_at?: string;
}

export type TThread = {
    id: string;
    user_id: string;
    assistant_id: string;
    name: string;
    kwargs: {};
    created_at: string;
    updated_at?: string;
}

export type TThreadRequest = {
    assistant_id: string;
    name: string;
    kwargs: {};
}

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
}

export type TUpdateMessageRequest = {
    assistant_id: string;
    content: string;
    additional_kwargs: {};
}
