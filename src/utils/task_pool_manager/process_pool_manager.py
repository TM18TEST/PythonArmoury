#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Process Pool Manager Class Source Code.
"""

import platform
from multiprocessing import Process, Queue, set_start_method, get_start_method
from queue import Empty
from typing import Callable, Dict, Any, Optional


# Handlers (must be defined at the top level)
def text_handler(data: str) -> str:
    """Example handler that processes text."""
    return data.upper()


def math_handler(data: Dict[str, Any]) -> int:
    """Example handler that processes math operations."""
    return data["x"] + data["y"]


class ProcessPoolManager:
    def __init__(self, num_workers: int = 2) -> None:
        self.num_workers: int = num_workers
        self.request_queue: Queue = Queue()
        self.response_queue: Queue = Queue()
        self.handlers: Dict[str, Callable[[Any], Any]] = {}
        self.pool: list[Process] = []
        self.task_id: int = 0
        self.stopped: bool = False

    def register_handler(self, message_type: str, handler: Callable[[Any], Any]) -> None:
        """Register a handler for a specific message type."""
        self.handlers[message_type] = handler

    def start_workers(self) -> None:
        """Start worker processes."""
        self.stopped = False
        for _ in range(self.num_workers):
            process = Process(
                target=self.worker_function,
                args=(self.request_queue, self.response_queue, self.handlers),
            )
            process.start()
            self.pool.append(process)

    def stop_workers(self) -> None:
        """Stop all worker processes."""
        for _ in range(len(self.pool)):
            self.request_queue.put(None)  # Send termination signal
        for process in self.pool:
            process.join()
        self.pool.clear()
        self.stopped = True

    def send_request(self, message: Dict[str, Any]) -> None:
        """Send a request to the worker pool."""
        if self.stopped or not self.pool:
            raise RuntimeError("Cannot send request: worker processes are not running.")
        if "type" not in message or "data" not in message:
            raise ValueError("Message must contain 'type' and 'data' fields.")
        if message["type"] not in self.handlers:
            raise ValueError(f"Unknown message type: {message['type']}")

        self.task_id += 1
        message["id"] = self.task_id  # Assign a unique task ID
        self.request_queue.put(message)

    def get_response(self, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Retrieve a response from the response queue."""
        try:
            return self.response_queue.get(timeout=timeout)
        except Empty:
            return None

    @staticmethod
    def worker_function(request_queue: Queue, response_queue: Queue, handlers: Dict[str, Callable[[Any], Any]]) -> None:
        """Worker process function to handle requests."""
        while True:
            try:
                message = request_queue.get()
                if message is None:  # Termination signal
                    break
                message_type = message["type"]
                data = message["data"]
                task_id = message["id"]

                if message_type not in handlers:
                    raise ValueError(f"Unknown message type: {message_type}")

                # Call the corresponding handler
                handler = handlers[message_type]
                result = handler(data)
                rsp = {"id": task_id, "type": message_type, "result": result}

                # Send the result to the response queue
                response_queue.put(rsp)

            except Exception as exp:
                response_queue.put({"error": str(exp)})


# Main function
if __name__ == "__main__":
    # Automatically set the start method based on the platform
    if platform.system() == "Windows":
        start_method = "spawn"
    elif platform.system() == "Darwin":
        start_method = "spawn"  # Explicitly use spawn on macOS
    else:
        start_method = "fork"

    try:
        current_method = get_start_method(allow_none=True)
        if current_method != start_method:
            set_start_method(start_method, force=True)
    except RuntimeError as e:
        print(f"Warning: {e}. Using existing start method.")

    # Create the manager
    manager = ProcessPoolManager(num_workers=4)

    # Register handlers
    manager.register_handler("text", text_handler)
    manager.register_handler("math", math_handler)

    # Start workers
    manager.start_workers()

    # Send requests
    manager.send_request({"type": "text", "data": "hello world"})
    manager.send_request({"type": "math", "data": {"x": 5, "y": 10}})

    # Collect responses
    results = []
    for _ in range(2):
        response = manager.get_response(timeout=5)
        results.append(response)

    # Stop workers
    manager.stop_workers()

    print("Results:", results)
