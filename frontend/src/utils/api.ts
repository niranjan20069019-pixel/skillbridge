import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('skillbridge_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ERR_CANCELED' || error.code === 'ERR_ABORTED') {
      return Promise.reject(error)
    }
    const message = error.response?.data?.error || error.message || 'Something went wrong'
    const status = error.response?.status
    if (status === 429) {
      return Promise.reject(new Error('Too many requests. Please wait a moment and try again.'))
    }
    return Promise.reject(new Error(message))
  }
)

export default api
