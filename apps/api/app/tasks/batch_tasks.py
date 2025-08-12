"""
Batch Processing Tasks

Background tasks for batch job execution and scheduling.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import structlog

from app.services.batch_processor import BatchProcessor
from app.models.batch_job import JobType, JobStatus
from app.database import AsyncSessionLocal
from app.config import settings

logger = structlog.get_logger(__name__)

# Initialize Celery (can be replaced with other task queue systems)
# For now, we'll use asyncio tasks directly
class BatchTaskScheduler:
    """
    Scheduler for batch processing tasks.
    Manages scheduled and recurring batch jobs.
    """
    
    def __init__(self):
        self.batch_processor = BatchProcessor()
        self.scheduled_tasks: Dict[str, asyncio.Task] = {}
        self._running = False
        
    async def start(self):
        """Start the task scheduler"""
        self._running = True
        logger.info("Batch task scheduler started")
        
        # Start monitoring task
        asyncio.create_task(self._monitor_scheduled_jobs())
        
        # Start job executor
        asyncio.create_task(self._execute_pending_jobs())
    
    async def stop(self):
        """Stop the task scheduler"""
        self._running = False
        
        # Cancel all scheduled tasks
        for task_id, task in self.scheduled_tasks.items():
            task.cancel()
            logger.info(f"Cancelled scheduled task {task_id}")
        
        self.scheduled_tasks.clear()
        logger.info("Batch task scheduler stopped")
    
    async def _monitor_scheduled_jobs(self):
        """Monitor for scheduled jobs that need to be executed"""
        while self._running:
            try:
                async with AsyncSessionLocal() as session:
                    # Find jobs scheduled to run now
                    current_time = datetime.utcnow()
                    
                    jobs = await self.batch_processor.list_jobs(
                        status=JobStatus.PENDING
                    )
                    
                    for job in jobs:
                        if job.scheduled_at and job.scheduled_at <= current_time:
                            # Job is ready to run
                            if str(job.id) not in self.scheduled_tasks:
                                logger.info(
                                    "Starting scheduled job",
                                    job_id=str(job.id),
                                    scheduled_at=job.scheduled_at.isoformat()
                                )
                                
                                task = asyncio.create_task(
                                    self._run_batch_job(str(job.id))
                                )
                                self.scheduled_tasks[str(job.id)] = task
                
                # Check every minute
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(
                    "Error monitoring scheduled jobs",
                    error=str(e),
                    exc_info=True
                )
                await asyncio.sleep(60)
    
    async def _execute_pending_jobs(self):
        """Execute pending jobs based on priority"""
        while self._running:
            try:
                # Get highest priority pending job
                jobs = await self.batch_processor.list_jobs(
                    status=JobStatus.PENDING
                )
                
                if jobs:
                    # Sort by priority (lower number = higher priority)
                    jobs.sort(key=lambda j: j.priority)
                    
                    for job in jobs:
                        # Skip if already scheduled or running
                        if str(job.id) in self.scheduled_tasks:
                            continue
                        
                        # Skip if scheduled for future
                        if job.scheduled_at and job.scheduled_at > datetime.utcnow():
                            continue
                        
                        # Check if we have capacity
                        running_count = sum(
                            1 for t in self.scheduled_tasks.values() 
                            if not t.done()
                        )
                        
                        max_concurrent = settings.FEATURE_FLAGS.get(
                            'max_concurrent_batch_jobs', 2
                        )
                        
                        if running_count < max_concurrent:
                            logger.info(
                                "Starting pending job",
                                job_id=str(job.id),
                                priority=job.priority
                            )
                            
                            task = asyncio.create_task(
                                self._run_batch_job(str(job.id))
                            )
                            self.scheduled_tasks[str(job.id)] = task
                
                # Clean up completed tasks
                completed = [
                    task_id for task_id, task in self.scheduled_tasks.items()
                    if task.done()
                ]
                for task_id in completed:
                    del self.scheduled_tasks[task_id]
                
                # Wait before checking again
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(
                    "Error executing pending jobs",
                    error=str(e),
                    exc_info=True
                )
                await asyncio.sleep(10)
    
    async def _run_batch_job(self, job_id: str):
        """Run a batch processing job"""
        try:
            logger.info(f"Starting batch job {job_id}")
            
            # Check if job should be resumed
            job = await self.batch_processor.get_job_status(job_id)
            resume = job and job.is_resumable()
            
            # Execute the job
            result = await self.batch_processor.start_job(
                job_id=job_id,
                resume_from_checkpoint=resume
            )
            
            logger.info(
                "Batch job completed",
                job_id=job_id,
                events_detected=result.get('events_detected', 0),
                events_stored=result.get('events_stored', 0)
            )
            
            # Handle recurring jobs
            if job and job.is_recurring and job.recurrence_pattern:
                await self._schedule_next_recurrence(job)
            
        except Exception as e:
            logger.error(
                "Batch job failed",
                job_id=job_id,
                error=str(e),
                exc_info=True
            )
    
    async def _schedule_next_recurrence(self, job):
        """Schedule the next recurrence of a job"""
        try:
            # Parse recurrence pattern (simplified - could use croniter for complex patterns)
            if job.recurrence_pattern == "daily":
                next_run = datetime.utcnow() + timedelta(days=1)
            elif job.recurrence_pattern == "weekly":
                next_run = datetime.utcnow() + timedelta(weeks=1)
            elif job.recurrence_pattern == "hourly":
                next_run = datetime.utcnow() + timedelta(hours=1)
            else:
                logger.warning(
                    "Unknown recurrence pattern",
                    pattern=job.recurrence_pattern
                )
                return
            
            # Create new job for next recurrence
            new_job = await self.batch_processor.create_batch_job(
                job_type=job.job_type,
                instruments=job.instruments,
                timeframes=job.timeframes,
                start_date=job.start_date,
                end_date=job.end_date,
                batch_size=job.batch_size,
                concurrency_limit=job.concurrency_limit,
                priority=job.priority
            )
            
            # Set scheduling info
            async with AsyncSessionLocal() as session:
                from sqlalchemy import update
                from app.models.batch_job import BatchJob
                
                await session.execute(
                    update(BatchJob)
                    .where(BatchJob.id == new_job.id)
                    .values(
                        scheduled_at=next_run,
                        is_recurring=True,
                        recurrence_pattern=job.recurrence_pattern,
                        created_by=f"recurring-{job.id}"
                    )
                )
                await session.commit()
            
            logger.info(
                "Scheduled next recurrence",
                original_job_id=str(job.id),
                new_job_id=str(new_job.id),
                next_run=next_run.isoformat()
            )
            
        except Exception as e:
            logger.error(
                "Failed to schedule recurrence",
                job_id=str(job.id),
                error=str(e),
                exc_info=True
            )


async def schedule_daily_historical_backfill():
    """
    Schedule a daily historical data backfill job.
    Runs every day at 2 AM UTC.
    """
    try:
        processor = BatchProcessor()
        
        # Calculate date range (last 7 days)
        end_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=7)
        
        # Create batch job
        job = await processor.create_batch_job(
            job_type=JobType.HISTORICAL_BACKFILL,
            instruments=settings.SUPPORTED_INSTRUMENTS[:5],  # Start with subset
            timeframes=["H1", "H4"],  # Focus on key timeframes
            start_date=start_date,
            end_date=end_date,
            batch_size=1000,
            concurrency_limit=4,
            priority=7  # Lower priority
        )
        
        # Set as recurring
        async with AsyncSessionLocal() as session:
            from sqlalchemy import update
            from app.models.batch_job import BatchJob
            
            await session.execute(
                update(BatchJob)
                .where(BatchJob.id == job.id)
                .values(
                    scheduled_at=datetime.utcnow().replace(hour=2, minute=0),
                    is_recurring=True,
                    recurrence_pattern="daily",
                    created_by="system-scheduler"
                )
            )
            await session.commit()
        
        logger.info(
            "Scheduled daily historical backfill",
            job_id=str(job.id),
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        return job
        
    except Exception as e:
        logger.error(
            "Failed to schedule daily backfill",
            error=str(e),
            exc_info=True
        )
        raise


async def schedule_resistance_detection_batch(
    instruments: List[str],
    timeframes: List[str],
    start_date: datetime,
    end_date: datetime,
    priority: int = 5
) -> str:
    """
    Schedule a batch resistance detection job.
    
    Args:
        instruments: List of instruments to process
        timeframes: List of timeframes to process
        start_date: Start date for analysis
        end_date: End date for analysis
        priority: Job priority
        
    Returns:
        Job ID
    """
    try:
        processor = BatchProcessor()
        
        job = await processor.create_batch_job(
            job_type=JobType.RESISTANCE_DETECTION,
            instruments=instruments,
            timeframes=timeframes,
            start_date=start_date,
            end_date=end_date,
            batch_size=500,
            concurrency_limit=4,
            priority=priority
        )
        
        logger.info(
            "Scheduled resistance detection batch",
            job_id=str(job.id),
            instruments_count=len(instruments),
            timeframes_count=len(timeframes)
        )
        
        return str(job.id)
        
    except Exception as e:
        logger.error(
            "Failed to schedule resistance detection",
            error=str(e),
            exc_info=True
        )
        raise


async def retry_failed_jobs():
    """
    Retry failed jobs that haven't exceeded max retries.
    """
    try:
        processor = BatchProcessor()
        
        # Get failed jobs
        failed_jobs = await processor.list_jobs(status=JobStatus.FAILED)
        
        retried_count = 0
        
        for job in failed_jobs:
            if job.can_retry():
                logger.info(
                    "Retrying failed job",
                    job_id=str(job.id),
                    retry_count=job.retry_count
                )
                
                try:
                    # Update retry count
                    async with AsyncSessionLocal() as session:
                        from sqlalchemy import update
                        from app.models.batch_job import BatchJob
                        
                        await session.execute(
                            update(BatchJob)
                            .where(BatchJob.id == job.id)
                            .values(
                                status=JobStatus.PENDING,
                                retry_count=job.retry_count + 1,
                                error_message=None
                            )
                        )
                        await session.commit()
                    
                    retried_count += 1
                    
                except Exception as e:
                    logger.error(
                        "Failed to retry job",
                        job_id=str(job.id),
                        error=str(e)
                    )
        
        logger.info(
            "Retry failed jobs completed",
            retried_count=retried_count,
            total_failed=len(failed_jobs)
        )
        
        return retried_count
        
    except Exception as e:
        logger.error(
            "Error retrying failed jobs",
            error=str(e),
            exc_info=True
        )
        raise


async def cleanup_old_jobs(days: int = 30):
    """
    Clean up old completed jobs.
    
    Args:
        days: Number of days to keep completed jobs
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        async with AsyncSessionLocal() as session:
            from sqlalchemy import delete
            from app.models.batch_job import BatchJob, BatchJobLog
            
            # Delete old logs first
            await session.execute(
                delete(BatchJobLog)
                .where(BatchJobLog.timestamp < cutoff_date)
            )
            
            # Delete old completed jobs
            result = await session.execute(
                delete(BatchJob)
                .where(BatchJob.status == JobStatus.COMPLETED)
                .where(BatchJob.completed_at < cutoff_date)
            )
            
            await session.commit()
            
            deleted_count = result.rowcount
            
            logger.info(
                "Cleaned up old jobs",
                deleted_count=deleted_count,
                cutoff_date=cutoff_date.isoformat()
            )
            
            return deleted_count
            
    except Exception as e:
        logger.error(
            "Failed to cleanup old jobs",
            error=str(e),
            exc_info=True
        )
        raise


# Global scheduler instance
_scheduler: Optional[BatchTaskScheduler] = None


async def get_scheduler() -> BatchTaskScheduler:
    """Get the global task scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = BatchTaskScheduler()
        await _scheduler.start()
    return _scheduler


async def shutdown_scheduler():
    """Shutdown the global task scheduler"""
    global _scheduler
    if _scheduler:
        await _scheduler.stop()
        _scheduler = None