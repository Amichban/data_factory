"""
Queue Management System for Batch Processing

Manages job queues, priority scheduling, and concurrent execution limits.
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import heapq
import structlog
from contextlib import asynccontextmanager

logger = structlog.get_logger(__name__)


class QueuePriority(Enum):
    """Queue priority levels"""
    CRITICAL = 1
    HIGH = 3
    NORMAL = 5
    LOW = 7
    BACKGROUND = 10


@dataclass
class QueuedTask:
    """Represents a task in the queue"""
    task_id: str
    job_id: str
    priority: int
    payload: Dict[str, Any]
    created_at: datetime
    execute_func: Optional[Callable] = None
    
    def __lt__(self, other):
        """Compare tasks by priority (lower number = higher priority)"""
        return self.priority < other.priority


class JobQueue:
    """
    Priority queue for batch processing jobs.
    Manages concurrent execution limits and job scheduling.
    """
    
    def __init__(self, max_concurrent: int = 4):
        """
        Initialize the job queue.
        
        Args:
            max_concurrent: Maximum number of concurrent jobs
        """
        self.max_concurrent = max_concurrent
        self.queue: List[QueuedTask] = []
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.completed_tasks: Dict[str, Any] = {}
        self.failed_tasks: Dict[str, Exception] = {}
        self._lock = asyncio.Lock()
        self._shutdown = False
        self._workers: List[asyncio.Task] = []
        
    async def start(self):
        """Start the queue workers"""
        logger.info(
            "Starting job queue",
            max_concurrent=self.max_concurrent
        )
        
        # Create worker tasks
        for i in range(self.max_concurrent):
            worker = asyncio.create_task(self._worker(worker_id=i))
            self._workers.append(worker)
    
    async def stop(self):
        """Stop the queue and wait for running tasks to complete"""
        logger.info("Stopping job queue")
        self._shutdown = True
        
        # Cancel all workers
        for worker in self._workers:
            worker.cancel()
        
        # Wait for running tasks to complete
        if self.running_tasks:
            logger.info(
                "Waiting for running tasks to complete",
                count=len(self.running_tasks)
            )
            await asyncio.gather(
                *self.running_tasks.values(),
                return_exceptions=True
            )
    
    async def add_task(
        self,
        task_id: str,
        job_id: str,
        payload: Dict[str, Any],
        priority: int = QueuePriority.NORMAL.value,
        execute_func: Optional[Callable] = None
    ) -> None:
        """
        Add a task to the queue.
        
        Args:
            task_id: Unique task identifier
            job_id: Parent job identifier
            payload: Task payload data
            priority: Task priority (lower = higher priority)
            execute_func: Function to execute for this task
        """
        async with self._lock:
            task = QueuedTask(
                task_id=task_id,
                job_id=job_id,
                priority=priority,
                payload=payload,
                created_at=datetime.utcnow(),
                execute_func=execute_func
            )
            
            heapq.heappush(self.queue, task)
            
            logger.debug(
                "Task added to queue",
                task_id=task_id,
                job_id=job_id,
                priority=priority,
                queue_size=len(self.queue)
            )
    
    async def _worker(self, worker_id: int):
        """
        Worker coroutine that processes tasks from the queue.
        
        Args:
            worker_id: Worker identifier
        """
        logger.info(f"Worker {worker_id} started")
        
        while not self._shutdown:
            try:
                # Get next task from queue
                task = await self._get_next_task()
                if task is None:
                    # No tasks available, wait a bit
                    await asyncio.sleep(0.1)
                    continue
                
                # Execute the task
                logger.info(
                    f"Worker {worker_id} executing task",
                    task_id=task.task_id,
                    job_id=task.job_id
                )
                
                start_time = datetime.utcnow()
                
                try:
                    if task.execute_func:
                        result = await task.execute_func(task.payload)
                    else:
                        # Default execution if no function provided
                        result = await self._default_execute(task.payload)
                    
                    execution_time = (datetime.utcnow() - start_time).total_seconds()
                    
                    async with self._lock:
                        self.completed_tasks[task.task_id] = {
                            'result': result,
                            'execution_time': execution_time,
                            'completed_at': datetime.utcnow()
                        }
                        if task.task_id in self.running_tasks:
                            del self.running_tasks[task.task_id]
                    
                    logger.info(
                        f"Worker {worker_id} completed task",
                        task_id=task.task_id,
                        execution_time=execution_time
                    )
                    
                except Exception as e:
                    logger.error(
                        f"Worker {worker_id} task failed",
                        task_id=task.task_id,
                        error=str(e),
                        exc_info=True
                    )
                    
                    async with self._lock:
                        self.failed_tasks[task.task_id] = e
                        if task.task_id in self.running_tasks:
                            del self.running_tasks[task.task_id]
                
            except asyncio.CancelledError:
                logger.info(f"Worker {worker_id} cancelled")
                break
            except Exception as e:
                logger.error(
                    f"Worker {worker_id} error",
                    error=str(e),
                    exc_info=True
                )
                await asyncio.sleep(1)  # Brief pause on error
        
        logger.info(f"Worker {worker_id} stopped")
    
    async def _get_next_task(self) -> Optional[QueuedTask]:
        """Get the next task from the priority queue"""
        async with self._lock:
            if not self.queue:
                return None
            
            # Check if we're at concurrent limit
            if len(self.running_tasks) >= self.max_concurrent:
                return None
            
            # Get highest priority task
            task = heapq.heappop(self.queue)
            
            # Mark as running
            self.running_tasks[task.task_id] = asyncio.current_task()
            
            return task
    
    async def _default_execute(self, payload: Dict[str, Any]) -> Any:
        """Default task execution (can be overridden)"""
        # Simulate some work
        await asyncio.sleep(0.1)
        return {'status': 'completed', 'payload': payload}
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get current queue statistics"""
        return {
            'queued': len(self.queue),
            'running': len(self.running_tasks),
            'completed': len(self.completed_tasks),
            'failed': len(self.failed_tasks),
            'max_concurrent': self.max_concurrent,
            'is_shutdown': self._shutdown
        }
    
    async def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """
        Wait for a specific task to complete.
        
        Args:
            task_id: Task identifier
            timeout: Maximum time to wait
            
        Returns:
            Task result
            
        Raises:
            TimeoutError: If timeout is exceeded
            Exception: If task failed
        """
        start_time = datetime.utcnow()
        
        while True:
            # Check if completed
            if task_id in self.completed_tasks:
                return self.completed_tasks[task_id]['result']
            
            # Check if failed
            if task_id in self.failed_tasks:
                raise self.failed_tasks[task_id]
            
            # Check timeout
            if timeout:
                elapsed = (datetime.utcnow() - start_time).total_seconds()
                if elapsed > timeout:
                    raise TimeoutError(f"Task {task_id} did not complete within {timeout}s")
            
            # Wait a bit before checking again
            await asyncio.sleep(0.1)
    
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task if it's queued or running.
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if task was cancelled, False otherwise
        """
        async with self._lock:
            # Remove from queue if present
            original_len = len(self.queue)
            self.queue = [t for t in self.queue if t.task_id != task_id]
            
            if len(self.queue) < original_len:
                heapq.heapify(self.queue)  # Re-heapify after removal
                logger.info(f"Cancelled queued task {task_id}")
                return True
            
            # Cancel if running
            if task_id in self.running_tasks:
                self.running_tasks[task_id].cancel()
                logger.info(f"Cancelled running task {task_id}")
                return True
            
            return False


class RateLimiter:
    """
    Rate limiter for controlling API calls and processing speed.
    """
    
    def __init__(self, max_per_second: float = 10.0):
        """
        Initialize rate limiter.
        
        Args:
            max_per_second: Maximum operations per second
        """
        self.max_per_second = max_per_second
        self.min_interval = 1.0 / max_per_second
        self.last_call_time = 0.0
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to proceed, waiting if necessary"""
        async with self._lock:
            current_time = asyncio.get_event_loop().time()
            time_since_last = current_time - self.last_call_time
            
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                await asyncio.sleep(sleep_time)
                self.last_call_time = asyncio.get_event_loop().time()
            else:
                self.last_call_time = current_time
    
    @asynccontextmanager
    async def limit(self):
        """Context manager for rate limiting"""
        await self.acquire()
        yield
    
    def update_rate(self, max_per_second: float):
        """Update the rate limit"""
        self.max_per_second = max_per_second
        self.min_interval = 1.0 / max_per_second


# Global queue instance (singleton)
_job_queue: Optional[JobQueue] = None


def get_job_queue(max_concurrent: int = 4) -> JobQueue:
    """Get the global job queue instance"""
    global _job_queue
    if _job_queue is None:
        _job_queue = JobQueue(max_concurrent=max_concurrent)
    return _job_queue


async def initialize_queue(max_concurrent: int = 4):
    """Initialize and start the global job queue"""
    queue = get_job_queue(max_concurrent)
    await queue.start()
    return queue


async def shutdown_queue():
    """Shutdown the global job queue"""
    global _job_queue
    if _job_queue:
        await _job_queue.stop()
        _job_queue = None