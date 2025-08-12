"""
Firestore Service Module
Handles all Firestore database operations for the resistance event detection system
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from contextlib import contextmanager

from google.cloud import firestore
from google.cloud.firestore_v1 import Client
from google.api_core.exceptions import GoogleAPIError
import firebase_admin
from firebase_admin import credentials

logger = logging.getLogger(__name__)


class FirestoreService:
    """Service class for Firestore operations"""
    
    _instance: Optional['FirestoreService'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Firestore client with credentials"""
        try:
            # Check for credentials in environment
            project_id = os.getenv("FIRESTORE_PROJECT_ID", "dezoomcamp23")
            
            # Try to use application default credentials first
            if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                self._client = firestore.Client(project=project_id)
                logger.info(f"Firestore client initialized with service account for project: {project_id}")
            else:
                # Use emulator if configured
                if os.getenv("FIRESTORE_EMULATOR_HOST"):
                    self._client = firestore.Client(project=project_id)
                    logger.info(f"Firestore client initialized with emulator for project: {project_id}")
                else:
                    # Default to application default credentials
                    self._client = firestore.Client(project=project_id)
                    logger.info(f"Firestore client initialized with default credentials for project: {project_id}")
                    
        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {e}")
            raise
    
    @property
    def client(self) -> Client:
        """Get the Firestore client instance"""
        if self._client is None:
            self._initialize_client()
        return self._client
    
    def health_check(self) -> Dict[str, Any]:
        """Check Firestore connection health"""
        try:
            # Try to list collections (limited to 1) as a health check
            collections = list(self.client.collections(limit=1))
            return {
                "status": "healthy",
                "connected": True,
                "project_id": self.client.project,
                "collections_accessible": True
            }
        except Exception as e:
            logger.error(f"Firestore health check failed: {e}")
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            }
    
    # Collection references
    def get_collection(self, collection_name: str):
        """Get a collection reference"""
        return self.client.collection(collection_name)
    
    # CRUD Operations for Events
    def create_event(self, event_data: Dict[str, Any]) -> str:
        """Create a new event document"""
        try:
            # Add timestamp if not present
            if 'created_at' not in event_data:
                event_data['created_at'] = datetime.utcnow()
            
            # Add to events collection
            doc_ref = self.get_collection('resistance_events').add(event_data)
            doc_id = doc_ref[1].id
            logger.info(f"Created event document: {doc_id}")
            return doc_id
        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            raise
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get an event by ID"""
        try:
            doc_ref = self.get_collection('resistance_events').document(event_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            logger.error(f"Failed to get event {event_id}: {e}")
            raise
    
    def update_event(self, event_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an event document"""
        try:
            # Add updated timestamp
            update_data['updated_at'] = datetime.utcnow()
            
            doc_ref = self.get_collection('resistance_events').document(event_id)
            doc_ref.update(update_data)
            logger.info(f"Updated event document: {event_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update event {event_id}: {e}")
            raise
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an event document"""
        try:
            doc_ref = self.get_collection('resistance_events').document(event_id)
            doc_ref.delete()
            logger.info(f"Deleted event document: {event_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete event {event_id}: {e}")
            raise
    
    def list_events(self, 
                   instrument: Optional[str] = None,
                   granularity: Optional[str] = None,
                   limit: int = 100,
                   offset: int = 0) -> List[Dict[str, Any]]:
        """List events with optional filters"""
        try:
            query = self.get_collection('resistance_events')
            
            # Apply filters
            if instrument:
                query = query.where('instrument', '==', instrument)
            if granularity:
                query = query.where('granularity', '==', granularity)
            
            # Apply pagination
            query = query.limit(limit).offset(offset)
            
            # Execute query
            docs = query.stream()
            
            events = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                events.append(data)
            
            return events
        except Exception as e:
            logger.error(f"Failed to list events: {e}")
            raise
    
    # CRUD Operations for Market Data
    def store_market_data(self, market_data: Dict[str, Any]) -> str:
        """Store market data document"""
        try:
            # Create document ID from instrument, granularity, and timestamp
            doc_id = f"{market_data['instrument']}_{market_data['granularity']}_{int(market_data['timestamp'].timestamp())}"
            
            # Store in market_data collection
            doc_ref = self.get_collection('market_data').document(doc_id)
            doc_ref.set(market_data)
            logger.info(f"Stored market data: {doc_id}")
            return doc_id
        except Exception as e:
            logger.error(f"Failed to store market data: {e}")
            raise
    
    def get_market_data(self, 
                       instrument: str,
                       granularity: str,
                       start_time: datetime,
                       end_time: datetime) -> List[Dict[str, Any]]:
        """Get market data for a specific instrument and time range"""
        try:
            query = (self.get_collection('market_data')
                    .where('instrument', '==', instrument)
                    .where('granularity', '==', granularity)
                    .where('timestamp', '>=', start_time)
                    .where('timestamp', '<=', end_time)
                    .order_by('timestamp'))
            
            docs = query.stream()
            
            data = []
            for doc in docs:
                item = doc.to_dict()
                item['id'] = doc.id
                data.append(item)
            
            return data
        except Exception as e:
            logger.error(f"Failed to get market data: {e}")
            raise
    
    # Configuration Management
    def get_configuration(self, config_key: str) -> Optional[Dict[str, Any]]:
        """Get configuration by key"""
        try:
            doc_ref = self.get_collection('configurations').document(config_key)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Failed to get configuration {config_key}: {e}")
            raise
    
    def set_configuration(self, config_key: str, config_data: Dict[str, Any]) -> bool:
        """Set configuration"""
        try:
            config_data['updated_at'] = datetime.utcnow()
            doc_ref = self.get_collection('configurations').document(config_key)
            doc_ref.set(config_data)
            logger.info(f"Set configuration: {config_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to set configuration {config_key}: {e}")
            raise
    
    # Batch Operations
    @contextmanager
    def batch_writer(self):
        """Context manager for batch write operations"""
        batch = self.client.batch()
        try:
            yield batch
            batch.commit()
        except Exception as e:
            logger.error(f"Batch write failed: {e}")
            raise
    
    def batch_create_events(self, events: List[Dict[str, Any]]) -> int:
        """Create multiple events in a batch"""
        try:
            with self.batch_writer() as batch:
                count = 0
                for event_data in events:
                    if 'created_at' not in event_data:
                        event_data['created_at'] = datetime.utcnow()
                    
                    doc_ref = self.get_collection('resistance_events').document()
                    batch.set(doc_ref, event_data)
                    count += 1
            
            logger.info(f"Batch created {count} events")
            return count
        except Exception as e:
            logger.error(f"Failed to batch create events: {e}")
            raise


# Singleton instance
firestore_service = FirestoreService()