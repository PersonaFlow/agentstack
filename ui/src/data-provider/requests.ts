import axios, { AxiosRequestConfig } from 'axios'

async function _get<T>(url: string, options?: AxiosRequestConfig): Promise<T> {
  const response = await axios.get(url, { ...options })
  return response.data
}

async function _post<T>(url: string, data?: any): Promise<T> {
  const response = await axios.post(url, data)
  return response.data
}

async function _postMultiPart<T>(url: string, formData: FormData): Promise<T> {
  const response = await axios.postForm(url, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

async function _put<T>(url: string, data?: any): Promise<T> {
  const response = await axios.put(url, JSON.stringify(data))
  return response.data
}

async function _patch<T>(url: string, data?: any): Promise<T> {
  const response = await axios.patch(url, data)
  return response.data
}

async function _delete<T>(url: string, data?: any): Promise<T> {
  const response = await axios.delete(url)
  return response.data
}

axios.defaults.baseURL = 'http://127.0.0.1:9000'

// Set token for requests
axios.interceptors.request.use(
  async (config) => {
    // @ts-ignore
    // config.headers = {
    //   "X-API-KEY": process.env.NEXT_PUBLIC_PERSONAFLOW_API_KEY,
    // };

    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

const request = {
  get: _get,
  post: _post,
  postMultiPart: _postMultiPart,
  put: _put,
  patch: _patch,
  delete: _delete,
}

export default request
