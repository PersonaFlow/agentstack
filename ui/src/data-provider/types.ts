export type TStreamInput = {}

export type TConfigurable = {}

export type TMetadata = {}

export type TStreamConfig = {
    tags: string[];
    metadata: TMetadata;
    callbacks: string[];
    run_name: string;
    max_concurrency: number;
    recursion_limit: number;
    configurable: TConfigurable;
    run_id: string;
}

export type TStreamRequest = {
    user_id: string;
    assistant_id: string;
    thread_id: string;
    input: TStreamInput[];
    config: TStreamConfig;
}

export type TStreamDetail = {
    loc: (string | number)[];
    msg: string;
    type: string;
}

export type TStreamResponse = {
    detail: TStreamDetail;
}