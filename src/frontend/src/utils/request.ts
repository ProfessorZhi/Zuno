import axios from 'axios'
import { apiUrl, isDesktopRuntime } from './api'

const request = axios.create({
  baseURL: '',
  timeout: 10000,
})

request.interceptors.request.use(
  (config) => {
    if (config.url) {
      config.url = apiUrl(config.url)
    }

    const token = localStorage.getItem('token')
    if (token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    console.error('Request interceptor error:', error)
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('Response error:', error.response?.status, error.config?.url)
    console.error('Response error detail:', error.response?.data || error.message)

    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')

      if (isDesktopRuntime()) {
        window.location.hash = '#/login'
      } else {
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export { request }
