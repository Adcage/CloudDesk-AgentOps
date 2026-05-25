import axios from 'axios'

const NOT_LOGIN_CODE = 40100

const myAxios = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 60000,
  withCredentials: true,
})

const redirectToLogin = () => {
  const currentPath = window.location.pathname + window.location.search
  if (currentPath !== '/user/login') {
    window.location.href = `/user/login?redirect=${encodeURIComponent(currentPath)}`
  }
}

myAxios.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error),
)

myAxios.interceptors.response.use(
  (response) => {
    const code = response.data?.code
    if (code === NOT_LOGIN_CODE) {
      redirectToLogin()
      return Promise.reject(new Error('未登录'))
    }
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      redirectToLogin()
    }
    return Promise.reject(error)
  },
)

export default myAxios
