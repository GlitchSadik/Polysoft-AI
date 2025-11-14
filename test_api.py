#!/usr/bin/env python3
"""
Test script for RAG chatbot setup and functionality.
"""
import requests
import json
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_health():
    """Test health endpoint."""
    print_section("Testing Health Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        
        data = response.json()
        print(f"Status: {data['status']}")
        print(f"Database: {data['db']}")
        print(f"ChromaDB: {data['chroma']}")
        
        return data['status'] == 'ok'
    
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_upload_document():
    """Test document upload."""
    print_section("Testing Document Upload")
    
    # Use the sample policy file
    sample_file = Path("storage/docs/sample_company_policy.txt")
    
    if not sample_file.exists():
        print(f"❌ Sample file not found: {sample_file}")
        return None
    
    try:
        with open(sample_file, 'rb') as f:
            files = {'file': (sample_file.name, f, 'text/plain')}
            response = requests.post(f"{BASE_URL}/docs/upload", files=files)
            response.raise_for_status()
        
        data = response.json()
        print(f"✅ Upload successful!")
        print(f"   Document ID: {data['document_id']}")
        print(f"   Name: {data['document_name']}")
        print(f"   Lines: {data['line_count']}")
        print(f"   Characters: {data['character_count']}")
        print(f"   Chunks: {data['chunk_count']}")
        
        return data['document_id']
    
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return None


def test_chat_query(query):
    """Test chat query."""
    print_section(f"Testing Chat Query: '{query}'")
    
    try:
        payload = {
            "message": query,
            "conversation_id": None
        }
        
        response = requests.post(
            f"{BASE_URL}/chat/query",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Query successful!")
        print(f"   Conversation ID: {data['conversation_id']}")
        print(f"\n📝 Answer:")
        print(f"   {data['answer']}")
        print(f"\n📚 Citations ({len(data['citations'])}):")
        
        for i, citation in enumerate(data['citations'], 1):
            print(f"\n   [{i}] {citation['doc_name']}")
            print(f"       Section: {citation['section_title']}")
            print(f"       Lines: {citation['start_line']}-{citation['end_line']}")
            print(f"       Snippet: {citation['snippet'][:100]}...")
        
        return data['conversation_id']
    
    except Exception as e:
        print(f"❌ Chat query failed: {e}")
        return None


def test_list_documents():
    """Test listing documents."""
    print_section("Testing List Documents")
    
    try:
        response = requests.get(f"{BASE_URL}/docs/list")
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Found {data['count']} documents:")
        
        for doc in data['documents']:
            print(f"\n   ID: {doc['id']}")
            print(f"   Name: {doc['name']}")
            print(f"   Created: {doc['created_at']}")
        
        return True
    
    except Exception as e:
        print(f"❌ List documents failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  RAG Company Policy Chatbot - Test Suite")
    print("=" * 70)
    print(f"\nTesting API at: {BASE_URL}")
    print("Make sure the server is running (python app/main.py)")
    
    input("\nPress Enter to start tests...")
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Health check failed. Aborting tests.")
        sys.exit(1)
    
    # Test 2: Upload document
    doc_id = test_upload_document()
    if not doc_id:
        print("\n⚠️  Document upload failed. Continuing with other tests...")
    
    # Test 3: List documents
    test_list_documents()
    
    # Test 4: Chat queries
    test_queries = [
        "What are the working hours?",
        "How many days of annual leave do employees get?",
        "What is the remote work policy?",
        "What is the professional development budget?",
    ]
    
    conversation_id = None
    for query in test_queries:
        conversation_id = test_chat_query(query)
    
    # Summary
    print_section("Test Summary")
    print("✅ All tests completed!")
    print("\nNote: The LLM responses are placeholders.")
    print("Replace llm_service.generate() with a real LLM API to see actual answers.")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
