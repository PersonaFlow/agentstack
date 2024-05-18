import request from "./requests"
import * as endpoint from "./endpoints"
import * as t from "./types"

// --Runs--
export function stream(params: t.TStreamRequest): Promise<t.TStreamResponse> {
    return request.post(endpoint.stream, {
        ...params
    })
}



