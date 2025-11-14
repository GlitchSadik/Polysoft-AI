"""
Embeddings and text generation using sentence-transformers and OpenAI.
"""
from typing import List
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from app.config import (
    EMBEDDING_MODEL_NAME,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    OPENAI_MAX_TOKENS
)
import logging

logger = logging.getLogger(__name__)


class LLMService:
    # Handles embeddings and LLM text generation
    
    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        # Initialize embedding model and OpenAI client
        logger.info("Initializing LLM service")
        self.model_name = model_name
        self.embedding_model = None
        self.openai_client = None
        self._load_embedding_model()
        self._initialize_openai()
    
    def _load_embedding_model(self):
        # Load embedding model
        logger.info(f"Loading embedding model: {self.model_name}")
        try:
            self.embedding_model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def _initialize_openai(self):
        # Set up OpenAI client
        if not OPENAI_API_KEY:
            logger.warning("OpenAI API key not found. LLM generation will fail.")
            self.openai_client = None
            return
        
        try:
            self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info(f"OpenAI client initialized with model: {OPENAI_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.openai_client = None
    
    def embed_text(self, text: str) -> List[float]:
        # Return embedding for a single text
        try:
            if not text or not text.strip():
                logger.warning("Attempted to embed empty text")
                return []
            
            # Generate embedding
            embedding = self.embedding_model.encode(
                text,
                convert_to_tensor=False,
                show_progress_bar=False
            )
            
            # Convert to list
            embedding_list = embedding.tolist()
            
            logger.debug(
                f"Generated embedding of dimension {len(embedding_list)} "
                f"for text of length {len(text)}"
            )
            
            return embedding_list
        
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        # Return embeddings for a list of texts
        try:
            if not texts:
                return []
            
            logger.info(f"Generating embeddings for {len(texts)} texts")
            
            embeddings = self.embedding_model.encode(
                texts,
                convert_to_tensor=False,
                show_progress_bar=False,
                batch_size=32
            )
            
            embeddings_list = [emb.tolist() for emb in embeddings]
            
            logger.info(f"Successfully generated {len(embeddings_list)} embeddings")
            return embeddings_list
        
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise
    
    def generate(self, prompt: str) -> str:
        # Generate text using OpenAI API
        if not self.openai_client:
            error_msg = "OpenAI client not initialized. Please set OPENAI_API_KEY in .env file."
            logger.error(error_msg)
            return error_msg
        
        try:
            logger.info(f"Generating response with {OPENAI_MODEL}")
            logger.debug(f"Prompt length: {len(prompt)} characters")
            
            response = self.openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on company policy documents. "
                                   "CRITICAL: When you reference information from the numbered sources [1], [2], [3], etc. provided in the context, "
                                   "you MUST cite them by including the source number in square brackets like [1] or [2] in your answer. "
                                   "Only cite sources that directly support your statements. "
                                   "Provide accurate, concise answers using only the context provided."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=OPENAI_TEMPERATURE,
                max_tokens=OPENAI_MAX_TOKENS
            )
            
            generated_text = response.choices[0].message.content
            logger.info(f"Generated response of {len(generated_text)} characters")
            logger.debug(f"Response preview: {generated_text[:100]}...")
            
            return generated_text
            
        except Exception as e:
            error_msg = f"OpenAI API error: {str(e)}"
            logger.error(error_msg)
            return f"Error generating response: {str(e)}"


# Singleton instance
_llm_service_instance = None


def get_llm_service() -> LLMService:
    # Singleton getter for LLMService
    global _llm_service_instance
    
    if _llm_service_instance is None:
        logger.info("Initializing global LLM service")
        _llm_service_instance = LLMService()
    
    return _llm_service_instance
