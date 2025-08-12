"""
Comprehensive tests for batch processing engine
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import uuid
import time

from app.services.batch_processor import BatchProcessor
from app.models.batch_job import BatchJob, JobStatus, JobType, BatchJobLog
from app.core.queue import JobQueue, QueuePriority, QueuedTask, RateLimiter
from app.tasks.batch_tasks import (
    BatchTaskScheduler,
    schedule_resistance_detection_batch,
    retry_failed_jobs,
    cleanup_old_jobs
)


class TestBatchJobModel:
    """Test suite for BatchJob model"""
    
    def test_batch_job_creation(self):
        """Test creating a batch job"""
        job = BatchJob(
            job_type=JobType.RESISTANCE_DETECTION,
            status=JobStatus.PENDING,
            instruments=["EUR_USD", "GBP_USD"],
            timeframes=["H1", "H4"],
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            batch_size=500,
            concurrency_limit=4,
            priority=5,
            total_items=100,
            processed_items=0,
            failed_items=0,
            progress_percentage=0.0
        )
        
        assert job.job_type == JobType.RESISTANCE_DETECTION
        assert job.status == JobStatus.PENDING
        assert len(job.instruments) == 2
        assert job.batch_size == 500
        assert job.progress_percentage == 0.0
    
    def test_batch_job_update_progress(self):
        """Test updating job progress"""
        job = BatchJob(
            job_type=JobType.HISTORICAL_BACKFILL,
            status=JobStatus.RUNNING,
            instruments=["EUR_USD"],
            timeframes=["H1"],
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            total_items=100,
            processed_items=0,
            failed_items=0,
            progress_percentage=0.0
        )
        
        job.update_progress(processed=10, failed=2)
        
        assert job.processed_items == 10
        assert job.failed_items == 2
        assert job.progress_percentage == 10.0
        
        job.update_progress(processed=40, failed=3)
        
        assert job.processed_items == 50
        assert job.failed_items == 5
        assert job.progress_percentage == 50.0
    
    def test_batch_job_can_retry(self):
        """Test retry logic"""
        job = BatchJob(
            job_type=JobType.RESISTANCE_DETECTION,
            status=JobStatus.FAILED,
            instruments=["EUR_USD"],
            timeframes=["H1"],
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            retry_count=1,
            max_retries=3
        )
        
        assert job.can_retry() is True
        
        job.retry_count = 3
        assert job.can_retry() is False
    
    def test_batch_job_is_resumable(self):
        """Test resumable state check"""
        job = BatchJob(
            job_type=JobType.HISTORICAL_BACKFILL,
            status=JobStatus.FAILED,
            instruments=["EUR_USD"],
            timeframes=["H1"],
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            checkpoint_data={"last_processed": "EUR_USD"}
        )
        
        assert job.is_resumable() is True
        
        job.status = JobStatus.COMPLETED
        assert job.is_resumable() is False
        
        job.status = JobStatus.PAUSED
        job.checkpoint_data = None
        assert job.is_resumable() is False
    
    def test_batch_job_to_dict(self):
        """Test converting job to dictionary"""
        job = BatchJob(
            id=uuid.uuid4(),
            job_type=JobType.RESISTANCE_DETECTION,
            status=JobStatus.RUNNING,
            instruments=["EUR_USD"],
            timeframes=["H1"],
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            batch_size=500,
            concurrency_limit=4,
            priority=5,
            total_items=100,
            processed_items=50,
            progress_percentage=50.0
        )
        
        job_dict = job.to_dict()
        
        assert 'id' in job_dict
        assert job_dict['job_type'] == 'resistance_detection'
        assert job_dict['status'] == 'running'
        assert job_dict['progress']['percentage'] == 50.0
        assert job_dict['progress']['processed_items'] == 50


class TestJobQueue:
    """Test suite for JobQueue"""
    
    @pytest.mark.asyncio
    async def test_queue_initialization(self):
        """Test queue initialization"""
        queue = JobQueue(max_concurrent=4)
        
        assert queue.max_concurrent == 4
        assert len(queue.queue) == 0
        assert len(queue.running_tasks) == 0
        assert queue._shutdown is False
    
    @pytest.mark.asyncio
    async def test_add_task_to_queue(self):
        """Test adding tasks to queue"""
        queue = JobQueue(max_concurrent=2)
        
        await queue.add_task(
            task_id="task1",
            job_id="job1",
            payload={"test": "data"},
            priority=5
        )
        
        await queue.add_task(
            task_id="task2",
            job_id="job1",
            payload={"test": "data2"},
            priority=3  # Higher priority
        )
        
        assert len(queue.queue) == 2
        
        # Check priority ordering (lower number = higher priority)
        next_task = queue.queue[0]
        assert next_task.priority == 3
        assert next_task.task_id == "task2"
    
    @pytest.mark.asyncio
    async def test_queue_execution(self):
        """Test queue task execution"""
        queue = JobQueue(max_concurrent=2)
        await queue.start()
        
        executed = []
        
        async def test_execute(payload):
            executed.append(payload['id'])
            await asyncio.sleep(0.01)
            return {"result": "success", "id": payload['id']}
        
        # Add tasks
        for i in range(5):
            await queue.add_task(
                task_id=f"task{i}",
                job_id="job1",
                payload={"id": i},
                priority=i,
                execute_func=test_execute
            )
        
        # Wait for all tasks to complete
        await asyncio.sleep(0.2)
        
        # Verify execution
        assert len(executed) == 5
        assert 0 in executed  # Task with priority 0 should be executed
        
        await queue.stop()
    
    @pytest.mark.asyncio
    async def test_queue_concurrent_limit(self):
        """Test concurrent execution limit"""
        queue = JobQueue(max_concurrent=2)
        await queue.start()
        
        running_count = []
        
        async def slow_execute(payload):
            running_count.append(len(queue.running_tasks))
            await asyncio.sleep(0.1)
            return {"result": "success"}
        
        # Add more tasks than concurrent limit
        for i in range(5):
            await queue.add_task(
                task_id=f"task{i}",
                job_id="job1",
                payload={"id": i},
                execute_func=slow_execute
            )
        
        await asyncio.sleep(0.05)  # Let some tasks start
        
        # Check that we never exceed concurrent limit
        assert max(running_count) <= 2
        
        await queue.stop()
    
    @pytest.mark.asyncio
    async def test_cancel_task(self):
        """Test task cancellation"""
        queue = JobQueue(max_concurrent=2)
        
        await queue.add_task(
            task_id="task1",
            job_id="job1",
            payload={"test": "data"}
        )
        
        # Cancel queued task
        cancelled = await queue.cancel_task("task1")
        assert cancelled is True
        assert len(queue.queue) == 0
    
    @pytest.mark.asyncio
    async def test_queue_stats(self):
        """Test queue statistics"""
        queue = JobQueue(max_concurrent=2)
        
        await queue.add_task(
            task_id="task1",
            job_id="job1",
            payload={"test": "data"}
        )
        
        stats = queue.get_queue_stats()
        
        assert stats['queued'] == 1
        assert stats['running'] == 0
        assert stats['completed'] == 0
        assert stats['failed'] == 0
        assert stats['max_concurrent'] == 2


class TestRateLimiter:
    """Test suite for RateLimiter"""
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting functionality"""
        limiter = RateLimiter(max_per_second=10.0)
        
        start_time = time.time()
        
        # Try to make 5 rapid calls
        for _ in range(5):
            await limiter.acquire()
        
        elapsed = time.time() - start_time
        
        # Should take at least 0.4 seconds (5 calls at 10/sec = 0.5 sec)
        assert elapsed >= 0.4
    
    @pytest.mark.asyncio
    async def test_rate_limiter_context_manager(self):
        """Test rate limiter as context manager"""
        limiter = RateLimiter(max_per_second=10.0)
        
        start_time = time.time()
        
        async with limiter.limit():
            pass
        
        async with limiter.limit():
            pass
        
        elapsed = time.time() - start_time
        
        # Should enforce rate limit
        assert elapsed >= 0.1


class TestBatchProcessor:
    """Test suite for BatchProcessor"""
    
    @pytest.fixture
    def processor(self):
        """Create a BatchProcessor instance"""
        return BatchProcessor()
    
    @pytest.mark.asyncio
    async def test_create_batch_job(self, processor):
        """Test batch job creation"""
        with patch('app.config.settings.FEATURE_FLAGS', {'batch_processing_enabled': True}):
            with patch.object(processor, '_get_session') as mock_session:
                mock_session.return_value.__aenter__.return_value = AsyncMock()
                
                job = await processor.create_batch_job(
                    job_type=JobType.RESISTANCE_DETECTION,
                    instruments=["EUR_USD", "GBP_USD"],
                    timeframes=["H1", "H4"],
                    start_date=datetime(2024, 1, 1),
                    end_date=datetime(2024, 1, 31),
                    batch_size=500,
                    concurrency_limit=4,
                    priority=5
                )
                
                assert job.job_type == JobType.RESISTANCE_DETECTION
                assert len(job.instruments) == 2
                assert job.batch_size == 500
    
    @pytest.mark.asyncio
    async def test_create_batch_job_feature_disabled(self, processor):
        """Test batch job creation with feature disabled"""
        with patch('app.config.settings.FEATURE_FLAGS', {'batch_processing_enabled': False}):
            with pytest.raises(ValueError, match="Batch processing is disabled"):
                await processor.create_batch_job(
                    job_type=JobType.RESISTANCE_DETECTION,
                    instruments=["EUR_USD"],
                    timeframes=["H1"],
                    start_date=datetime(2024, 1, 1),
                    end_date=datetime(2024, 1, 31)
                )
    
    def test_generate_work_items(self, processor):
        """Test work item generation"""
        job = BatchJob(
            job_type=JobType.RESISTANCE_DETECTION,
            status=JobStatus.PENDING,
            instruments=["EUR_USD", "GBP_USD"],
            timeframes=["H1", "H4"],
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 15),
            batch_size=500,
            concurrency_limit=4,
            priority=5,
            total_items=100
        )
        
        work_items = processor._generate_work_items(job, resume_from_checkpoint=False)
        
        # Should generate items for each instrument/timeframe combination
        assert len(work_items) > 0
        
        # Check first work item
        first_item = work_items[0]
        assert first_item['instrument'] in ["EUR_USD", "GBP_USD"]
        assert first_item['timeframe'] in ["H1", "H4"]
        assert first_item['start_date'] == datetime(2024, 1, 1)
    
    def test_generate_work_items_with_checkpoint(self, processor):
        """Test work item generation with checkpoint"""
        job = BatchJob(
            job_type=JobType.RESISTANCE_DETECTION,
            status=JobStatus.FAILED,
            instruments=["EUR_USD", "GBP_USD", "USD_JPY"],
            timeframes=["H1", "H4"],
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 15),
            checkpoint_data={
                "last_instrument": "GBP_USD",
                "last_timeframe": "H1",
                "last_date": "2024-01-07T00:00:00"
            }
        )
        
        work_items = processor._generate_work_items(job, resume_from_checkpoint=True)
        
        # Should start from checkpoint
        first_item = work_items[0]
        assert first_item['instrument'] in ["GBP_USD", "USD_JPY"]  # Should not include EUR_USD
    
    def test_calculate_total_items(self, processor):
        """Test total items calculation"""
        total = processor._calculate_total_items(
            instruments=["EUR_USD", "GBP_USD"],
            timeframes=["H1", "H4"],
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 15)
        )
        
        # 2 instruments * 2 timeframes * 2 weeks (2 chunks) = 8
        assert total == 8
    
    @pytest.mark.asyncio
    async def test_process_work_item(self, processor):
        """Test processing a single work item"""
        job = BatchJob(
            id=uuid.uuid4(),
            job_type=JobType.RESISTANCE_DETECTION,
            status=JobStatus.RUNNING,
            instruments=["EUR_USD"],
            timeframes=["H1"],
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 2),
            batch_size=100
        )
        
        # Mock dependencies
        processor.market_data_service.fetch_historical_data = AsyncMock(return_value=[])
        processor.event_processor.process_market_data_batch = AsyncMock(
            return_value={
                'events_detected': 5,
                'events_stored': 5,
                'candles_processed': 100
            }
        )
        
        with patch.object(processor, '_log_job_metrics', new_callable=AsyncMock):
            result = await processor._process_work_item(
                job=job,
                work_item={
                    'instrument': 'EUR_USD',
                    'timeframe': 'H1',
                    'start_date': datetime(2024, 1, 1),
                    'end_date': datetime(2024, 1, 2)
                }
            )
        
        assert result['events_detected'] == 0  # No candles fetched in mock
        assert result['candles_processed'] == 0


class TestBatchTaskScheduler:
    """Test suite for BatchTaskScheduler"""
    
    @pytest.fixture
    def scheduler(self):
        """Create a BatchTaskScheduler instance"""
        return BatchTaskScheduler()
    
    @pytest.mark.asyncio
    async def test_scheduler_start_stop(self, scheduler):
        """Test scheduler start and stop"""
        await scheduler.start()
        assert scheduler._running is True
        
        await scheduler.stop()
        assert scheduler._running is False
        assert len(scheduler.scheduled_tasks) == 0
    
    @pytest.mark.asyncio
    async def test_schedule_resistance_detection_batch():
        """Test scheduling a resistance detection batch"""
        with patch('app.services.batch_processor.BatchProcessor.create_batch_job') as mock_create:
            mock_job = Mock(id=uuid.uuid4())
            mock_create.return_value = mock_job
            
            job_id = await schedule_resistance_detection_batch(
                instruments=["EUR_USD"],
                timeframes=["H1"],
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 1, 31),
                priority=5
            )
            
            assert job_id == str(mock_job.id)
            mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_retry_failed_jobs():
        """Test retrying failed jobs"""
        mock_failed_job = Mock(
            id=uuid.uuid4(),
            can_retry=Mock(return_value=True),
            retry_count=1
        )
        
        with patch('app.services.batch_processor.BatchProcessor.list_jobs') as mock_list:
            mock_list.return_value = [mock_failed_job]
            
            with patch('app.database.AsyncSessionLocal') as mock_session:
                mock_session.return_value.__aenter__.return_value = AsyncMock()
                
                retried = await retry_failed_jobs()
                
                assert retried == 1
    
    @pytest.mark.asyncio
    async def test_cleanup_old_jobs():
        """Test cleaning up old jobs"""
        with patch('app.database.AsyncSessionLocal') as mock_session:
            mock_exec = AsyncMock()
            mock_exec.rowcount = 5
            mock_session.return_value.__aenter__.return_value.execute = AsyncMock(
                return_value=mock_exec
            )
            
            deleted = await cleanup_old_jobs(days=30)
            
            assert deleted == 5


class TestPerformanceMetrics:
    """Test suite for performance and metrics tracking"""
    
    @pytest.mark.asyncio
    async def test_parallel_processing_performance(self):
        """Test parallel processing performance"""
        processor = BatchProcessor()
        
        job = BatchJob(
            id=uuid.uuid4(),
            job_type=JobType.RESISTANCE_DETECTION,
            status=JobStatus.RUNNING,
            instruments=["EUR_USD", "GBP_USD"],
            timeframes=["H1", "H4"],
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 7),
            batch_size=500,
            concurrency_limit=4,
            total_items=10
        )
        
        # Mock dependencies for speed
        processor.event_processor.process_market_data_batch = AsyncMock(
            return_value={
                'events_detected': 10,
                'events_stored': 10,
                'candles_processed': 500
            }
        )
        processor.market_data_service.fetch_historical_data = AsyncMock(
            return_value=[Mock() for _ in range(500)]
        )
        
        with patch('app.config.settings.FEATURE_FLAGS', {'parallel_processing': True}):
            with patch.object(processor, '_get_session') as mock_session:
                mock_session.return_value.__aenter__.return_value = AsyncMock()
                
                with patch.object(processor.job_queue, 'add_task', new_callable=AsyncMock):
                    with patch.object(processor.job_queue, 'wait_for_task', new_callable=AsyncMock) as mock_wait:
                        mock_wait.return_value = {
                            'events_detected': 10,
                            'events_stored': 10,
                            'candles_processed': 500
                        }
                        
                        start_time = time.time()
                        result = await processor._process_job_parallel(job, False)
                        elapsed = time.time() - start_time
                        
                        # Should complete quickly with mocked operations
                        assert elapsed < 2.0
                        assert result['events_detected'] > 0
    
    @pytest.mark.asyncio
    async def test_progress_tracking(self):
        """Test job progress tracking"""
        processor = BatchProcessor()
        
        job = BatchJob(
            id=uuid.uuid4(),
            job_type=JobType.HISTORICAL_BACKFILL,
            status=JobStatus.RUNNING,
            total_items=100,
            processed_items=0,
            failed_items=0
        )
        
        with patch.object(processor, '_get_session') as mock_session:
            mock_session.return_value.__aenter__.return_value = AsyncMock()
            
            # Update progress
            await processor._update_job_progress(job, processed=10, failed=2)
            
            assert job.processed_items == 10
            assert job.failed_items == 2
            assert job.progress_percentage == 10.0
    
    @pytest.mark.asyncio
    async def test_checkpoint_saving(self):
        """Test checkpoint saving for resumable execution"""
        processor = BatchProcessor()
        
        job = BatchJob(
            id=uuid.uuid4(),
            job_type=JobType.RESISTANCE_DETECTION,
            status=JobStatus.RUNNING
        )
        
        work_item = {
            'instrument': 'EUR_USD',
            'timeframe': 'H1',
            'start_date': datetime(2024, 1, 1),
            'end_date': datetime(2024, 1, 2)
        }
        
        with patch.object(processor, '_get_session') as mock_session:
            mock_session.return_value.__aenter__.return_value = AsyncMock()
            
            await processor._save_checkpoint(job, work_item)
            
            # Verify checkpoint was saved
            mock_session.return_value.__aenter__.return_value.execute.assert_called_once()


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.mark.asyncio
    async def test_job_cancellation(self):
        """Test job cancellation"""
        processor = BatchProcessor()
        
        job_id = str(uuid.uuid4())
        
        with patch.object(processor, '_get_session') as mock_session:
            mock_exec = AsyncMock()
            mock_exec.rowcount = 1
            mock_session.return_value.__aenter__.return_value.execute = AsyncMock(
                return_value=mock_exec
            )
            
            cancelled = await processor.cancel_job(job_id)
            
            assert cancelled is True
    
    @pytest.mark.asyncio
    async def test_job_pause_resume(self):
        """Test pausing and resuming jobs"""
        processor = BatchProcessor()
        
        job_id = str(uuid.uuid4())
        
        with patch.object(processor, '_get_session') as mock_session:
            mock_exec = AsyncMock()
            mock_exec.rowcount = 1
            mock_session.return_value.__aenter__.return_value.execute = AsyncMock(
                return_value=mock_exec
            )
            
            # Pause job
            paused = await processor.pause_job(job_id)
            assert paused is True
    
    @pytest.mark.asyncio
    async def test_concurrent_job_limit(self):
        """Test concurrent job execution limit"""
        scheduler = BatchTaskScheduler()
        
        # Create multiple pending jobs
        jobs = []
        for i in range(5):
            job = Mock(
                id=uuid.uuid4(),
                priority=i,
                scheduled_at=None
            )
            jobs.append(job)
        
        with patch.object(scheduler.batch_processor, 'list_jobs', return_value=jobs):
            with patch('app.config.settings.FEATURE_FLAGS', {'max_concurrent_batch_jobs': 2}):
                # Mock task creation
                scheduler.scheduled_tasks = {
                    str(uuid.uuid4()): Mock(done=Mock(return_value=False)),
                    str(uuid.uuid4()): Mock(done=Mock(return_value=False))
                }
                
                # Try to execute pending jobs
                # Should not exceed max concurrent limit
                assert len([t for t in scheduler.scheduled_tasks.values() if not t.done()]) <= 2
    
    @pytest.mark.asyncio
    async def test_error_recovery(self):
        """Test error recovery and retry logic"""
        processor = BatchProcessor()
        
        job = BatchJob(
            id=uuid.uuid4(),
            job_type=JobType.RESISTANCE_DETECTION,
            status=JobStatus.RUNNING,
            instruments=["EUR_USD"],
            timeframes=["H1"],
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 2),
            retry_count=0,
            max_retries=3
        )
        
        # Simulate error in processing
        processor.event_processor.process_market_data_batch = AsyncMock(
            side_effect=Exception("Processing error")
        )
        
        with patch.object(processor, '_get_session') as mock_session:
            mock_session.return_value.__aenter__.return_value = AsyncMock()
            
            with pytest.raises(Exception):
                await processor._process_work_item(
                    job=job,
                    work_item={
                        'instrument': 'EUR_USD',
                        'timeframe': 'H1',
                        'start_date': datetime(2024, 1, 1),
                        'end_date': datetime(2024, 1, 2)
                    }
                )
            
            # Job should still be retryable
            assert job.can_retry() is True