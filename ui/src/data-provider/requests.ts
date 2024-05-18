import axios, { AxiosRequestConfig } from "axios";

async function _get<T>(url: string, options?: AxiosRequestConfig): Promise<T> {
  const response = await axios.get(url, { ...options });
  return response.data;
}

async function _post<T>(url: string, data?: any): Promise<T> {
  const response = await axios.post(url, data);
  return response.data;
}

async function _postMultiPart<T>(
  url: string,
  formData: FormData,
  token: string | null,
): Promise<T> {
  const response = await axios.post(url, formData);
  return response.data;
}

async function _put<T>(
  url: string,
  token: string | null,
  data?: any,
): Promise<T> {
  const response = await axios.put(url, JSON.stringify(data));
  return response.data;
}

async function _patch<T>(
  url: string,
  token: string | null,
  data?: any,
): Promise<T> {
  const response = await axios.put(url, JSON.stringify(data));
  return response.data;
}

// axios.defaults.baseURL = config.url.API_URL;

// Set token for requests
// axios.interceptors.request.use(
//   async (config) => {
//     const token = await window.Clerk.session.getToken();

//     // @ts-ignore
//     config.headers = {
//       Authorization: `Bearer ${token}`,
//     };

//     return config;
//   },
//   (error) => {
//     return Promise.reject(error);
//   },
// );

// Grabs new token if bearer token is stale
// axios.interceptors.response.use(
//   async (response) => {
//     return response;
//   },
//   async (error) => {
//     const originalRequest = error.config;
//     // 403 - Forbidden means auth token stale
//     if (error.response.status === 403 && !originalRequest._retry) {
//       // Prevents continuous retries
//       originalRequest._retry = true;
//       const sessionToken = await window.Clerk.session.getToken();
//       axios.defaults.headers.common["Authorization"] = "Bearer " + sessionToken;
//       return axios(originalRequest);
//     }
//     return Promise.reject(error);
//   },
// );

const request = {
  get: _get,
  post: _post,
  postMultiPart: _postMultiPart,
  put: _put,
  patch: _patch,
};

export default request;