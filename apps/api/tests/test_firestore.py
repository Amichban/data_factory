"""
Unit tests for Firestore Service
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from google.cloud import firestore

from app.services.firestore_service import FirestoreService, firestore_service
from app.models.events import ResistanceEvent, EventType, Granularity


class TestFirestoreService:
    """Test suite for FirestoreService"""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Firestore client"""
        with patch('app.services.firestore_service.firestore.Client') as mock:
            yield mock
    
    @pytest.fixture
    def service(self, mock_client):
        """Create a FirestoreService instance with mocked client"""
        # Reset singleton
        FirestoreService._instance = None
        FirestoreService._client = None
        
        # Create service
        service = FirestoreService()
        service._client = mock_client.return_value
        return service
    
    def test_singleton_pattern(self):
        """Test that FirestoreService follows singleton pattern"""
        service1 = FirestoreService()
        service2 = FirestoreService()
        assert service1 is service2
    
    def test_health_check_success(self, service, mock_client):
        """Test successful health check"""
        # Mock collections
        mock_collection = Mock()
        mock_client.return_value.collections.return_value = [mock_collection]
        
        result = service.health_check()
        
        assert result["status"] == "healthy"
        assert result["connected"] is True
        assert result["collections_accessible"] is True
    
    def test_health_check_failure(self, service, mock_client):
        """Test health check when Firestore is not accessible"""
        mock_client.return_value.collections.side_effect = Exception("Connection failed")
        
        result = service.health_check()
        
        assert result["status"] == "unhealthy"
        assert result["connected"] is False
        assert "error" in result
    
    def test_create_event(self, service, mock_client):
        """Test creating a resistance event"""
        # Mock collection and document
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc_ref.id = "test_event_id"
        mock_collection.add.return_value = (None, mock_doc_ref)
        mock_client.return_value.collection.return_value = mock_collection
        
        event_data = {
            "instrument": "EUR_USD",
            "granularity": "H1",
            "event_type": "new_resistance",
            "event_price_level": 1.0850
        }
        
        result = service.create_event(event_data)
        
        assert result == "test_event_id"
        mock_collection.add.assert_called_once()
        # Check that created_at was added
        call_args = mock_collection.add.call_args[0][0]
        assert "created_at" in call_args
    
    def test_get_event_exists(self, service, mock_client):
        """Test getting an existing event"""
        # Mock document
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.id = "test_event_id"
        mock_doc.to_dict.return_value = {
            "instrument": "EUR_USD",
            "granularity": "H1"
        }
        
        mock_doc_ref = Mock()
        mock_doc_ref.get.return_value = mock_doc
        
        mock_collection = Mock()
        mock_collection.document.return_value = mock_doc_ref
        mock_client.return_value.collection.return_value = mock_collection
        
        result = service.get_event("test_event_id")
        
        assert result is not None
        assert result["id"] == "test_event_id"
        assert result["instrument"] == "EUR_USD"
    
    def test_get_event_not_exists(self, service, mock_client):
        """Test getting a non-existent event"""
        # Mock document
        mock_doc = Mock()
        mock_doc.exists = False
        
        mock_doc_ref = Mock()
        mock_doc_ref.get.return_value = mock_doc
        
        mock_collection = Mock()
        mock_collection.document.return_value = mock_doc_ref
        mock_client.return_value.collection.return_value = mock_collection
        
        result = service.get_event("non_existent_id")
        
        assert result is None
    
    def test_update_event(self, service, mock_client):
        """Test updating an event"""
        mock_doc_ref = Mock()
        mock_collection = Mock()
        mock_collection.document.return_value = mock_doc_ref
        mock_client.return_value.collection.return_value = mock_collection
        
        update_data = {"status": "processed"}
        result = service.update_event("test_event_id", update_data)
        
        assert result is True
        mock_doc_ref.update.assert_called_once()
        # Check that updated_at was added
        call_args = mock_doc_ref.update.call_args[0][0]
        assert "updated_at" in call_args
    
    def test_delete_event(self, service, mock_client):
        """Test deleting an event"""
        mock_doc_ref = Mock()
        mock_collection = Mock()
        mock_collection.document.return_value = mock_doc_ref
        mock_client.return_value.collection.return_value = mock_collection
        
        result = service.delete_event("test_event_id")
        
        assert result is True
        mock_doc_ref.delete.assert_called_once()
    
    def test_list_events_with_filters(self, service, mock_client):
        """Test listing events with filters"""
        # Mock query chain
        mock_query = Mock()
        mock_query.where.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        
        # Mock documents
        mock_doc1 = Mock()
        mock_doc1.id = "event1"
        mock_doc1.to_dict.return_value = {"instrument": "EUR_USD"}
        
        mock_doc2 = Mock()
        mock_doc2.id = "event2"
        mock_doc2.to_dict.return_value = {"instrument": "EUR_USD"}
        
        mock_query.stream.return_value = [mock_doc1, mock_doc2]
        
        mock_collection = Mock()
        mock_collection.where.return_value = mock_query
        mock_client.return_value.collection.return_value = mock_collection
        
        result = service.list_events(instrument="EUR_USD", granularity="H1", limit=10)
        
        assert len(result) == 2
        assert result[0]["id"] == "event1"
        assert result[1]["id"] == "event2"
        mock_collection.where.assert_called()
    
    def test_batch_create_events(self, service, mock_client):
        """Test batch creation of events"""
        mock_batch = Mock()
        mock_client.return_value.batch.return_value = mock_batch
        
        mock_doc_ref = Mock()
        mock_collection = Mock()
        mock_collection.document.return_value = mock_doc_ref
        mock_client.return_value.collection.return_value = mock_collection
        
        events = [
            {"instrument": "EUR_USD", "granularity": "H1"},
            {"instrument": "GBP_USD", "granularity": "H1"},
            {"instrument": "USD_JPY", "granularity": "H1"}
        ]
        
        result = service.batch_create_events(events)
        
        assert result == 3
        assert mock_batch.set.call_count == 3
        mock_batch.commit.assert_called_once()
    
    def test_store_market_data(self, service, mock_client):
        """Test storing market data"""
        mock_doc_ref = Mock()
        mock_collection = Mock()
        mock_collection.document.return_value = mock_doc_ref
        mock_client.return_value.collection.return_value = mock_collection
        
        market_data = {
            "instrument": "EUR_USD",
            "granularity": "H1",
            "timestamp": datetime.utcnow(),
            "candle": {
                "open": 1.0850,
                "high": 1.0860,
                "low": 1.0840,
                "close": 1.0855,
                "volume": 1000
            }
        }
        
        result = service.store_market_data(market_data)
        
        assert result.startswith("EUR_USD_H1_")
        mock_doc_ref.set.assert_called_once_with(market_data)
    
    def test_get_configuration(self, service, mock_client):
        """Test getting configuration"""
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"feature_flags": {"firestore_enabled": True}}
        
        mock_doc_ref = Mock()
        mock_doc_ref.get.return_value = mock_doc
        
        mock_collection = Mock()
        mock_collection.document.return_value = mock_doc_ref
        mock_client.return_value.collection.return_value = mock_collection
        
        result = service.get_configuration("system_config")
        
        assert result is not None
        assert result["feature_flags"]["firestore_enabled"] is True
    
    def test_set_configuration(self, service, mock_client):
        """Test setting configuration"""
        mock_doc_ref = Mock()
        mock_collection = Mock()
        mock_collection.document.return_value = mock_doc_ref
        mock_client.return_value.collection.return_value = mock_collection
        
        config_data = {"feature_flags": {"new_feature": True}}
        result = service.set_configuration("system_config", config_data)
        
        assert result is True
        mock_doc_ref.set.assert_called_once()
        # Check that updated_at was added
        call_args = mock_doc_ref.set.call_args[0][0]
        assert "updated_at" in call_args


class TestResistanceEventModel:
    """Test suite for ResistanceEvent model"""
    
    def test_valid_resistance_event(self):
        """Test creating a valid resistance event"""
        event = ResistanceEvent(
            original_event_id="test_123",
            event_creation_date=datetime.utcnow(),
            granularity=Granularity.H1,
            instrument="EUR_USD",
            event_price_level=1.0850,
            atr_at_event=0.0010,
            volume_at_event=1000,
            new_resistance_negative_rebound=-0.0005,
            new_resistance_negative_rebound_in_atr=-0.5,
            day_of_week=1,
            hours_of_day=14
        )
        
        assert event.event_type == EventType.NEW_RESISTANCE
        assert event.instrument == "EUR_USD"
    
    def test_invalid_positive_rebound(self):
        """Test that positive rebound values are rejected"""
        with pytest.raises(ValueError, match="should be negative"):
            ResistanceEvent(
                original_event_id="test_123",
                event_creation_date=datetime.utcnow(),
                granularity=Granularity.H1,
                instrument="EUR_USD",
                event_price_level=1.0850,
                atr_at_event=0.0010,
                volume_at_event=1000,
                new_resistance_negative_rebound=0.0005,  # Positive value
                new_resistance_negative_rebound_in_atr=-0.5,
                day_of_week=1,
                hours_of_day=14
            )