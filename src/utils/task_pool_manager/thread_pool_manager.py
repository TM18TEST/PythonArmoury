#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Thread Pool Manager Class Source Code.
"""

from concurrent.futures import ThreadPoolExecutor, Future
from queue import Queue, Empty
from threading import Lock
from typing import Callable, Dict, Any, Optional


class ThreadPoolManager:
    def __init__(self, max_workers: int = 4) -> None:
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.handlers: Dict[str, Callable[[Any], Any]] = {}
        self.response_queue: Queue = Queue()
        self.task_id_lock = Lock()
        self.task_id = 0

    def register_handler(self, message_type: str, handler: Callable[[Any], Any]) -> None:
        """Register a handler for a specific message type."""
        self.handlers[message_type] = handler

    def submit_task(self, message: Dict[str, Any]) -> None:
        """Submit a task to the thread pool."""
        if "type" not in message or "data" not in message:
            raise ValueError("Message must contain 'type' and 'data' fields.")
        if message["type"] not in self.handlers:
            raise ValueError(f"Unknown message type: {message['type']}")

        with self.task_id_lock:
            self.task_id += 1
            message["id"] = self.task_id  # Assign a unique task ID

        handler = self.handlers[message["type"]]
        future: Future = self.executor.submit(self._task_wrapper, handler, message)
        future.add_done_callback(self._handle_response)

    @staticmethod
    def _task_wrapper(handler: Callable[[Any], Any], message: Dict[str, Any]) -> Dict[str, Any]:
        """Wrapper to execute a handler and capture its result."""
        try:
            result = handler(message["data"])
            return {"id": message["id"], "type": message["type"], "result": result}
        except Exception as e:
            return {"id": message["id"], "type": message["type"], "error": str(e)}

    def _handle_response(self, future: Future) -> None:
        """Callback to handle the response from a task."""
        try:
            result = future.result()
            self.response_queue.put(result)
        except Exception as e:
            self.response_queue.put({"error": str(e)})

    def get_response(self, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Retrieve a response from the response queue."""
        try:
            return self.response_queue.get(timeout=timeout)
        except Empty:
            return None

    def shutdown(self) -> None:
        """Shut down the thread pool."""
        self.executor.shutdown(wait=True)
