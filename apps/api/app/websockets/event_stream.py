"""
WebSocket Event Stream for Real-time Notifications

Provides WebSocket endpoints for streaming resistance events to clients.
"""

from typing import Dict, Set, Any, Optional
from datetime import datetime
import asyncio
import json
import structlog
from fastapi import WebSocket, WebSocketDisconnect, Query, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings
from app.services.spike_processor import get_spike_processor

logger = structlog.get_logger(__name__)

# Security for WebSocket connections
security = HTTPBearer(auto_error=False)


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasting.
    """
    
    def __init__(self):
        # Store active connections by client ID
        self.active_connections: Dict[str, WebSocket] = {}
        # Store subscriptions (instrument/timeframe) per client
        self.subscriptions: Dict[str, Set[str]] = {}
        # Connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    async def connect(
        self,
        websocket: WebSocket,
        client_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            client_id: Unique client identifier
            metadata: Optional connection metadata
        """
        await websocket.accept()
        
        async with self._lock:
            self.active_connections[client_id] = websocket
            self.subscriptions[client_id] = set()
            self.connection_metadata[client_id] = metadata or {}
            self.connection_metadata[client_id]['connected_at'] = datetime.utcnow()
        
        logger.info(
            "WebSocket client connected",
            client_id=client_id,
            total_connections=len(self.active_connections)
        )
        
        # Send welcome message
        await self.send_personal_message(
            {
                'type': 'connection',
                'status': 'connected',
                'client_id': client_id,
                'timestamp': datetime.utcnow().isoformat()
            },
            client_id
        )
    
    async def disconnect(self, client_id: str):
        """
        Remove a WebSocket connection.
        
        Args:
            client_id: Client identifier
        """
        async with self._lock:
            if client_id in self.active_connections:
                del self.active_connections[client_id]
            if client_id in self.subscriptions:
                del self.subscriptions[client_id]
            if client_id in self.connection_metadata:
                del self.connection_metadata[client_id]
        
        logger.info(
            "WebSocket client disconnected",
            client_id=client_id,
            remaining_connections=len(self.active_connections)
        )
    
    async def subscribe(
        self,
        client_id: str,
        instrument: str,
        timeframe: str
    ):
        """
        Subscribe client to specific instrument/timeframe events.
        
        Args:
            client_id: Client identifier
            instrument: Trading instrument
            timeframe: Data timeframe
        """
        subscription_key = f"{instrument}_{timeframe}"
        
        async with self._lock:
            if client_id in self.subscriptions:
                self.subscriptions[client_id].add(subscription_key)
        
        logger.debug(
            "Client subscribed",
            client_id=client_id,
            subscription=subscription_key
        )
        
        # Send confirmation
        await self.send_personal_message(
            {
                'type': 'subscription',
                'action': 'subscribed',
                'instrument': instrument,
                'timeframe': timeframe,
                'timestamp': datetime.utcnow().isoformat()
            },
            client_id
        )
    
    async def unsubscribe(
        self,
        client_id: str,
        instrument: str,
        timeframe: str
    ):
        """
        Unsubscribe client from specific instrument/timeframe events.
        
        Args:
            client_id: Client identifier
            instrument: Trading instrument
            timeframe: Data timeframe
        """
        subscription_key = f"{instrument}_{timeframe}"
        
        async with self._lock:
            if client_id in self.subscriptions:
                self.subscriptions[client_id].discard(subscription_key)
        
        logger.debug(
            "Client unsubscribed",
            client_id=client_id,
            subscription=subscription_key
        )
        
        # Send confirmation
        await self.send_personal_message(
            {
                'type': 'subscription',
                'action': 'unsubscribed',
                'instrument': instrument,
                'timeframe': timeframe,
                'timestamp': datetime.utcnow().isoformat()
            },
            client_id
        )
    
    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        """
        Send message to a specific client.
        
        Args:
            message: Message data
            client_id: Client identifier
        """
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(
                    "Failed to send message to client",
                    client_id=client_id,
                    error=str(e)
                )
                await self.disconnect(client_id)
    
    async def broadcast_event(
        self,
        event: Dict[str, Any],
        instrument: str,
        timeframe: str
    ):
        """
        Broadcast event to all subscribed clients.
        
        Args:
            event: Event data
            instrument: Trading instrument
            timeframe: Data timeframe
        """
        subscription_key = f"{instrument}_{timeframe}"
        disconnected_clients = []
        
        # Find subscribed clients
        for client_id, subscriptions in self.subscriptions.items():
            if subscription_key in subscriptions or '*' in subscriptions:
                websocket = self.active_connections.get(client_id)
                
                if websocket:
                    try:
                        await websocket.send_json({
                            'type': 'event',
                            'data': event,
                            'instrument': instrument,
                            'timeframe': timeframe,
                            'timestamp': datetime.utcnow().isoformat()
                        })
                    except Exception as e:
                        logger.error(
                            "Failed to broadcast to client",
                            client_id=client_id,
                            error=str(e)
                        )
                        disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            await self.disconnect(client_id)
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """
        Broadcast message to all connected clients.
        
        Args:
            message: Message data
        """
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(
                    "Failed to broadcast to client",
                    client_id=client_id,
                    error=str(e)
                )
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            await self.disconnect(client_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        total_subscriptions = sum(
            len(subs) for subs in self.subscriptions.values()
        )
        
        return {
            'total_connections': len(self.active_connections),
            'total_subscriptions': total_subscriptions,
            'clients': [
                {
                    'client_id': client_id,
                    'subscriptions': list(self.subscriptions.get(client_id, set())),
                    'connected_at': self.connection_metadata.get(client_id, {}).get(
                        'connected_at', ''
                    )
                }
                for client_id in self.active_connections.keys()
            ]
        }


# Global connection manager
manager = ConnectionManager()


async def verify_token(credentials: Optional[HTTPAuthorizationCredentials]) -> bool:
    """
    Verify authentication token for WebSocket connection.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        True if authenticated, False otherwise
    """
    # Simple token verification - implement proper authentication
    if not credentials:
        return False
    
    # For now, just check if token is provided
    # In production, verify against your auth system
    return bool(credentials.credentials)


async def websocket_endpoint(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None),
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time event streaming.
    
    Args:
        websocket: WebSocket connection
        client_id: Optional client identifier
        token: Optional authentication token
    """
    # Generate client ID if not provided
    if not client_id:
        import uuid
        client_id = str(uuid.uuid4())
    
    # Simple authentication check (improve for production)
    # if token != "valid_token":  # Replace with proper auth
    #     await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    #     return
    
    try:
        # Connect client
        await manager.connect(websocket, client_id)
        
        # Set up event notification callback
        async def notification_callback(notification: Dict[str, Any]):
            """Callback for spike processor notifications"""
            if notification.get('type') == 'resistance_event':
                event_data = notification.get('data', {})
                await manager.broadcast_event(
                    event=event_data,
                    instrument=event_data.get('instrument', ''),
                    timeframe=event_data.get('timeframe', '')
                )
        
        # Get spike processor and set callback
        spike_processor = await get_spike_processor(
            notification_callback=notification_callback
        )
        
        # Process incoming messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_json()
                
                message_type = data.get('type')
                
                if message_type == 'subscribe':
                    # Handle subscription request
                    instrument = data.get('instrument')
                    timeframe = data.get('timeframe')
                    
                    if instrument and timeframe:
                        await manager.subscribe(client_id, instrument, timeframe)
                    elif instrument == '*':
                        # Subscribe to all events
                        await manager.subscribe(client_id, '*', '*')
                
                elif message_type == 'unsubscribe':
                    # Handle unsubscription request
                    instrument = data.get('instrument')
                    timeframe = data.get('timeframe')
                    
                    if instrument and timeframe:
                        await manager.unsubscribe(client_id, instrument, timeframe)
                
                elif message_type == 'ping':
                    # Handle ping/pong for connection keep-alive
                    await manager.send_personal_message(
                        {'type': 'pong', 'timestamp': datetime.utcnow().isoformat()},
                        client_id
                    )
                
                elif message_type == 'status':
                    # Send status information
                    processor_status = spike_processor.get_status()
                    await manager.send_personal_message(
                        {
                            'type': 'status',
                            'processor': processor_status,
                            'connections': manager.get_stats(),
                            'timestamp': datetime.utcnow().isoformat()
                        },
                        client_id
                    )
                
                else:
                    # Unknown message type
                    await manager.send_personal_message(
                        {
                            'type': 'error',
                            'message': f'Unknown message type: {message_type}',
                            'timestamp': datetime.utcnow().isoformat()
                        },
                        client_id
                    )
            
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    {
                        'type': 'error',
                        'message': 'Invalid JSON format',
                        'timestamp': datetime.utcnow().isoformat()
                    },
                    client_id
                )
            except Exception as e:
                logger.error(
                    "Error processing WebSocket message",
                    client_id=client_id,
                    error=str(e),
                    exc_info=True
                )
                await manager.send_personal_message(
                    {
                        'type': 'error',
                        'message': 'Internal server error',
                        'timestamp': datetime.utcnow().isoformat()
                    },
                    client_id
                )
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for client {client_id}")
    except Exception as e:
        logger.error(
            "WebSocket error",
            client_id=client_id,
            error=str(e),
            exc_info=True
        )
    finally:
        await manager.disconnect(client_id)


async def broadcast_system_message(message: str, level: str = "info"):
    """
    Broadcast system message to all connected clients.
    
    Args:
        message: System message
        level: Message level (info, warning, error)
    """
    await manager.broadcast_to_all({
        'type': 'system',
        'level': level,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    })


def get_connection_stats() -> Dict[str, Any]:
    """Get current connection statistics"""
    return manager.get_stats()