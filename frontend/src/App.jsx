import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import ChatArea from './components/ChatArea'
import { getConversations } from './services/api'

function App() {
  const [conversations, setConversations] = useState([])
  const [activeConversation, setActiveConversation] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  useEffect(() => {
    loadConversations()
  }, [])

  const loadConversations = async () => {
    try {
      const data = await getConversations()
      setConversations(data)
    } catch (error) {
      console.error('Failed to load conversations:', error)
    }
  }

  const handleNewChat = () => {
    setActiveConversation(null)
  }

  const handleSelectConversation = (conv) => {
    setActiveConversation(conv)
  }

  const handleConversationCreated = async (newConv) => {
    // Reload conversations to get the updated list with proper title from backend
    await loadConversations()
    // Set the new conversation as active
    setActiveConversation(newConv)
  }

  return (
    <div className="flex h-screen overflow-hidden bg-primary">
      <Sidebar
        conversations={conversations}
        activeConversation={activeConversation}
        onNewChat={handleNewChat}
        onSelectConversation={handleSelectConversation}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        onRefresh={loadConversations}
      />
      <ChatArea
        conversation={activeConversation}
        onConversationCreated={handleConversationCreated}
        sidebarOpen={sidebarOpen}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
      />
    </div>
  )
}

export default App
