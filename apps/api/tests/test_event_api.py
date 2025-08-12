"""
Comprehensive tests for Event Management REST API

Tests all event endpoints, filtering, pagination, statistics, and rate limiting.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4
from typing import List, Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.database import get_db
from app.models.resistance_event import ResistanceEvent
from app.schemas.event_schemas import (
    EventType,
    TimeFrame,
    EventSortField,
    SortOrder
)


# Test client
client = TestClient(app)


# Test fixtures
@pytest.fixture
def sample_event_data():
    """Sample event data for testing"""
    return {
        "event_type": "resistance_bounce",
        "instrument": "EUR_USD",
        "timeframe": "H1",
        "event_timestamp": datetime.utcnow().isoformat(),
        "resistance_level": 1.0850,
        "rebound_amplitude": 0.0020,
        "rebound_percentage": 0.18,
        "green_candle": {
            "open": 1.0820,
            "high": 1.0850,
            "low": 1.0815,
            "close": 1.0845,
            "volume": 1000
        },
        "red_candle": {
            "open": 1.0845,
            "high": 1.0852,
            "low": 1.0830,
            "close": 1.0835,
            "volume": 1200
        },
        "atr_value": 0.0025,
        "rebound_in_atr": 0.8,
        "day_of_week": 1,
        "hour_of_day": 14
    }


@pytest.fixture
def multiple_events_data():
    """Generate multiple events for testing"""
    events = []
    base_time = datetime.utcnow() - timedelta(days=7)
    
    instruments = ["EUR_USD", "GBP_USD", "USD_JPY"]
    timeframes = ["H1", "H4", "D"]
    
    for i in range(30):
        event = {
            "event_type": "resistance_bounce" if i % 2 == 0 else "support_bounce",
            "instrument": instruments[i % 3],
            "timeframe": timeframes[i % 3],
            "event_timestamp": (base_time + timedelta(hours=i * 6)).isoformat(),
            "resistance_level": 1.0800 + (i * 0.0010),
            "rebound_amplitude": 0.0015 + (i * 0.0001),
            "rebound_percentage": 0.10 + (i * 0.01),
            "green_candle": {
                "open": 1.0820,
                "high": 1.0850,
                "low": 1.0815,
                "close": 1.0845,
                "volume": 1000 + i * 100
            },
            "red_candle": {
                "open": 1.0845,
                "high": 1.0852,
                "low": 1.0830,
                "close": 1.0835,
                "volume": 1200 + i * 100
            },
            "day_of_week": i % 7,
            "hour_of_day": i % 24
        }
        events.append(event)
    
    return events


class TestEventCRUD:
    """Test CRUD operations for events"""
    
    def test_create_event(self, sample_event_data):
        """Test creating a new event"""
        response = client.post(
            f"/api/v1/events/",
            json=sample_event_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["event_type"] == sample_event_data["event_type"]
        assert data["instrument"] == sample_event_data["instrument"]
        assert float(data["resistance_level"]) == sample_event_data["resistance_level"]
        assert "id" in data
        assert "detected_at" in data
    
    def test_get_event(self, sample_event_data):
        """Test retrieving an event by ID"""
        # Create event
        create_response = client.post(
            f"/api/v1/events/",
            json=sample_event_data
        )
        event_id = create_response.json()["id"]
        
        # Get event
        response = client.get(f"/api/v1/events/{event_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == event_id
        assert data["instrument"] == sample_event_data["instrument"]
    
    def test_get_nonexistent_event(self):
        """Test retrieving a non-existent event"""
        fake_id = str(uuid4())
        response = client.get(f"/api/v1/events/{fake_id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_update_event(self, sample_event_data):
        """Test updating an event"""
        # Create event
        create_response = client.post(
            f"/api/v1/events/",
            json=sample_event_data
        )
        event_id = create_response.json()["id"]
        
        # Update event
        update_data = {
            "metadata": {"reviewed": True},
            "notes": "Important resistance level",
            "tags": ["significant", "EUR_USD"]
        }
        response = client.put(
            f"/api/v1/events/{event_id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == event_id
        # Note: metadata field update would need to be implemented in the model
    
    def test_delete_event(self, sample_event_data):
        """Test deleting an event"""
        # Create event
        create_response = client.post(
            f"/api/v1/events/",
            json=sample_event_data
        )
        event_id = create_response.json()["id"]
        
        # Delete event
        response = client.delete(f"/api/v1/events/{event_id}")
        assert response.status_code == 204
        
        # Verify deletion
        get_response = client.get(f"/api/v1/events/{event_id}")
        assert get_response.status_code == 404


class TestEventListing:
    """Test event listing and filtering"""
    
    def test_list_events_basic(self, multiple_events_data):
        """Test basic event listing"""
        # Create multiple events
        for event_data in multiple_events_data[:5]:
            client.post(f"/api/v1/events/", json=event_data)
        
        # List events
        response = client.get(f"/api/v1/events/")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "pages" in data
        assert len(data["items"]) <= 50  # Default page size
    
    def test_list_events_pagination(self, multiple_events_data):
        """Test event pagination"""
        # Create events
        for event_data in multiple_events_data[:10]:
            client.post(f"/api/v1/events/", json=event_data)
        
        # Get first page
        response1 = client.get(f"/api/v1/events/?page=1&page_size=5")
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1["items"]) <= 5
        assert data1["page"] == 1
        
        # Get second page
        response2 = client.get(f"/api/v1/events/?page=2&page_size=5")
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["page"] == 2
        
        # Ensure different events
        if data1["items"] and data2["items"]:
            assert data1["items"][0]["id"] != data2["items"][0]["id"]
    
    def test_list_events_sorting(self, multiple_events_data):
        """Test event sorting"""
        # Create events
        for event_data in multiple_events_data[:5]:
            client.post(f"/api/v1/events/", json=event_data)
        
        # Sort by resistance level ascending
        response_asc = client.get(
            f"/api/v1/events/?sort_by=resistance_level&sort_order=asc"
        )
        assert response_asc.status_code == 200
        items_asc = response_asc.json()["items"]
        
        if len(items_asc) > 1:
            assert float(items_asc[0]["resistance_level"]) <= float(items_asc[-1]["resistance_level"])
        
        # Sort by resistance level descending
        response_desc = client.get(
            f"/api/v1/events/?sort_by=resistance_level&sort_order=desc"
        )
        assert response_desc.status_code == 200
        items_desc = response_desc.json()["items"]
        
        if len(items_desc) > 1:
            assert float(items_desc[0]["resistance_level"]) >= float(items_desc[-1]["resistance_level"])
    
    def test_filter_by_instrument(self, multiple_events_data):
        """Test filtering by instrument"""
        # Create events
        for event_data in multiple_events_data[:10]:
            client.post(f"/api/v1/events/", json=event_data)
        
        # Filter by EUR_USD
        response = client.get(f"/api/v1/events/?instrument=EUR_USD")
        assert response.status_code == 200
        items = response.json()["items"]
        
        for item in items:
            assert item["instrument"] == "EUR_USD"
    
    def test_filter_by_date_range(self, multiple_events_data):
        """Test filtering by date range"""
        # Create events
        for event_data in multiple_events_data[:10]:
            client.post(f"/api/v1/events/", json=event_data)
        
        # Filter by date range
        start_date = (datetime.utcnow() - timedelta(days=5)).isoformat()
        end_date = datetime.utcnow().isoformat()
        
        response = client.get(
            f"/api/v1/events/?start_date={start_date}&end_date={end_date}"
        )
        assert response.status_code == 200
        items = response.json()["items"]
        
        for item in items:
            event_time = datetime.fromisoformat(item["event_timestamp"].replace("Z", ""))
            assert event_time >= datetime.fromisoformat(start_date.replace("Z", ""))
            assert event_time <= datetime.fromisoformat(end_date.replace("Z", ""))
    
    def test_filter_by_resistance_level(self):
        """Test filtering by resistance level range"""
        # Create events with different resistance levels
        levels = [1.0800, 1.0850, 1.0900, 1.0950]
        for level in levels:
            event_data = {
                "event_type": "resistance_bounce",
                "instrument": "EUR_USD",
                "timeframe": "H1",
                "event_timestamp": datetime.utcnow().isoformat(),
                "resistance_level": level,
                "rebound_amplitude": 0.0020,
                "rebound_percentage": 0.18,
                "green_candle": {
                    "open": level - 0.0030,
                    "high": level,
                    "low": level - 0.0035,
                    "close": level - 0.0005
                },
                "red_candle": {
                    "open": level - 0.0005,
                    "high": level + 0.0002,
                    "low": level - 0.0020,
                    "close": level - 0.0015
                },
                "day_of_week": 1,
                "hour_of_day": 14
            }
            client.post(f"/api/v1/events/", json=event_data)
        
        # Filter by resistance level range
        response = client.get(
            f"/api/v1/events/?min_resistance_level=1.0840&max_resistance_level=1.0910"
        )
        assert response.status_code == 200
        items = response.json()["items"]
        
        for item in items:
            level = float(item["resistance_level"])
            assert 1.0840 <= level <= 1.0910


class TestBulkOperations:
    """Test bulk event operations"""
    
    def test_bulk_create_events(self, multiple_events_data):
        """Test bulk event creation"""
        bulk_data = {
            "events": multiple_events_data[:5]
        }
        
        response = client.post(f"/api/v1/events/bulk", json=bulk_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["created"] == 5
        assert data["failed"] == 0
        assert len(data["event_ids"]) == 5
    
    def test_bulk_create_with_errors(self, multiple_events_data):
        """Test bulk creation with some invalid events"""
        # Add an invalid event
        invalid_event = multiple_events_data[0].copy()
        del invalid_event["instrument"]  # Remove required field
        
        bulk_data = {
            "events": [invalid_event] + multiple_events_data[1:3]
        }
        
        response = client.post(f"/api/v1/events/bulk", json=bulk_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["created"] == 2
        assert data["failed"] == 1
        assert len(data["errors"]) == 1


class TestEventExport:
    """Test event export functionality"""
    
    def test_export_csv(self, multiple_events_data):
        """Test exporting events as CSV"""
        # Create events
        for event_data in multiple_events_data[:5]:
            client.post(f"/api/v1/events/", json=event_data)
        
        export_request = {
            "format": "csv",
            "include_metadata": False
        }
        
        response = client.post(f"/api/v1/events/export", json=export_request)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv"
        assert "attachment" in response.headers.get("content-disposition", "")
    
    def test_export_json(self, multiple_events_data):
        """Test exporting events as JSON"""
        # Create events
        for event_data in multiple_events_data[:5]:
            client.post(f"/api/v1/events/", json=event_data)
        
        export_request = {
            "format": "json",
            "include_metadata": True
        }
        
        response = client.post(f"/api/v1/events/export", json=export_request)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        # Verify JSON structure
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert "id" in data[0]
            assert "instrument" in data[0]


class TestSpecializedEndpoints:
    """Test specialized event endpoints"""
    
    def test_search_by_resistance_level(self):
        """Test searching events by resistance level"""
        # Create events around specific level
        target_level = 1.0850
        for i in range(5):
            offset = i * 0.0001
            event_data = {
                "event_type": "resistance_bounce",
                "instrument": "EUR_USD",
                "timeframe": "H1",
                "event_timestamp": datetime.utcnow().isoformat(),
                "resistance_level": target_level + offset,
                "rebound_amplitude": 0.0020,
                "rebound_percentage": 0.18,
                "green_candle": {
                    "open": 1.0820,
                    "high": target_level + offset,
                    "low": 1.0815,
                    "close": 1.0845
                },
                "red_candle": {
                    "open": 1.0845,
                    "high": 1.0852,
                    "low": 1.0830,
                    "close": 1.0835
                },
                "day_of_week": 1,
                "hour_of_day": 14
            }
            client.post(f"/api/v1/events/", json=event_data)
        
        # Search with tolerance
        response = client.get(
            f"/api/v1/events/search/by-resistance-level?level={target_level}&tolerance=0.0010"
        )
        
        assert response.status_code == 200
        items = response.json()
        assert len(items) > 0
        
        for item in items:
            level = float(item["resistance_level"])
            assert abs(level - target_level) <= 0.0010
    
    def test_get_recent_events(self, multiple_events_data):
        """Test getting recent events"""
        # Create recent events
        for event_data in multiple_events_data[:5]:
            event_data["event_timestamp"] = datetime.utcnow().isoformat()
            client.post(f"/api/v1/events/", json=event_data)
        
        # Get events from last 24 hours
        response = client.get(f"/api/v1/events/recent?hours=24")
        
        assert response.status_code == 200
        items = response.json()
        assert len(items) > 0
        
        cutoff = datetime.utcnow() - timedelta(hours=24)
        for item in items:
            event_time = datetime.fromisoformat(item["event_timestamp"].replace("Z", ""))
            assert event_time >= cutoff


class TestStatistics:
    """Test statistics endpoints"""
    
    def test_get_statistics_overview(self, multiple_events_data):
        """Test getting statistics overview"""
        # Create events
        for event_data in multiple_events_data[:10]:
            client.post(f"/api/v1/events/", json=event_data)
        
        response = client.get(f"/api/v1/statistics/overview")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_events" in data
        assert "events_by_type" in data
        assert "events_by_instrument" in data
        assert "events_by_timeframe" in data
        assert "avg_rebound_percentage" in data
        assert "top_resistance_levels" in data
    
    def test_get_time_series(self, multiple_events_data):
        """Test getting time series data"""
        # Create events
        for event_data in multiple_events_data[:10]:
            client.post(f"/api/v1/events/", json=event_data)
        
        response = client.get(f"/api/v1/statistics/time-series?interval=day")
        
        assert response.status_code == 200
        data = response.json()
        assert "interval" in data
        assert data["interval"] == "day"
        assert "data" in data
        assert "total_events" in data
        
        if data["data"]:
            point = data["data"][0]
            assert "timestamp" in point
            assert "value" in point
            assert "count" in point
    
    def test_aggregate_events(self):
        """Test custom event aggregation"""
        # Create events
        for i in range(10):
            event_data = {
                "event_type": "resistance_bounce" if i % 2 == 0 else "support_bounce",
                "instrument": "EUR_USD" if i < 5 else "GBP_USD",
                "timeframe": "H1",
                "event_timestamp": datetime.utcnow().isoformat(),
                "resistance_level": 1.0850,
                "rebound_amplitude": 0.0020,
                "rebound_percentage": 0.10 + (i * 0.01),
                "green_candle": {
                    "open": 1.0820,
                    "high": 1.0850,
                    "low": 1.0815,
                    "close": 1.0845
                },
                "red_candle": {
                    "open": 1.0845,
                    "high": 1.0852,
                    "low": 1.0830,
                    "close": 1.0835
                },
                "day_of_week": i % 7,
                "hour_of_day": i % 24
            }
            client.post(f"/api/v1/events/", json=event_data)
        
        aggregation_request = {
            "group_by": ["instrument", "event_type"],
            "metrics": ["count", "avg_rebound"]
        }
        
        response = client.post(f"/api/v1/statistics/aggregate", json=aggregation_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "groups" in data
        assert "total_groups" in data
        assert len(data["groups"]) > 0
        
        group = data["groups"][0]
        assert "instrument" in group
        assert "event_type" in group
        assert "count" in group
        assert "avg_rebound" in group
    
    def test_instrument_statistics(self, multiple_events_data):
        """Test getting statistics for specific instrument"""
        # Create events for EUR_USD
        for event_data in multiple_events_data[:5]:
            event_data["instrument"] = "EUR_USD"
            client.post(f"/api/v1/events/", json=event_data)
        
        response = client.get(f"/api/v1/statistics/by-instrument/EUR_USD")
        
        assert response.status_code == 200
        data = response.json()
        assert data["instrument"] == "EUR_USD"
        assert "total_events" in data
        assert "events_by_timeframe" in data
        assert "daily_trend" in data
    
    def test_compare_instruments(self):
        """Test comparing multiple instruments"""
        # Create events for different instruments
        instruments = ["EUR_USD", "GBP_USD", "USD_JPY"]
        for inst in instruments:
            for i in range(3):
                event_data = {
                    "event_type": "resistance_bounce",
                    "instrument": inst,
                    "timeframe": "H1",
                    "event_timestamp": datetime.utcnow().isoformat(),
                    "resistance_level": 1.0850,
                    "rebound_amplitude": 0.0020,
                    "rebound_percentage": 0.10 + (i * 0.01),
                    "green_candle": {
                        "open": 1.0820,
                        "high": 1.0850,
                        "low": 1.0815,
                        "close": 1.0845
                    },
                    "red_candle": {
                        "open": 1.0845,
                        "high": 1.0852,
                        "low": 1.0830,
                        "close": 1.0835
                    },
                    "day_of_week": 1,
                    "hour_of_day": 14
                }
                client.post(f"/api/v1/events/", json=event_data)
        
        response = client.get(
            f"/api/v1/statistics/compare-instruments?instruments=EUR_USD&instruments=GBP_USD"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "instruments" in data
        assert "EUR_USD" in data["instruments"]
        assert "GBP_USD" in data["instruments"]
        assert "rankings" in data
    
    def test_heatmap_data(self, multiple_events_data):
        """Test getting heatmap data"""
        # Create events
        for event_data in multiple_events_data[:20]:
            client.post(f"/api/v1/events/", json=event_data)
        
        # Test hour/day heatmap
        response = client.get(
            f"/api/v1/statistics/heatmap-data?group_by=hour_day&metric=count"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "hour_day"
        assert "data" in data
        assert len(data["data"]) == 7  # 7 days
        assert len(data["data"][0]) == 24  # 24 hours
        assert "x_labels" in data
        assert "y_labels" in data
    
    def test_health_check(self):
        """Test event service health check"""
        response = client.get(f"/api/v1/statistics/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "total_events" in data
        assert "database_connected" in data
        assert "processing_enabled" in data


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limit_headers(self):
        """Test that rate limit headers are present"""
        response = client.get(f"/api/v1/events/")
        
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
    
    @pytest.mark.skip(reason="Rate limiting test requires Redis and time delays")
    def test_rate_limit_exceeded(self):
        """Test rate limit enforcement"""
        # This test would need to make many rapid requests
        # and verify 429 response when limit is exceeded
        pass


class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_event_data(self):
        """Test creating event with invalid data"""
        invalid_data = {
            "event_type": "invalid_type",  # Invalid enum value
            "instrument": "EUR_USD",
            "timeframe": "H1"
            # Missing required fields
        }
        
        response = client.post(f"/api/v1/events/", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_invalid_filter_parameters(self):
        """Test listing with invalid filter parameters"""
        response = client.get(
            f"/api/v1/events/?day_of_week=8"  # Invalid day (0-6)
        )
        
        # Should handle gracefully or return validation error
        assert response.status_code in [200, 422]
    
    def test_invalid_aggregation(self):
        """Test aggregation with invalid parameters"""
        invalid_aggregation = {
            "group_by": ["invalid_field"],
            "metrics": ["invalid_metric"]
        }
        
        response = client.post(
            f"/api/v1/statistics/aggregate",
            json=invalid_aggregation
        )
        
        assert response.status_code == 422  # Validation error