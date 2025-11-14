import axios from 'axios'

const API_BASE = '/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const sendMessage = async (message, conversationId = null) => {
  const { data } = await api.post('/chat/query', {
    message,
    conversation_id: conversationId,
  })
  return data
}

export const getConversations = async () => {
  try {
    const { data } = await api.get('/chat/conversations')
    console.log('Loaded conversations:', data)
    return data
  } catch (error) {
    console.error('Failed to load conversations:', error)
    // If endpoint doesn't exist, return empty array
    return []
  }
}

export const getConversationHistory = async (conversationId) => {
  try {
    const { data } = await api.get(`/chat/conversations/${conversationId}/messages`)
    // Backend returns { conversation_id, message_count, messages }
    const messages = data.messages || data
    return messages.map(msg => ({
      role: msg.role,
      content: msg.content,
      citations: msg.citations || []
    }))
  } catch (error) {
    console.error('Failed to load conversation history:', error)
    return []
  }
}

export const uploadDocument = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const { data } = await api.post('/docs/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return data
}

export const listDocuments = async () => {
  const { data } = await api.get('/docs/list')
  return data
}

export const deleteDocument = async (documentId) => {
  const { data } = await api.delete(`/docs/${documentId}`)
  return data
}
