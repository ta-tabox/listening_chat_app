import axios from 'axios'

const API_ENDPOINT = import.meta.env.VITE_API_ENDPOINT || null
const GET_PROMPT_ENDPOINT = import.meta.env.VITE_GET_PROMPT_ENDPOINT || null
const UPDATE_PROMPT_ENDPOINT = import.meta.env.VITE_UPDATE_PROMPT_ENDPOINT || null

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

export async function getPrompt() {
  if (!GET_PROMPT_ENDPOINT) {
    console.error('Get prompt endpoint is not configured. Please set VITE_GET_PROMPT_ENDPOINT environment variable.')
    throw new Error('Get prompt endpoint is not configured')
  }

  try {
    const response = await axios.get(GET_PROMPT_ENDPOINT)
    return response.data
  } catch (error) {
    console.error('Get Prompt Error:', error)
    throw error
  }
}

export async function updatePrompt(promptText) {
  if (!UPDATE_PROMPT_ENDPOINT) {
    console.error('Update prompt endpoint is not configured. Please set VITE_UPDATE_PROMPT_ENDPOINT environment variable.')
    throw new Error('Update prompt endpoint is not configured')
  }

  try {
    const response = await axios.post(UPDATE_PROMPT_ENDPOINT, { prompt: promptText })
    return response.data
  } catch (error) {
    console.error('Update Prompt Error:', error)
    throw error
  }
}
