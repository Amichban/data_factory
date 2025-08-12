"""
Health check endpoint tests.

This module contains comprehensive tests for all health check endpoints
including basic health, detailed health, liveness, and readiness probes.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock


class TestHealthEndpoints:
    """Test suite for health check endpoints."""

    @pytest.mark.asyncio
    async def test_basic_health_check(self, client: AsyncClient):
        """Test the basic health check endpoint."""
        response = await client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "app_name" in data

    @pytest.mark.asyncio
    async def test_detailed_health_check_success(self, client: AsyncClient):
        """Test the detailed health check endpoint with healthy database."""
        with patch('psutil.cpu_percent', return_value=25.5), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk:
            
            # Mock system info
            mock_memory.return_value.total = 8 * 1024**3  # 8GB
            mock_memory.return_value.available = 4 * 1024**3  # 4GB available
            mock_memory.return_value.percent = 50.0
            
            mock_disk.return_value.total = 100 * 1024**3  # 100GB
            mock_disk.return_value.free = 50 * 1024**3  # 50GB free
            mock_disk.return_value.used = 50 * 1024**3  # 50GB used
            
            response = await client.get("/api/v1/health/detailed")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "healthy"
            assert "timestamp" in data
            assert "version" in data
            assert "app_name" in data
            
            # Check environment section
            assert "environment" in data
            assert "debug" in data["environment"]
            assert "testing" in data["environment"]
            
            # Check database section
            assert "database" in data
            assert data["database"]["status"] == "healthy"
            assert "response_time_ms" in data["database"]
            assert data["database"]["response_time_ms"] is not None
            
            # Check system section
            assert "system" in data
            assert data["system"]["cpu_usage_percent"] == 25.5
            assert "memory" in data["system"]
            assert "disk" in data["system"]

    @pytest.mark.asyncio
    async def test_detailed_health_check_db_failure(self, client: AsyncClient):
        """Test the detailed health check when database is unhealthy."""
        # Mock database failure
        with patch('app.routers.health.get_db') as mock_get_db:
            mock_session = AsyncMock()
            mock_session.execute.side_effect = Exception("Database connection failed")
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            with patch('psutil.cpu_percent', return_value=25.5), \
                 patch('psutil.virtual_memory') as mock_memory, \
                 patch('psutil.disk_usage') as mock_disk:
                
                mock_memory.return_value.total = 8 * 1024**3
                mock_memory.return_value.available = 4 * 1024**3
                mock_memory.return_value.percent = 50.0
                
                mock_disk.return_value.total = 100 * 1024**3
                mock_disk.return_value.free = 50 * 1024**3
                mock_disk.return_value.used = 50 * 1024**3
                
                response = await client.get("/api/v1/health/detailed")
                
                assert response.status_code == 503
                data = response.json()["detail"]
                
                assert data["status"] == "degraded"
                assert "unhealthy" in data["database"]["status"]

    @pytest.mark.asyncio
    async def test_liveness_probe(self, client: AsyncClient):
        """Test the liveness probe endpoint."""
        response = await client.get("/api/v1/health/liveness")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "alive"
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_readiness_probe_success(self, client: AsyncClient):
        """Test the readiness probe endpoint when service is ready."""
        response = await client.get("/api/v1/health/readiness")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ready"
        assert "timestamp" in data
        assert "checks" in data
        assert data["checks"]["database"] == "healthy"

    @pytest.mark.asyncio
    async def test_readiness_probe_failure(self, client: AsyncClient):
        """Test the readiness probe when service is not ready."""
        # Mock database failure
        with patch('app.routers.health.get_db') as mock_get_db:
            mock_session = AsyncMock()
            mock_session.execute.side_effect = Exception("Database connection failed")
            mock_get_db.return_value.__aenter__.return_value = mock_session
            
            response = await client.get("/api/v1/health/readiness")
            
            assert response.status_code == 503
            data = response.json()["detail"]
            
            assert data["status"] == "not_ready"
            assert "timestamp" in data
            assert "checks" in data
            assert data["checks"]["database"] == "unhealthy"

    @pytest.mark.asyncio
    async def test_health_endpoints_response_headers(self, client: AsyncClient):
        """Test that health endpoints include proper response headers."""
        response = await client.get("/api/v1/health")
        
        # Should have request ID header from logging middleware
        assert "X-Request-ID" in response.headers
        
        # Should have proper content type
        assert response.headers["content-type"] == "application/json"

    @pytest.mark.asyncio
    async def test_health_check_timing(self, client: AsyncClient):
        """Test that health check endpoints respond quickly."""
        import time
        
        start_time = time.time()
        response = await client.get("/api/v1/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        # Health check should respond within 1 second
        assert response_time < 1.0

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_health_endpoints_integration(self, client: AsyncClient):
        """Integration test for all health endpoints."""
        endpoints = [
            "/api/v1/health",
            "/api/v1/health/liveness",
            "/api/v1/health/readiness"
        ]
        
        for endpoint in endpoints:
            response = await client.get(endpoint)
            assert response.status_code in [200, 503]  # 503 acceptable for readiness
            assert "timestamp" in response.json() or "timestamp" in response.json().get("detail", {})