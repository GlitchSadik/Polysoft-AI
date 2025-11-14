import { useState } from 'react'
import UploadModal from './UploadModal'
import DocumentsModal from './DocumentsModal'

export default function Sidebar({ 
  conversations, 
  activeConversation, 
  onNewChat, 
  onSelectConversation,
  isOpen,
  onToggle,
  onRefresh
}) {
  const [showUpload, setShowUpload] = useState(false)
  const [showDocuments, setShowDocuments] = useState(false)

  return (
    <>
      <div className={`${isOpen ? 'w-72' : 'w-0'} bg-primary border-r border-border transition-all duration-300 flex flex-col`}>
        {isOpen && (
          <>
            {/* Header */}
            <div className="p-3">
              <button
                onClick={onNewChat}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-gradient-to-r from-blue-900 to-cyan-900 hover:from-blue-800 hover:to-cyan-800 transition-all duration-200 font-medium shadow-lg border border-blue-800"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                <span>New Chat</span>
              </button>
            </div>

            {/* Conversations List */}
            <div className="flex-1 overflow-y-auto px-3 py-2">
              {conversations.length > 0 && (
                <div className="mb-3">
                  <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider px-3 mb-2">
                    Recent Chats
                  </h3>
                </div>
              )}
              <div className="space-y-1">
                {conversations.map((conv) => (
                  <button
                    key={conv.id}
                    onClick={() => onSelectConversation(conv)}
                    className={`w-full text-left px-3 py-3 rounded-xl transition-all duration-200 group ${
                      activeConversation?.id === conv.id
                        ? 'bg-hover text-text-primary shadow-md'
                        : 'hover:bg-hover/60 text-text-secondary hover:text-text-primary'
                    }`}
                  >
                    <div className="text-sm font-medium truncate">
                      {conv.title || `Conversation ${conv.id}`}
                    </div>
                    <div className="text-xs text-text-secondary mt-1 flex items-center gap-1">
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {new Date(conv.created_at).toLocaleDateString()}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Upload and Manage Buttons */}
            <div className="p-3 border-t border-border space-y-2">
              <button
                onClick={() => setShowUpload(true)}
                className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-secondary hover:bg-hover transition-all duration-200 border border-border"
              >
                <svg className="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <span className="font-medium text-sm">Upload PDF</span>
              </button>
              
              <button
                onClick={() => setShowDocuments(true)}
                className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-secondary hover:bg-hover transition-all duration-200 border border-border"
              >
                <svg className="w-5 h-5 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="font-medium text-sm">Manage PDFs</span>
              </button>
            </div>
          </>
        )}
      </div>

      {showUpload && (
        <UploadModal 
          onClose={() => setShowUpload(false)} 
          onSuccess={onRefresh}
        />
      )}
      
      {showDocuments && (
        <DocumentsModal 
          onClose={() => setShowDocuments(false)}
        />
      )}
    </>
  )
}
