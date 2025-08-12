"""
Data Ingestion Tasks Module
Background tasks for market data ingestion, processing, and monitoring
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import uuid4

from app.config import settings
from app.models.market_data import (
    DataIngestionRequest, DataIngestionResponse, TimeFrame, DataMode,
    MarketDataCandle, DataQualityMetrics
)
from app.services.market_data_service import market_data_service
from app.services.firestore_service import firestore_service
from app.core.config import (
    MarketDataConstants, ProcessingModes, CollectionNames,
    get_instrument_category, get_quality_rating
)

logger = logging.getLogger(__name__)


class DataIngestionScheduler:
    """Scheduler for automated data ingestion tasks"""
    
    def __init__(self):
        self.running_tasks: Dict[str, Dict[str, Any]] = {}
        self.task_history: List[Dict[str, Any]] = []
        self._shutdown = False
    
    async def schedule_historical_backfill(
        self,
        instruments: List[str],
        timeframes: List[TimeFrame],
        start_date: datetime,
        end_date: datetime,
        priority: int = 1
    ) -> str:
        """Schedule a historical data backfill task"""
        
        task_id = str(uuid4())
        request = DataIngestionRequest(
            instruments=instruments,
            timeframes=timeframes,
            mode=DataMode.BATCH,
            start_date=start_date,
            end_date=end_date,
            validate_data=True,
            force_refresh=False
        )
        
        task_info = {
            'task_id': task_id,
            'type': 'historical_backfill',
            'request': request,
            'priority': priority,
            'status': 'scheduled',
            'created_at': datetime.utcnow(),
            'started_at': None,
            'completed_at': None,
            'progress': 0.0,
            'errors': []
        }
        
        self.running_tasks[task_id] = task_info
        
        # Start task execution in background
        asyncio.create_task(self._execute_ingestion_task(task_id))
        
        logger.info(f"Scheduled historical backfill task {task_id} for {len(instruments)} instruments")
        return task_id
    
    async def schedule_real_time_ingestion(
        self,
        instruments: List[str],
        timeframes: List[TimeFrame]
    ) -> str:
        """Schedule real-time data ingestion task"""
        
        task_id = str(uuid4())
        request = DataIngestionRequest(
            instruments=instruments,
            timeframes=timeframes,
            mode=DataMode.STREAM,
            validate_data=True
        )
        
        task_info = {
            'task_id': task_id,
            'type': 'real_time_ingestion',
            'request': request,
            'priority': 0,  # Highest priority
            'status': 'scheduled',
            'created_at': datetime.utcnow(),
            'started_at': None,
            'completed_at': None,
            'progress': 0.0,
            'errors': []
        }
        
        self.running_tasks[task_id] = task_info
        
        # Start task execution in background
        asyncio.create_task(self._execute_streaming_task(task_id))
        
        logger.info(f"Scheduled real-time ingestion task {task_id}")
        return task_id
    
    async def schedule_data_quality_check(
        self,
        instruments: List[str],
        timeframes: List[TimeFrame]
    ) -> str:
        """Schedule data quality assessment task"""
        
        task_id = str(uuid4())
        
        task_info = {
            'task_id': task_id,
            'type': 'quality_check',
            'instruments': instruments,
            'timeframes': timeframes,
            'priority': 2,
            'status': 'scheduled',
            'created_at': datetime.utcnow(),
            'started_at': None,
            'completed_at': None,
            'progress': 0.0,
            'errors': []
        }
        
        self.running_tasks[task_id] = task_info
        
        # Start task execution in background
        asyncio.create_task(self._execute_quality_check_task(task_id))
        
        logger.info(f"Scheduled quality check task {task_id}")
        return task_id
    
    async def _execute_ingestion_task(self, task_id: str):
        """Execute a data ingestion task"""
        task_info = self.running_tasks.get(task_id)
        if not task_info:
            return
        
        try:
            task_info['status'] = 'running'
            task_info['started_at'] = datetime.utcnow()
            
            # Execute the ingestion request
            response = await market_data_service.process_ingestion_request(task_info['request'])
            
            # Update task status
            task_info['status'] = response.status
            task_info['completed_at'] = datetime.utcnow()
            task_info['progress'] = 100.0
            task_info['response'] = response
            
            # Log task completion
            await self._log_task_completion(task_id, response)
            
            logger.info(f"Completed ingestion task {task_id}: {response.status}")
            
        except Exception as e:
            logger.error(f"Error executing ingestion task {task_id}: {e}")
            task_info['status'] = 'failed'
            task_info['completed_at'] = datetime.utcnow()
            task_info['errors'].append(str(e))
        
        finally:
            # Move to history and cleanup
            self.task_history.append(task_info.copy())
            if len(self.task_history) > 100:  # Keep last 100 tasks
                self.task_history.pop(0)
            del self.running_tasks[task_id]
    
    async def _execute_streaming_task(self, task_id: str):
        """Execute a real-time streaming task"""
        task_info = self.running_tasks.get(task_id)
        if not task_info:
            return
        
        try:
            task_info['status'] = 'running'
            task_info['started_at'] = datetime.utcnow()
            
            # For streaming, we keep the task running
            response = await market_data_service.process_ingestion_request(task_info['request'])
            
            # This would typically run indefinitely for streaming
            task_info['status'] = response.status
            task_info['response'] = response
            
        except Exception as e:
            logger.error(f"Error in streaming task {task_id}: {e}")
            task_info['status'] = 'failed'
            task_info['errors'].append(str(e))
        
        # For streaming tasks, we don't automatically remove them
    
    async def _execute_quality_check_task(self, task_id: str):
        """Execute a data quality check task"""
        task_info = self.running_tasks.get(task_id)
        if not task_info:
            return
        
        try:
            task_info['status'] = 'running'
            task_info['started_at'] = datetime.utcnow()
            
            instruments = task_info['instruments']
            timeframes = task_info['timeframes']
            quality_results = []
            
            total_checks = len(instruments) * len(timeframes)
            completed_checks = 0
            
            for instrument in instruments:
                for timeframe in timeframes:
                    try:
                        metrics = await market_data_service.get_data_quality_metrics(
                            instrument, timeframe
                        )
                        
                        quality_results.append({
                            'instrument': instrument,
                            'timeframe': timeframe.value,
                            'metrics': metrics.dict(),
                            'quality_rating': get_quality_rating(metrics.quality_score)
                        })
                        
                        # Store metrics in Firestore
                        await self._store_quality_metrics(metrics)
                        
                        completed_checks += 1
                        task_info['progress'] = (completed_checks / total_checks) * 100
                        
                    except Exception as e:
                        logger.error(f"Error checking quality for {instrument} {timeframe.value}: {e}")
                        task_info['errors'].append(f"{instrument}_{timeframe.value}: {str(e)}")
            
            task_info['status'] = 'completed'
            task_info['completed_at'] = datetime.utcnow()
            task_info['progress'] = 100.0
            task_info['quality_results'] = quality_results
            
            logger.info(f"Completed quality check task {task_id}")
            
        except Exception as e:
            logger.error(f"Error executing quality check task {task_id}: {e}")
            task_info['status'] = 'failed'
            task_info['errors'].append(str(e))
        
        finally:
            # Move to history
            self.task_history.append(task_info.copy())
            if len(self.task_history) > 100:
                self.task_history.pop(0)
            del self.running_tasks[task_id]
    
    async def _store_quality_metrics(self, metrics: DataQualityMetrics):
        """Store quality metrics in Firestore"""
        try:
            doc_id = f"{metrics.instrument}_{metrics.timeframe.value}_{int(metrics.last_updated.timestamp())}"
            
            metrics_data = {
                'instrument': metrics.instrument,
                'timeframe': metrics.timeframe.value,
                'total_candles': metrics.total_candles,
                'complete_candles': metrics.complete_candles,
                'missing_periods': metrics.missing_periods,
                'duplicate_periods': metrics.duplicate_periods,
                'price_gaps': metrics.price_gaps,
                'volume_anomalies': metrics.volume_anomalies,
                'completeness_ratio': metrics.completeness_ratio,
                'quality_score': metrics.quality_score,
                'quality_rating': get_quality_rating(metrics.quality_score),
                'last_updated': metrics.last_updated
            }
            
            collection_ref = firestore_service.get_collection(CollectionNames.QUALITY_METRICS)
            doc_ref = collection_ref.document(doc_id)
            doc_ref.set(metrics_data)
            
        except Exception as e:
            logger.error(f"Failed to store quality metrics: {e}")
    
    async def _log_task_completion(self, task_id: str, response: DataIngestionResponse):
        """Log task completion to Firestore"""
        try:
            log_data = {
                'task_id': task_id,
                'request_id': response.request_id,
                'status': response.status,
                'message': response.message,
                'instruments_processed': response.instruments_processed,
                'candles_ingested': response.candles_ingested,
                'candles_updated': response.candles_updated,
                'candles_failed': response.candles_failed,
                'processing_time_seconds': response.processing_time_seconds,
                'errors': response.errors,
                'warnings': response.warnings,
                'started_at': response.started_at,
                'completed_at': response.completed_at
            }
            
            collection_ref = firestore_service.get_collection(CollectionNames.INGESTION_LOGS)
            collection_ref.add(log_data)
            
        except Exception as e:
            logger.error(f"Failed to log task completion: {e}")
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        # Check running tasks
        if task_id in self.running_tasks:
            return self.running_tasks[task_id]
        
        # Check history
        for task in self.task_history:
            if task['task_id'] == task_id:
                return task
        
        return None
    
    def get_all_tasks(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all tasks (running and historical)"""
        return {
            'running': list(self.running_tasks.values()),
            'history': self.task_history
        }
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id in self.running_tasks:
            task_info = self.running_tasks[task_id]
            task_info['status'] = 'cancelled'
            task_info['completed_at'] = datetime.utcnow()
            
            # Move to history
            self.task_history.append(task_info.copy())
            del self.running_tasks[task_id]
            
            logger.info(f"Cancelled task {task_id}")
            return True
        
        return False
    
    async def cleanup_old_logs(self, days_to_keep: int = 30):
        """Cleanup old ingestion logs"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Query and delete old logs
            query = (firestore_service.get_collection(CollectionNames.INGESTION_LOGS)
                    .where('completed_at', '<', cutoff_date))
            
            docs = query.stream()
            batch_size = 0
            
            with firestore_service.batch_writer() as batch:
                for doc in docs:
                    batch.delete(doc.reference)
                    batch_size += 1
                    
                    if batch_size >= 500:  # Firestore batch limit
                        break
            
            if batch_size > 0:
                logger.info(f"Cleaned up {batch_size} old ingestion logs")
            
        except Exception as e:
            logger.error(f"Error cleaning up old logs: {e}")
    
    async def shutdown(self):
        """Shutdown the scheduler gracefully"""
        self._shutdown = True
        
        # Wait for running tasks to complete or timeout after 30 seconds
        start_time = datetime.utcnow()
        while self.running_tasks and (datetime.utcnow() - start_time).seconds < 30:
            await asyncio.sleep(1)
        
        # Force cancel remaining tasks
        for task_id in list(self.running_tasks.keys()):
            self.cancel_task(task_id)
        
        logger.info("Data ingestion scheduler shutdown complete")


class AutomaticIngestionManager:
    """Manager for automatic/scheduled data ingestion"""
    
    def __init__(self):
        self.scheduler = DataIngestionScheduler()
        self._running = False
    
    async def start_automatic_ingestion(self):
        """Start automatic data ingestion for all supported instruments"""
        if self._running:
            return
        
        self._running = True
        logger.info("Starting automatic data ingestion")
        
        try:
            # Schedule historical backfill for the last 30 days
            await self._schedule_initial_backfill()
            
            # Schedule real-time ingestion
            await self._schedule_real_time_ingestion()
            
            # Schedule periodic quality checks
            await self._schedule_quality_monitoring()
            
        except Exception as e:
            logger.error(f"Error starting automatic ingestion: {e}")
            self._running = False
            raise
    
    async def _schedule_initial_backfill(self):
        """Schedule initial historical data backfill"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=settings.MAX_HISTORICAL_DAYS)
        
        # Group instruments by priority (majors first)
        major_pairs = [inst for inst in settings.SUPPORTED_INSTRUMENTS 
                      if get_instrument_category(inst) == "major"]
        minor_pairs = [inst for inst in settings.SUPPORTED_INSTRUMENTS 
                      if get_instrument_category(inst) == "minor"]
        exotic_pairs = [inst for inst in settings.SUPPORTED_INSTRUMENTS 
                       if get_instrument_category(inst) == "exotic"]
        
        timeframes = [TimeFrame(tf) for tf in settings.SUPPORTED_TIMEFRAMES]
        
        # Schedule major pairs first (highest priority)
        if major_pairs:
            await self.scheduler.schedule_historical_backfill(
                instruments=major_pairs,
                timeframes=timeframes,
                start_date=start_date,
                end_date=end_date,
                priority=1
            )
        
        # Schedule minor pairs
        if minor_pairs:
            await self.scheduler.schedule_historical_backfill(
                instruments=minor_pairs,
                timeframes=timeframes,
                start_date=start_date,
                end_date=end_date,
                priority=2
            )
        
        # Schedule exotic pairs
        if exotic_pairs:
            await self.scheduler.schedule_historical_backfill(
                instruments=exotic_pairs,
                timeframes=timeframes,
                start_date=start_date,
                end_date=end_date,
                priority=3
            )
    
    async def _schedule_real_time_ingestion(self):
        """Schedule real-time data ingestion"""
        # Start with major pairs for real-time
        major_pairs = [inst for inst in settings.SUPPORTED_INSTRUMENTS 
                      if get_instrument_category(inst) == "major"]
        
        if major_pairs:
            timeframes = [TimeFrame.H1]  # Start with H1 for real-time
            await self.scheduler.schedule_real_time_ingestion(
                instruments=major_pairs,
                timeframes=timeframes
            )
    
    async def _schedule_quality_monitoring(self):
        """Schedule periodic data quality monitoring"""
        await self.scheduler.schedule_data_quality_check(
            instruments=settings.SUPPORTED_INSTRUMENTS[:10],  # Check first 10 instruments
            timeframes=[TimeFrame(tf) for tf in settings.SUPPORTED_TIMEFRAMES]
        )
    
    async def stop_automatic_ingestion(self):
        """Stop automatic data ingestion"""
        self._running = False
        await self.scheduler.shutdown()
        logger.info("Stopped automatic data ingestion")
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of automatic ingestion"""
        return {
            'running': self._running,
            'tasks': self.scheduler.get_all_tasks(),
            'last_check': datetime.utcnow().isoformat()
        }


# Global instances
ingestion_scheduler = DataIngestionScheduler()
automatic_ingestion_manager = AutomaticIngestionManager()