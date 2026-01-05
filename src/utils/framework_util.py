#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Framework Utility Class Source Code.
"""
import time
from typing import Callable, Any, List, Type, Optional, Iterable


class FrameworkUtil:
    @staticmethod
    def call_with_retry(
            func: Callable[..., Any],
            *args: Any,
            retries: int = 5,
            interval_sec: float = 0.2,
            exc_list: Optional[List[Type[Exception]]] = None,
            **kwargs: Any):
        """
        Call a function with retry mechanism.

        This method executes the given function and retries it if it raises an exception.
        The number of retries and the exceptions to retry on can be specified.

        Parameters:
            func (Callable): The function to be called.
            *args: Positional arguments to pass to the function.
            retries (int): Maximum number of retry attempts. Default is 3.
            interval_sec (float): Time in seconds to wait between retries. Default is 0.1.
            exc_list (List[Type[Exception]]): List of exception types to retry on.
                                             If None, retry on any exception.
            **kwargs: Keyword arguments to pass to the function.

        Returns:
            Any: The result of the function call if successful.

        Raises:
            Exception: If the function raises an exception not in the exc_list or after all retries.
        """
        if retries <= 0:
            raise RuntimeError(f"Invalid retries: {retries}")
        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if exc_list is not None and not isinstance(e, tuple(exc_list)):
                    raise
                if attempt == retries - 1:
                    raise
                time.sleep(interval_sec)

    @staticmethod
    def call_with_retry2(
            func: Callable,
            *args,
            retries: int = 5,
            interval_sec: float = 0.5,
            retry_exceptions: Iterable[Type[Exception]] = (
                    FileNotFoundError,
                    PermissionError,
                    OSError,
            ),
            **kwargs
    ):
        last_exc = None
        for attempt in range(1, retries + 1):
            try:
                return func(*args, **kwargs)
            except retry_exceptions as e:
                last_exc = e
                if attempt < retries:
                    time.sleep(interval_sec)

        raise last_exc
