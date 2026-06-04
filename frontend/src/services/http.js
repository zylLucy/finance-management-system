import axios from 'axios'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000
})

http.interceptors.response.use(
  (response) => {
    const payload = response.data
    if (payload && typeof payload === 'object' && 'code' in payload && payload.code !== 200) {
      return Promise.reject(new Error(payload.msg || '请求失败，请稍后重试'))
    }
    return payload
  },
  (error) => {
    if (error?.response?.data?.msg) {
      return Promise.reject(new Error(error.response.data.msg))
    }

    if (error?.code === 'ERR_NETWORK') {
      return Promise.reject(new Error('无法连接后端服务，请确认 FastAPI 已启动'))
    }

    return Promise.reject(new Error('请求失败，请稍后重试'))
  }
)

export default http
