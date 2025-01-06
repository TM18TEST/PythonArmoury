#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Concurrent Thread Pool Task Executor Base Class.
"""

import concurrent.futures
import time
from typing import Any, Dict

from utils.log_ins import LogUtil

logger = LogUtil.get_logger()


class ThreadPoolTaskExecutor:
    """A utility class for executing tasks concurrently using ThreadPoolExecutor."""

    def __init__(self, task_count: int, max_workers: int = None):
        """Initializes the ThreadPoolTaskExecutor with the number of tasks and max workers.

        Args:
            task_count (int): The number of tasks to execute.
            max_workers (int): The maximum number of worker threads in the pool.
        """
        self._task_count: int = task_count
        self._max_workers: int = max_workers
        if max_workers is None:
            self._max_workers = min(self._task_count, 8)
        self.params_demo: list[Any] = []
        logger.info("Concurrent executor initialized successfully.")

    @staticmethod
    def task_function_demo(param: Any) -> Any:
        """Demo task function that simply returns the input parameter.

        Args:
            param (Any): The parameter for the task.

        Returns:
            Any: The result of the task (just the input parameter).
        """
        return param

    def _submit_tasks(self, executor: concurrent.futures.ThreadPoolExecutor) -> Dict[concurrent.futures.Future, Any]:
        """Submits tasks to the executor and returns a mapping of futures to task data.

        Args:
            executor (concurrent.futures.ThreadPoolExecutor): The executor instance.

        Returns:
            Dict[concurrent.futures.Future, Any]: A dictionary mapping futures to their respective task data.
        """
        future_to_task_data = {executor.submit(self.task_function_demo, param): param for param in self.params_demo}
        logger.info("Submitted tasks successfully, task count: %d.", len(future_to_task_data))
        return future_to_task_data

    @staticmethod
    def _handle_exception(future: concurrent.futures.Future, task_data: Any) -> None:
        """Handles exceptions raised by tasks.

        Args:
            future (concurrent.futures.Future): The future object representing the task.
            task_data (Any): The task data associated with the future.
        """
        try:
            exc = future.exception()
            if exc:
                logger.exception("Captured exception from sub-thread: %s, task data: %s.", exc, task_data)
                raise exc
        except Exception as exc:
            logger.exception("Error capturing exception from sub-thread: %s, task data: %s.", exc, task_data)
            raise exc

    @staticmethod
    def _fetch_result(future: concurrent.futures.Future, task_data: Any) -> Any:
        """Fetch result from tasks.

        Args:
            future (concurrent.futures.Future): The future object representing the task.
            task_data (Any): The task data associated with the future.

        Returns:
            Any: The result fetch from task.
        """
        try:
            result = future.result()
        except Exception as exc:
            logger.exception("Error fetching result from sub-thread: %s, task data: %s.", exc, task_data)
            raise exc
        return result

    @staticmethod
    def _validate_result(result: Any, task_data: Any) -> None:
        """Validates the result of a task.

        Args:
            result (Any): The result of the task.
            task_data (Any): The task data associated with the result.

        Raises:
            RuntimeError: If the result is None.
        """
        if result is None:
            raise RuntimeError(f"None result fetched from subtask, task data: {task_data}.")

    def _get_task_index(self, task_data: Any) -> int:
        """Gets the index of a task in the params_demo list.

        Args:
            task_data (Any): The task data.

        Returns:
            int: The index of the task in the params_demo list.
        """
        return self.params_demo.index(task_data)

    @staticmethod
    def _get_task_id(task_data: Any) -> str:
        """Gets the task ID from the task data.

        Args:
            task_data (Any): The task data.

        Returns:
            str: The task ID.
        """
        return task_data.identifier

    def concurrent_run_tasks(self) -> list[Any]:
        """Runs tasks concurrently and returns their results.

        This method uses ThreadPoolExecutor to run tasks concurrently, tracks progress,
        and handles exceptions gracefully.

        Returns:
            list[Any]: A list of results, corresponding to each task.
        """
        logger.info("Starting concurrent execution of tasks.")

        results = [None] * self._task_count
        completed_task_count = 0
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            future_to_task_data = self._submit_tasks(executor)

            for future in concurrent.futures.as_completed(future_to_task_data):
                task_data = future_to_task_data[future]

                # Handle exceptions raised by tasks
                self._handle_exception(future, task_data)

                # Fetch the result
                result: Any = self._fetch_result(future, task_data)

                # Validate and store the result
                self._validate_result(result, task_data)
                task_index = self._get_task_index(task_data)
                results[task_index] = result
                completed_task_count += 1

                # Log task progress
                elapsed_time = time.time() - start_time
                progress = completed_task_count / self._task_count
                logger.info("Task result fetched: %s, task ID: %s, elapsed time: %.3f seconds, progress: %.2f%%.",
                            result, self._get_task_id(task_data), elapsed_time, progress * 100)

        logger.info("Concurrent execution of tasks completed successfully.")
        return results
