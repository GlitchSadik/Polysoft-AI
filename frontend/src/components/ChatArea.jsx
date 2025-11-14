import { useState, useEffect, useRef } from 'react'
import { sendMessage, getConversationHistory } from '../services/api'
import Message from './Message'

export default function ChatArea({ conversation, onConversationCreated, sidebarOpen, onToggleSidebar }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [currentConversationId, setCurrentConversationId] = useState(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    if (conversation) {
      loadHistory()
      setCurrentConversationId(conversation.id)
    } else {
      // Clear messages and reset conversation ID for new chat
      setMessages([])
      setCurrentConversationId(null)
    }
  }, [conversation]) // Re-run when conversation changes (null or object)

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadHistory = async () => {
    try {
      const history = await getConversationHistory(conversation.id)
      setMessages(history)
    } catch (error) {
      console.error('Failed to load history:', error)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    const messageText = input
    setInput('')
    setLoading(true)

    try {
      const response = await sendMessage(messageText, currentConversationId)
      
      // If new conversation created, save the ID and notify parent once
      if (!currentConversationId && response.conversation_id) {
        setCurrentConversationId(response.conversation_id)
        onConversationCreated({ 
          id: response.conversation_id, 
          title: messageText.slice(0, 50),
          created_at: new Date().toISOString()
        })
      }

      const assistantMessage = {
        role: 'assistant',
        content: response.answer,
        citations: response.citations
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Failed to send message:', error)
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        error: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex-1 flex flex-col bg-primary">
      {/* Header */}
      <div className="h-16 border-b border-border flex items-center px-6 bg-primary">
        <button
          onClick={onToggleSidebar}
          className="p-2 hover:bg-hover rounded-xl transition-all duration-200 mr-3"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <h1 className="text-lg font-semibold">Policy Chatbot</h1>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center px-4">
            <div className="text-center space-y-6 max-w-2xl">
              <div className="w-20 h-20 mx-auto rounded-2xl flex items-center justify-center">
                <img src="/bot-avatar.png" alt="Bot" className="w-full h-full object-contain" />
              </div>
              <h2 className="text-3xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                How can I help you today?
              </h2>
              <p className="text-text-secondary text-lg">Ask me anything about your policy documents</p>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
            {messages.map((msg, idx) => (
              <Message key={idx} message={msg} />
            ))}
            {loading && (
              <div className="flex gap-4">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0">
                  <img src="/bot-avatar.png" alt="Bot" className="w-full h-full object-contain" />
                </div>
                <div className="flex-1 bg-secondary/50 backdrop-blur-sm rounded-2xl p-6 border border-border">
                  <div className="flex gap-2">
                    <div className="w-2 h-2 bg-accent rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-accent rounded-full animate-bounce delay-100"></div>
                    <div className="w-2 h-2 bg-accent rounded-full animate-bounce delay-200"></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-border p-6 bg-primary">
        <div className="max-w-4xl mx-auto">
          <div className="relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              rows="1"
              className="w-full bg-secondary border border-border rounded-2xl px-6 py-4 pr-14 outline-none resize-none max-h-32 focus:border-accent/50 transition-all duration-200 placeholder-text-secondary"
              disabled={loading}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading}
              className="absolute right-3 bottom-3 p-2.5 bg-accent hover:bg-accent-hover disabled:bg-gray-600 disabled:cursor-not-allowed rounded-xl transition-all duration-200 shadow-lg disabled:shadow-none"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
