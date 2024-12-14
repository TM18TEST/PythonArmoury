#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Time Utility Class Source Code.
"""


class TimeDuration:
    def __init__(self, start_timestamp_second: float, end_timestamp_second: float):
        self.start_timestamp_second: float = start_timestamp_second
        self.end_timestamp_second: float = end_timestamp_second

    def __repr__(self) -> str:
        return f'Start timestamp: {self.start_timestamp_second}, end: {self.end_timestamp_second}'
