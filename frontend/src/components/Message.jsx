export default function Message({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex gap-4 ${isUser ? 'justify-end' : ''}`}>
      {!isUser && (
        <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0">
          <img src="/bot-avatar.png" alt="Bot" className="w-full h-full object-contain" />
        </div>
      )}
      <div className={`flex-1 max-w-3xl ${isUser ? 'flex justify-end' : ''}`}>
        <div className={`rounded-2xl p-6 ${
          isUser 
            ? 'bg-gradient-to-br from-blue-900 to-cyan-900 text-white shadow-lg border border-blue-800' 
            : message.error 
              ? 'bg-red-900/30 border border-red-600/50 backdrop-blur-sm' 
              : 'bg-secondary/50 backdrop-blur-sm border border-border'
        }`}>
          <div className="whitespace-pre-wrap leading-relaxed">{message.content}</div>
          
          {message.citations && message.citations.length > 0 && (
            <div className="mt-6 pt-6 border-t border-border/50">
              <div className="text-sm font-semibold text-text-secondary mb-3 flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                Sources
              </div>
              <div className="space-y-2">
                {message.citations.map((cite, idx) => (
                  <details key={idx} className="bg-hover/30 rounded-xl p-4 text-sm border border-border/30 hover:border-accent/30 transition-all duration-200 group">
                    <summary className="cursor-pointer hover:text-accent transition-colors flex items-center gap-2 font-medium">
                      <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <span className="flex-1">{cite.doc_name}</span>
                      <span className="text-xs text-text-secondary">Lines {cite.start_line}-{cite.end_line}</span>
                    </summary>
                    <div className="mt-3 pl-6 text-xs text-text-secondary border-l-2 border-accent/50 leading-relaxed">
                      {cite.snippet}
                    </div>
                  </details>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
      {isUser && (
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-gray-600 to-gray-700 flex items-center justify-center flex-shrink-0 shadow-lg">
          👤
        </div>
      )}
    </div>
  )
}
