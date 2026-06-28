import axios from 'axios'

// Shared API client. Every api/*.ts module imports this so the base URL,
// timeout, and default headers are configured in exactly one place.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export default api
