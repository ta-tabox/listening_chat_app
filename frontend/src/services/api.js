import axios from 'axios'

const API_ENDPOINT = import.meta.env.VITE_API_ENDPOINT || null

export async function sendMessage(message, history = [], summary = null) {
  if (!API_ENDPOINT) {
    console.error('API endpoint is not configured. Please set VITE_API_ENDPOINT environment variable.')
    throw new Error('API endpoint is not configured')
  }

  try {
    const payload = {
      message,
      history,
    }

    if (summary) {
      payload.summary = summary
    }

    const response = await axios.post(API_ENDPOINT, payload)
    return response.data
  } catch (error) {
    console.error('API Error:', error)
    throw error
  }
}
