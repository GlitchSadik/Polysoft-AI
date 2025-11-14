"""
Retrieval-Augmented Generation (RAG) service for chat and document retrieval.
"""
from typing import List, Dict, Any, Optional
from sqlmodel import Session, select
from datetime import datetime
import logging

from app.models.conversations import Conversation
from app.models.messages import Message
from app.config import RETRIEVAL_TOP_K, CONVERSATION_HISTORY_LENGTH
from app.services.llm_service import get_llm_service
from app.services.document_service import get_document_service

logger = logging.getLogger(__name__)


class RAGService:
    # Manages RAG chat interactions
    
    def __init__(self):
        # Set up dependencies
        logger.info("Initializing RAGService")
        self.llm_service = get_llm_service()
        self.document_service = get_document_service()
        self.collection = self.document_service.collection
    
    def query(
        self,
        message: str,
        conversation_id: Optional[int],
        session: Session,
        top_k: int = RETRIEVAL_TOP_K
    ) -> Dict[str, Any]:
        # Main RAG query handler
        logger.info(f"Processing RAG query (conversation_id={conversation_id})")
        
        try:
            # 1. Get or create conversation
            if conversation_id:
                conversation = self._get_conversation(conversation_id, session)
                if not conversation:
                    logger.warning(f"Conversation {conversation_id} not found, creating new")
                    conversation = self._create_conversation(session, message)
            else:
                conversation = self._create_conversation(session, message)
            
            logger.info(f"Using conversation ID: {conversation.id}")
            
            # 2. Save user message
            user_message = Message(
                conversation_id=conversation.id,
                role="user",
                content=message
            )
            session.add(user_message)
            
            # 3. Update conversation timestamp
            from datetime import datetime
            conversation.updated_at = datetime.utcnow()
            session.add(conversation)
            
            session.commit()
            logger.debug(f"Saved user message: {message[:100]}...")
            
            # 3. Get conversation history
            history_messages = self._get_conversation_history(
                conversation.id,
                session,
                limit=CONVERSATION_HISTORY_LENGTH
            )
            
            # 4. Retrieve relevant chunks
            logger.info(f"Retrieving top {top_k} relevant chunks")
            retrieved_chunks = self._retrieve_chunks(message, top_k)
            
            logger.info(f"Retrieved {len(retrieved_chunks)} chunks")
            
            # 5. Build RAG prompt
            prompt = self._build_rag_prompt(
                user_message=message,
                history_messages=history_messages,
                retrieved_chunks=retrieved_chunks
            )
            
            logger.debug(f"Built prompt of length {len(prompt)}")
            
            # 6. Generate response using LLM
            logger.info("Generating LLM response")
            answer = self.llm_service.generate(prompt)
            
            # 7. Save assistant message
            assistant_message = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=answer
            )
            session.add(assistant_message)
            
            # 8. Update conversation timestamp
            from datetime import datetime
            conversation.updated_at = datetime.utcnow()
            session.add(conversation)
            
            session.commit()
            logger.debug(f"Saved assistant message: {answer[:100]}...")
            
            # 9. Format citations
            all_citations = self._format_citations(retrieved_chunks)
            
            # 10. Filter citations to only those referenced in the answer
            citations = self._filter_cited_sources(answer, all_citations)
            
            # 11. Return response
            result = {
                "conversation_id": conversation.id,
                "answer": answer,
                "citations": citations
            }
            
            logger.info(f"RAG query completed successfully")
            return result
        
        except Exception as e:
            logger.error(f"Failed to process RAG query: {e}")
            raise
    
    def _create_conversation(self, session: Session, first_message: str = None) -> Conversation:
        """
        Create a new conversation.
        
        Args:
            session: Database session
            first_message: Optional first message to generate title from
            
        Returns:
            New Conversation object
        """
        # Generate title from first message (first 50 chars)
        title = None
        if first_message:
            title = first_message[:50]
            if len(first_message) > 50:
                title += "..."
        
        conversation = Conversation(title=title)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        
        logger.info(f"Created new conversation with ID: {conversation.id}")
        return conversation
    
    def _get_conversation(
        self, conversation_id: int, session: Session
    ) -> Optional[Conversation]:
        """
        Retrieve a conversation by ID.
        
        Args:
            conversation_id: Conversation ID
            session: Database session
            
        Returns:
            Conversation object or None
        """
        statement = select(Conversation).where(Conversation.id == conversation_id)
        return session.exec(statement).first()
    
    def _get_conversation_history(
        self,
        conversation_id: int,
        session: Session,
        limit: int = CONVERSATION_HISTORY_LENGTH
    ) -> List[Message]:
        """
        Get recent messages from a conversation.
        
        Args:
            conversation_id: Conversation ID
            session: Database session
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of Message objects (oldest first)
        """
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = list(session.exec(statement))
        
        # Reverse to get chronological order
        messages.reverse()
        
        logger.debug(f"Retrieved {len(messages)} history messages")
        return messages
    
    def _retrieve_chunks(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks from ChromaDB.
        
        Args:
            query: Search query
            top_k: Number of chunks to retrieve
            
        Returns:
            List of chunk dictionaries with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.llm_service.embed_text(query)
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            chunks = []
            if results and results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    chunk = {
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    }
                    chunks.append(chunk)
            
            logger.info(f"Retrieved {len(chunks)} chunks from ChromaDB")
            return chunks
        
        except Exception as e:
            logger.error(f"Failed to retrieve chunks: {e}")
            return []
    
    def _build_rag_prompt(
        self,
        user_message: str,
        history_messages: List[Message],
        retrieved_chunks: List[Dict[str, Any]]
    ) -> str:
        """
        Build the RAG prompt with history and context.
        
        Args:
            user_message: Current user message
            history_messages: Previous messages in conversation
            retrieved_chunks: Retrieved document chunks
            
        Returns:
            Formatted prompt string
        """
        # System instruction
        prompt_parts = [
            "You are an AI assistant that answers strictly from company policy documents.",
            "IMPORTANT: When answering, cite the sources you use by referencing their numbers (e.g., [1], [2]).",
            "Only cite sources that directly support your answer.",
            "If the answer is not in the context, say:",
            '"I could not find this information in the provided company policies."',
            ""
        ]
        
        # Conversation history
        if history_messages:
            prompt_parts.append("Conversation history:")
            for msg in history_messages:
                role_label = "USER" if msg.role == "user" else "ASSISTANT"
                prompt_parts.append(f"{role_label}: {msg.content}")
            prompt_parts.append("")
        
        # Context chunks
        prompt_parts.append("Context (each block labeled with the source document, section title, and line range):")
        prompt_parts.append("")
        
        for idx, chunk in enumerate(retrieved_chunks, 1):
            metadata = chunk['metadata']
            doc_name = metadata.get('doc_name', 'unknown')
            section_title = metadata.get('section_title', '')
            start_line = metadata.get('start_line', 0)
            end_line = metadata.get('end_line', 0)
            content = chunk['content']
            
            prompt_parts.append(
                f'[{idx}] (doc={doc_name}, section="{section_title}", '
                f'lines={start_line}-{end_line})'
            )
            prompt_parts.append(content)
            prompt_parts.append("")
        
        # Current user query
        prompt_parts.append(f"USER: {user_message}")
        
        prompt = "\n".join(prompt_parts)
        return prompt
    
    def _format_citations(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format retrieved chunks as citations with readable snippets.
        
        Args:
            chunks: Retrieved chunk dictionaries
            
        Returns:
            List of citation dictionaries
        """
        citations = []
        
        for chunk in chunks:
            metadata = chunk['metadata']
            content = chunk['content']
            
            # Create readable snippet starting from sentence boundary
            snippet = self._create_readable_snippet(content, max_length=250)
            
            citation = {
                "doc_name": metadata.get('doc_name', 'unknown'),
                "section_title": metadata.get('section_title', ''),
                "start_line": metadata.get('start_line', 0),
                "end_line": metadata.get('end_line', 0),
                "snippet": snippet
            }
            citations.append(citation)
        
        return citations
    
    def _create_readable_snippet(self, content: str, max_length: int = 250) -> str:
        """
        Create a readable snippet that starts at a sentence boundary.
        
        Args:
            content: Full chunk content
            max_length: Maximum snippet length
            
        Returns:
            Readable snippet string
        """
        if len(content) <= max_length:
            return content
        
        # Try to find the first sentence start
        # Look for common sentence starters after trimming leading whitespace
        content_stripped = content.lstrip()
        
        # If content starts mid-sentence, try to find the next sentence
        if content_stripped and not content_stripped[0].isupper():
            # Find the first period, question mark, or exclamation followed by space and capital
            import re
            match = re.search(r'[.!?]\s+([A-Z])', content_stripped)
            if match:
                # Start from the capital letter after the punctuation
                start_pos = match.start(1)
                content_stripped = content_stripped[start_pos:]
        
        # Now take up to max_length and try to end at a sentence boundary
        if len(content_stripped) <= max_length:
            return content_stripped
        
        snippet = content_stripped[:max_length]
        
        # Try to end at the last complete sentence
        import re
        last_sentence_end = max(
            snippet.rfind('. '),
            snippet.rfind('! '),
            snippet.rfind('? ')
        )
        
        if last_sentence_end > max_length * 0.6:  # Only if we keep at least 60% of the snippet
            snippet = snippet[:last_sentence_end + 1]
        else:
            snippet += "..."
        
        return snippet
    
    def _filter_cited_sources(self, answer: str, citations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter citations to only include sources that were referenced in the answer.
        
        Args:
            answer: The LLM's response text
            citations: All available citations
            
        Returns:
            Filtered list of citations that were actually used
        """
        import re
        
        # Find all citation numbers in the answer like [1], [2], etc.
        cited_numbers = set()
        matches = re.findall(r'\[(\d+)\]', answer)
        cited_numbers.update(int(num) for num in matches)
        
        # If no citations found in answer, return empty list (LLM didn't cite anything)
        if not cited_numbers:
            logger.warning("No citation markers found in LLM response - returning no citations")
            return []
        
        # Filter citations to only those referenced (convert to 0-indexed)
        filtered = []
        for num in sorted(cited_numbers):
            idx = num - 1  # Citations are 1-indexed in prompt
            if 0 <= idx < len(citations):
                filtered.append(citations[idx])
        
        logger.info(f"Filtered citations from {len(citations)} to {len(filtered)} based on answer")
        return filtered if filtered else citations  # Return all if filtering fails
    
    def get_conversation_messages(
        self, conversation_id: int, session: Session
    ) -> List[Dict[str, Any]]:
        """
        Get all messages for a conversation.
        
        Args:
            conversation_id: Conversation ID
            session: Database session
            
        Returns:
            List of message dictionaries
        """
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        messages = list(session.exec(statement))
        
        return [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]


# Global singleton instance
_rag_service_instance = None


def get_rag_service() -> RAGService:
    """
    Get or create the global RAGService instance.
    
    Returns:
        RAGService instance
    """
    global _rag_service_instance
    
    if _rag_service_instance is None:
        logger.info("Initializing global RAGService")
        _rag_service_instance = RAGService()
    
    return _rag_service_instance
