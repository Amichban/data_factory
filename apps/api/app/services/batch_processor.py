"""
Batch Processing Service

High-performance batch processor for historical data analysis and bulk event generation.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import structlog
import uuid
import time

from app.models.batch_job import BatchJob, JobStatus, JobType, BatchJobLog
from app.models.market_data import MarketDataCandle, TimeFrame
from app.models.resistance_event import ResistanceEvent
from app.services.event_processor import EventProcessor
from app.services.market_data_service import MarketDataService
from app.core.queue import JobQueue, QueuePriority, get_job_queue
from app.database import AsyncSessionLocal
from app.config import settings

logger = structlog.get_logger(__name__)


class BatchProcessor:
    """
    High-performance batch processing engine for historical data analysis.
    Supports parallel processing, progress tracking, and resumable execution.
    """
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        """
        Initialize the batch processor.
        
        Args:
            db_session: Optional database session
        """
        self.db_session = db_session
        self.event_processor = EventProcessor(db_session)
        self.market_data_service = MarketDataService()
        self.job_queue = get_job_queue()
        self._active_jobs: Dict[str, BatchJob] = {}
        
    async def create_batch_job(
        self,
        job_type: JobType,
        instruments: List[str],
        timeframes: List[str],
        start_date: datetime,
        end_date: datetime,
        batch_size: int = 500,
        concurrency_limit: int = 4,
        priority: int = 5
    ) -> BatchJob:
        """
        Create a new batch processing job.
        
        Args:
            job_type: Type of batch job
            instruments: List of instruments to process
            timeframes: List of timeframes to process
            start_date: Start date for processing
            end_date: End date for processing
            batch_size: Number of items per batch
            concurrency_limit: Maximum concurrent tasks
            priority: Job priority (1-10)
            
        Returns:
            Created BatchJob instance
        """
        # Check feature flag
        if not settings.FEATURE_FLAGS.get('batch_processing_enabled', False):
            raise ValueError("Batch processing is disabled via feature flag")
        
        # Calculate total items to process
        total_items = self._calculate_total_items(
            instruments, timeframes, start_date, end_date
        )
        
        # Create job record
        job = BatchJob(
            job_type=job_type,
            status=JobStatus.PENDING,
            instruments=instruments,
            timeframes=timeframes,
            start_date=start_date,
            end_date=end_date,
            batch_size=batch_size,
            concurrency_limit=concurrency_limit,
            priority=priority,
            total_items=total_items
        )
        
        # Save to database
        async with self._get_session() as session:
            session.add(job)
            await session.commit()
            await session.refresh(job)
        
        logger.info(
            "Batch job created",
            job_id=str(job.id),
            job_type=job_type.value,
            total_items=total_items,
            instruments_count=len(instruments),
            timeframes_count=len(timeframes)
        )
        
        return job
    
    async def start_job(
        self,
        job_id: str,
        resume_from_checkpoint: bool = False
    ) -> Dict[str, Any]:
        """
        Start or resume a batch processing job.
        
        Args:
            job_id: Job identifier
            resume_from_checkpoint: Whether to resume from last checkpoint
            
        Returns:
            Job execution result
        """
        start_time = datetime.utcnow()
        
        # Load job from database
        async with self._get_session() as session:
            result = await session.execute(
                select(BatchJob).where(BatchJob.id == uuid.UUID(job_id))
            )
            job = result.scalar_one_or_none()
            
            if not job:
                raise ValueError(f"Job {job_id} not found")
            
            # Check if job can be started
            if job.status == JobStatus.RUNNING:
                raise ValueError(f"Job {job_id} is already running")
            
            if job.status == JobStatus.COMPLETED:
                raise ValueError(f"Job {job_id} is already completed")
            
            # Update job status
            job.status = JobStatus.RUNNING
            job.started_at = start_time
            
            if not resume_from_checkpoint:
                # Reset progress if not resuming
                job.processed_items = 0
                job.failed_items = 0
                job.progress_percentage = 0.0
                job.checkpoint_data = None
            
            await session.commit()
        
        # Store in active jobs
        self._active_jobs[job_id] = job
        
        try:
            # Check for parallel processing
            if settings.FEATURE_FLAGS.get('parallel_processing', False):
                result = await self._process_job_parallel(job, resume_from_checkpoint)
            else:
                result = await self._process_job_sequential(job, resume_from_checkpoint)
            
            # Update job completion
            async with self._get_session() as session:
                await session.execute(
                    update(BatchJob)
                    .where(BatchJob.id == job.id)
                    .values(
                        status=JobStatus.COMPLETED,
                        completed_at=datetime.utcnow(),
                        processing_time_seconds=(datetime.utcnow() - start_time).total_seconds(),
                        items_per_second=job.processed_items / max((datetime.utcnow() - start_time).total_seconds(), 1)
                    )
                )
                await session.commit()
            
            logger.info(
                "Batch job completed",
                job_id=job_id,
                processed_items=job.processed_items,
                failed_items=job.failed_items,
                processing_time=(datetime.utcnow() - start_time).total_seconds()
            )
            
            return result
            
        except Exception as e:
            # Update job as failed
            async with self._get_session() as session:
                await session.execute(
                    update(BatchJob)
                    .where(BatchJob.id == job.id)
                    .values(
                        status=JobStatus.FAILED,
                        error_message=str(e),
                        error_count=job.error_count + 1
                    )
                )
                await session.commit()
            
            logger.error(
                "Batch job failed",
                job_id=job_id,
                error=str(e),
                exc_info=True
            )
            
            raise
        
        finally:
            # Remove from active jobs
            if job_id in self._active_jobs:
                del self._active_jobs[job_id]
    
    async def _process_job_parallel(
        self,
        job: BatchJob,
        resume_from_checkpoint: bool
    ) -> Dict[str, Any]:
        """
        Process job using parallel execution.
        
        Args:
            job: Batch job to process
            resume_from_checkpoint: Whether to resume from checkpoint
            
        Returns:
            Processing results
        """
        logger.info(
            "Starting parallel batch processing",
            job_id=str(job.id),
            concurrency_limit=job.concurrency_limit
        )
        
        # Generate work items
        work_items = self._generate_work_items(job, resume_from_checkpoint)
        
        # Create tasks for parallel execution
        tasks = []
        results = {
            'events_detected': 0,
            'events_stored': 0,
            'candles_processed': 0,
            'errors': []
        }
        
        # Process in batches respecting concurrency limit
        for i in range(0, len(work_items), job.concurrency_limit):
            batch = work_items[i:i + job.concurrency_limit]
            batch_tasks = []
            
            for item in batch:
                # Add to queue
                task_id = f"{job.id}-{item['instrument']}-{item['timeframe']}-{i}"
                
                await self.job_queue.add_task(
                    task_id=task_id,
                    job_id=str(job.id),
                    payload=item,
                    priority=job.priority,
                    execute_func=lambda p: self._process_work_item(job, p)
                )
                
                batch_tasks.append(task_id)
            
            # Wait for batch to complete
            for task_id in batch_tasks:
                try:
                    result = await self.job_queue.wait_for_task(task_id, timeout=300)
                    
                    # Aggregate results
                    results['events_detected'] += result.get('events_detected', 0)
                    results['events_stored'] += result.get('events_stored', 0)
                    results['candles_processed'] += result.get('candles_processed', 0)
                    
                    # Update progress
                    await self._update_job_progress(job, 1, 0)
                    
                except Exception as e:
                    logger.error(
                        "Work item failed",
                        job_id=str(job.id),
                        task_id=task_id,
                        error=str(e)
                    )
                    results['errors'].append(str(e))
                    await self._update_job_progress(job, 0, 1)
        
        # Update job results
        async with self._get_session() as session:
            await session.execute(
                update(BatchJob)
                .where(BatchJob.id == job.id)
                .values(
                    events_detected=results['events_detected'],
                    events_stored=results['events_stored']
                )
            )
            await session.commit()
        
        return results
    
    async def _process_job_sequential(
        self,
        job: BatchJob,
        resume_from_checkpoint: bool
    ) -> Dict[str, Any]:
        """
        Process job using sequential execution.
        
        Args:
            job: Batch job to process
            resume_from_checkpoint: Whether to resume from checkpoint
            
        Returns:
            Processing results
        """
        logger.info(
            "Starting sequential batch processing",
            job_id=str(job.id)
        )
        
        # Generate work items
        work_items = self._generate_work_items(job, resume_from_checkpoint)
        
        results = {
            'events_detected': 0,
            'events_stored': 0,
            'candles_processed': 0,
            'errors': []
        }
        
        for item in work_items:
            try:
                # Process work item
                item_result = await self._process_work_item(job, item)
                
                # Aggregate results
                results['events_detected'] += item_result.get('events_detected', 0)
                results['events_stored'] += item_result.get('events_stored', 0)
                results['candles_processed'] += item_result.get('candles_processed', 0)
                
                # Update progress and checkpoint
                await self._update_job_progress(job, 1, 0)
                await self._save_checkpoint(job, item)
                
            except Exception as e:
                logger.error(
                    "Work item failed",
                    job_id=str(job.id),
                    instrument=item.get('instrument'),
                    timeframe=item.get('timeframe'),
                    error=str(e)
                )
                results['errors'].append(str(e))
                await self._update_job_progress(job, 0, 1)
        
        # Update job results
        async with self._get_session() as session:
            await session.execute(
                update(BatchJob)
                .where(BatchJob.id == job.id)
                .values(
                    events_detected=results['events_detected'],
                    events_stored=results['events_stored']
                )
            )
            await session.commit()
        
        return results
    
    async def _process_work_item(
        self,
        job: BatchJob,
        work_item: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a single work item (instrument + timeframe + date range).
        
        Args:
            job: Parent batch job
            work_item: Work item containing processing parameters
            
        Returns:
            Processing results
        """
        start_time = time.time()
        
        instrument = work_item['instrument']
        timeframe = TimeFrame(work_item['timeframe'])
        start_date = work_item['start_date']
        end_date = work_item['end_date']
        
        logger.debug(
            "Processing work item",
            job_id=str(job.id),
            instrument=instrument,
            timeframe=timeframe.value,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        try:
            # Fetch market data
            candles = await self.market_data_service.fetch_historical_data(
                instrument=instrument,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date,
                batch_size=job.batch_size
            )
            
            if not candles:
                logger.warning(
                    "No candles fetched",
                    instrument=instrument,
                    timeframe=timeframe.value
                )
                return {
                    'events_detected': 0,
                    'events_stored': 0,
                    'candles_processed': 0
                }
            
            # Process candles for resistance events
            if job.job_type == JobType.RESISTANCE_DETECTION:
                result = await self.event_processor.process_market_data_batch(
                    candles=candles,
                    instrument=instrument,
                    timeframe=timeframe
                )
                
                processing_time = time.time() - start_time
                
                # Log metrics
                await self._log_job_metrics(
                    job_id=str(job.id),
                    instrument=instrument,
                    timeframe=timeframe.value,
                    candles_processed=len(candles),
                    events_detected=result.get('events_detected', 0),
                    processing_time=processing_time
                )
                
                return {
                    'events_detected': result.get('events_detected', 0),
                    'events_stored': result.get('events_stored', 0),
                    'candles_processed': len(candles),
                    'processing_time': processing_time
                }
            
            else:
                # Other job types can be implemented here
                return {
                    'events_detected': 0,
                    'events_stored': 0,
                    'candles_processed': len(candles)
                }
                
        except Exception as e:
            logger.error(
                "Error processing work item",
                job_id=str(job.id),
                instrument=instrument,
                timeframe=timeframe.value,
                error=str(e),
                exc_info=True
            )
            raise
    
    def _generate_work_items(
        self,
        job: BatchJob,
        resume_from_checkpoint: bool
    ) -> List[Dict[str, Any]]:
        """
        Generate work items for batch processing.
        
        Args:
            job: Batch job
            resume_from_checkpoint: Whether to resume from checkpoint
            
        Returns:
            List of work items
        """
        work_items = []
        
        # Determine starting point
        if resume_from_checkpoint and job.checkpoint_data:
            # Resume from checkpoint
            start_instrument = job.checkpoint_data.get('last_instrument')
            start_timeframe = job.checkpoint_data.get('last_timeframe')
            start_date = datetime.fromisoformat(job.checkpoint_data.get('last_date'))
            
            # Filter to resume from checkpoint
            instruments = job.instruments[job.instruments.index(start_instrument):]
            timeframes = job.timeframes[job.timeframes.index(start_timeframe):]
        else:
            instruments = job.instruments
            timeframes = job.timeframes
            start_date = job.start_date
        
        # Generate work items for each instrument/timeframe combination
        for instrument in instruments:
            for timeframe in timeframes:
                # Split date range into smaller chunks for better parallelization
                current_date = start_date
                
                while current_date < job.end_date:
                    # Calculate chunk end date (e.g., 7 days)
                    chunk_end = min(
                        current_date + timedelta(days=7),
                        job.end_date
                    )
                    
                    work_items.append({
                        'instrument': instrument,
                        'timeframe': timeframe,
                        'start_date': current_date,
                        'end_date': chunk_end
                    })
                    
                    current_date = chunk_end
        
        return work_items
    
    async def _update_job_progress(
        self,
        job: BatchJob,
        processed: int,
        failed: int
    ):
        """Update job progress in database"""
        job.update_progress(processed, failed)
        
        async with self._get_session() as session:
            await session.execute(
                update(BatchJob)
                .where(BatchJob.id == job.id)
                .values(
                    processed_items=job.processed_items,
                    failed_items=job.failed_items,
                    progress_percentage=job.progress_percentage,
                    updated_at=datetime.utcnow()
                )
            )
            await session.commit()
    
    async def _save_checkpoint(
        self,
        job: BatchJob,
        work_item: Dict[str, Any]
    ):
        """Save checkpoint for resumable execution"""
        checkpoint_data = {
            'last_instrument': work_item['instrument'],
            'last_timeframe': work_item['timeframe'],
            'last_date': work_item['end_date'].isoformat(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        async with self._get_session() as session:
            await session.execute(
                update(BatchJob)
                .where(BatchJob.id == job.id)
                .values(
                    checkpoint_data=checkpoint_data,
                    last_processed_instrument=work_item['instrument'],
                    last_processed_timeframe=work_item['timeframe'],
                    last_processed_timestamp=work_item['end_date']
                )
            )
            await session.commit()
    
    async def _log_job_metrics(
        self,
        job_id: str,
        instrument: str,
        timeframe: str,
        candles_processed: int,
        events_detected: int,
        processing_time: float
    ):
        """Log job execution metrics"""
        log_entry = BatchJobLog(
            job_id=uuid.UUID(job_id),
            level="INFO",
            message=f"Processed {candles_processed} candles, detected {events_detected} events",
            details={
                'candles_processed': candles_processed,
                'events_detected': events_detected,
                'processing_time': processing_time,
                'items_per_second': candles_processed / max(processing_time, 0.001)
            },
            instrument=instrument,
            timeframe=timeframe
        )
        
        async with self._get_session() as session:
            session.add(log_entry)
            await session.commit()
    
    def _calculate_total_items(
        self,
        instruments: List[str],
        timeframes: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """Calculate approximate total items to process"""
        # Estimate based on date range and combinations
        days = (end_date - start_date).days
        chunks_per_combination = max(1, days // 7)  # 7-day chunks
        return len(instruments) * len(timeframes) * chunks_per_combination
    
    async def _get_session(self) -> AsyncSession:
        """Get database session"""
        if self.db_session:
            return self.db_session
        return AsyncSessionLocal()
    
    async def pause_job(self, job_id: str) -> bool:
        """Pause a running job"""
        async with self._get_session() as session:
            result = await session.execute(
                update(BatchJob)
                .where(BatchJob.id == uuid.UUID(job_id))
                .where(BatchJob.status == JobStatus.RUNNING)
                .values(status=JobStatus.PAUSED)
            )
            await session.commit()
            return result.rowcount > 0
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job"""
        async with self._get_session() as session:
            result = await session.execute(
                update(BatchJob)
                .where(BatchJob.id == uuid.UUID(job_id))
                .where(BatchJob.status.in_([JobStatus.PENDING, JobStatus.RUNNING, JobStatus.PAUSED]))
                .values(status=JobStatus.CANCELLED)
            )
            await session.commit()
            return result.rowcount > 0
    
    async def get_job_status(self, job_id: str) -> Optional[BatchJob]:
        """Get current job status"""
        async with self._get_session() as session:
            result = await session.execute(
                select(BatchJob).where(BatchJob.id == uuid.UUID(job_id))
            )
            return result.scalar_one_or_none()
    
    async def list_jobs(
        self,
        status: Optional[JobStatus] = None,
        limit: int = 100
    ) -> List[BatchJob]:
        """List batch jobs with optional status filter"""
        async with self._get_session() as session:
            query = select(BatchJob)
            if status:
                query = query.where(BatchJob.status == status)
            query = query.order_by(BatchJob.created_at.desc()).limit(limit)
            
            result = await session.execute(query)
            return result.scalars().all()