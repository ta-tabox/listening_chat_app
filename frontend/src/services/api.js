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

    const response = await axios.post(`${API_ENDPOINT}/chat`, payload)
    return response.data
  } catch (error) {
    console.error('API Error:', error)
    throw error
  }
}

export async function getPrompt() {
  if (!API_ENDPOINT) {
    console.error('API endpoint is not configured. Please set VITE_API_ENDPOINT environment variable.')
    throw new Error('API endpoint is not configured')
  }

  try {
    const response = await axios.get(`${API_ENDPOINT}/get_prompt`)
    return response.data
  } catch (error) {
    console.error('Get Prompt Error:', error)
    throw error
  }
}

export async function updatePrompt(promptText) {
  if (!API_ENDPOINT) {
    console.error('API endpoint is not configured. Please set VITE_API_ENDPOINT environment variable.')
    throw new Error('API endpoint is not configured')
  }

  try {
    const response = await axios.post(`${API_ENDPOINT}/update_prompt`, { prompt: promptText })
    return response.data
  } catch (error) {
    console.error('Update Prompt Error:', error)
    throw error
  }
}
