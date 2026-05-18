import axios from 'axios'

// Create a centralized Axios instance
const api = axios.create({
  // Import the base URL from Vite's environment variables
  baseURL: import.meta.env.VITE_API_BASE_URL,
  // Set a reasonable timeout (e.g., 10 seconds)
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export default api
