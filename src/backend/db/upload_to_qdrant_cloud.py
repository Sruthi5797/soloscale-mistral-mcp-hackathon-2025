#!/usr/bin/env python3
"""
Qdrant Cloud Upload Script for Yoga Poses Dataset

This script uploads the cleaned yoga poses data to Qdrant Cloud,
creates a collection, and inserts all records with embeddings.
"""

import json
import logging
import os
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
    from qdrant_client.http.models import Distance, VectorParams, PointStruct
except ImportError:
    print("❌ Qdrant client not installed. Install with: pip install qdrant-client")
    sys.exit(1)

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    print("❌ SentenceTransformers not available. Install with: pip install sentence-transformers")
    EMBEDDINGS_AVAILABLE = False


class QdrantCloudUploader:
    """Handles uploading yoga poses data to Qdrant Cloud."""
    
    def __init__(self, 
                 url: str,
                 api_key: str,
                 collection_name: str = "yoga_poses",
                 embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize Qdrant Cloud client.
        
        Args:
            url: Qdrant Cloud cluster URL
            api_key: Qdrant Cloud API key
            collection_name: Name of the collection to create
            embedding_model: SentenceTransformers model name
        """
        self.url = url
        self.api_key = api_key
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model
        
        # Initialize Qdrant client
        try:
            self.client = QdrantClient(
                url=url,
                api_key=api_key,
            )
            print(f"✅ Connected to Qdrant Cloud: {url}")
        except Exception as e:
            print(f"❌ Failed to connect to Qdrant Cloud: {e}")
            sys.exit(1)
        
        # Initialize embedding model
        if EMBEDDINGS_AVAILABLE:
            print(f"🔄 Loading embedding model: {embedding_model}")
            self.embedding_model = SentenceTransformer(embedding_model)
            self.vector_size = self.embedding_model.get_sentence_embedding_dimension()
            print(f"✅ Embedding model loaded. Vector size: {self.vector_size}")
        else:
            print("❌ Embedding model not available")
            sys.exit(1)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_cleaned_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Load cleaned data from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                records = data.get('records', [])
                print(f"✅ Loaded {len(records)} records from {file_path}")
                return records
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return []
    
    def create_collection(self, recreate: bool = False) -> bool:
        """Create Qdrant collection."""
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_exists = any(col.name == self.collection_name for col in collections)
            
            if collection_exists and recreate:
                print(f"🗑️  Deleting existing collection: {self.collection_name}")
                self.client.delete_collection(self.collection_name)
                collection_exists = False
            
            if not collection_exists:
                print(f"🔄 Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                print(f"✅ Collection '{self.collection_name}' created successfully")
            else:
                print(f"ℹ️  Collection '{self.collection_name}' already exists")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating collection: {e}")
            return False
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for text data."""
        try:
            print(f"🔄 Generating embeddings for {len(texts)} texts...")
            embeddings = self.embedding_model.encode(
                texts, 
                convert_to_tensor=False,
                show_progress_bar=True
            )
            print(f"✅ Generated {len(embeddings)} embeddings")
            return embeddings.tolist() if hasattr(embeddings, 'tolist') else embeddings
        except Exception as e:
            print(f"❌ Error generating embeddings: {e}")
            return []
    
    def prepare_points(self, records: List[Dict[str, Any]]) -> List[PointStruct]:
        """Prepare data points for Qdrant insertion."""
        print("🔄 Preparing points for upload...")
        
        # Extract searchable texts for embedding
        searchable_texts = [record['searchable_text'] for record in records]
        
        # Generate embeddings
        embeddings = self.generate_embeddings(searchable_texts)
        
        if len(embeddings) != len(records):
            print(f"❌ Mismatch: {len(embeddings)} embeddings vs {len(records)} records")
            return []
        
        # Prepare points
        points = []
        for i, record in enumerate(records):
            # Create payload with all record data
            payload = {
                'name': record['name'],
                'sanskrit_name': record.get('sanskrit_name'),
                'expertise_level': record['expertise_level'],
                'pose_type': record['pose_type'],
                'followup_poses': record['followup_poses'],
                'photo_url': record.get('photo_url'),
                'searchable_text': record['searchable_text'],
                'has_followup_poses': record['metadata']['has_followup_poses'],
                'has_photo': record['metadata']['has_photo']
            }
            
            point = PointStruct(
                id=record['id'],
                vector=embeddings[i],
                payload=payload
            )
            points.append(point)
        
        print(f"✅ Prepared {len(points)} points for upload")
        return points
    
    def upload_data(self, records: List[Dict[str, Any]], batch_size: int = 50) -> bool:
        """Upload data to Qdrant Cloud."""
        try:
            # Prepare points
            points = self.prepare_points(records)
            
            if not points:
                print("❌ No points to upload")
                return False
            
            # Upload in batches
            print(f"🔄 Uploading {len(points)} points in batches of {batch_size}...")
            
            total_batches = (len(points) - 1) // batch_size + 1
            
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                batch_num = i // batch_size + 1
                
                print(f"📤 Uploading batch {batch_num}/{total_batches} ({len(batch)} points)")
                
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
                
                print(f"✅ Batch {batch_num} uploaded successfully")
            
            print("🎉 All data uploaded successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error uploading data: {e}")
            return False
    
    def verify_upload(self) -> Dict[str, Any]:
        """Verify the upload by checking collection info."""
        try:
            info = self.client.get_collection(self.collection_name)
            collection_info = {
                'status': info.status,
                'points_count': info.points_count,
                'vectors_count': info.vectors_count,
                'indexed_vectors_count': info.indexed_vectors_count
            }
            
            print(f"📊 Collection Info:")
            print(f"   Status: {collection_info['status']}")
            print(f"   Points: {collection_info['points_count']}")
            print(f"   Vectors: {collection_info['vectors_count']}")
            print(f"   Indexed: {collection_info['indexed_vectors_count']}")
            
            return collection_info
            
        except Exception as e:
            print(f"❌ Error verifying upload: {e}")
            return {}
    
    def test_search(self, query: str = "standing balance pose", limit: int = 3):
        """Test search functionality."""
        try:
            print(f"\n🔍 Testing search with query: '{query}'")
            
            # Generate query embedding
            query_embedding = self.generate_embeddings([query])[0]
            
            # Perform search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                with_payload=True
            )
            
            print(f"📋 Search Results:")
            for i, result in enumerate(search_results, 1):
                payload = result.payload
                print(f"   {i}. {payload['name']} ({payload.get('sanskrit_name', 'N/A')})")
                print(f"      └── {payload['expertise_level']} | {', '.join(payload['pose_type'])} | Score: {result.score:.3f}")
            
            return search_results
            
        except Exception as e:
            print(f"❌ Error testing search: {e}")
            return []


def get_credentials():
    """Get Qdrant Cloud credentials from environment variables or user input."""
    # Try to get from environment variables first
    url = os.getenv('QDRANT_URL')
    api_key = os.getenv('QDRANT_API_KEY')
    
    if not url:
        print("\n🔑 Enter your Qdrant Cloud credentials:")
        url = input("Qdrant Cloud URL: ").strip()
    
    if not api_key:
        api_key = input("Qdrant API Key: ").strip()
    
    if not url or not api_key:
        print("❌ Both URL and API key are required")
        return None, None
    
    return url, api_key


def main():
    """Main function to upload data to Qdrant Cloud."""
    print("🧘 YOGA POSES QDRANT CLOUD UPLOADER")
    print("=" * 50)
    
    # Configuration
    data_file = "dataset/cleaned_yoga_poses_simple.json"
    collection_name = "yoga_poses"
    
    # Check if data file exists
    if not Path(data_file).exists():
        print(f"❌ Data file not found: {data_file}")
        print("Please run the cleaning script first: python clean_yoga_simple.py")
        return False
    
    # Get credentials
    url, api_key = get_credentials()
    if not url or not api_key:
        return False
    
    try:
        # Initialize uploader
        uploader = QdrantCloudUploader(
            url=url,
            api_key=api_key,
            collection_name=collection_name
        )
        
        # Load data
        records = uploader.load_cleaned_data(data_file)
        if not records:
            print("❌ No data to upload")
            return False
        
        # Create collection
        if not uploader.create_collection(recreate=True):
            print("❌ Failed to create collection")
            return False
        
        # Upload data
        if not uploader.upload_data(records):
            print("❌ Failed to upload data")
            return False
        
        # Verify upload
        info = uploader.verify_upload()
        if not info:
            print("❌ Failed to verify upload")
            return False
        
        # Test search
        uploader.test_search()
        
        print(f"\n🎉 Upload completed successfully!")
        print(f"Collection '{collection_name}' is ready for use.")
        print(f"You can now query your yoga poses using semantic search!")
        
        return True
        
    except KeyboardInterrupt:
        print("\n❌ Upload cancelled by user")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
