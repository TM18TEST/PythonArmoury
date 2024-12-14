#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Process Pool Manager Class Test Cases.
"""

import unittest
from utils.task_pool_manager.process_pool_manager import ProcessPoolManager, text_handler, math_handler


class TestProcessPoolManager(unittest.TestCase):
    def setUp(self):
        """Set up the ProcessPoolManager for testing."""
        self.manager = ProcessPoolManager(num_workers=2)
        self.manager.register_handler("text", text_handler)
        self.manager.register_handler("math", math_handler)
        self.manager.start_workers()

    def tearDown(self):
        """Clean up by stopping all worker processes."""
        self.manager.stop_workers()

    def test_register_handler(self):
        """Test that handlers can be correctly registered."""
        def dummy_handler(data):
            return data

        self.manager.register_handler("dummy", dummy_handler)
        self.assertIn("dummy", self.manager.handlers)
        self.assertEqual(self.manager.handlers["dummy"], dummy_handler)

    def test_process_text_request(self):
        """Test processing a text request."""
        self.manager.send_request({"type": "text", "data": "unittest"})
        response = self.manager.get_response(timeout=5)
        self.assertIsNotNone(response)
        self.assertEqual(response["result"], "UNITTEST")

    def test_process_math_request(self):
        """Test processing a math request."""
        self.manager.send_request({"type": "math", "data": {"x": 10, "y": 5}})
        response = self.manager.get_response(timeout=5)
        self.assertIsNotNone(response)
        self.assertEqual(response["result"], 15)

    def test_unknown_message_type(self):
        """Test sending an unknown message type."""
        with self.assertRaises(ValueError) as context:
            self.manager.send_request({"type": "unknown", "data": "test"})
        self.assertIn("Unknown message type", str(context.exception))

    def test_multiple_requests(self):
        """Test handling multiple requests concurrently."""
        requests = [
            {"type": "text", "data": "hello"},
            {"type": "math", "data": {"x": 2, "y": 3}},
            {"type": "text", "data": "world"},
        ]
        for request in requests:
            self.manager.send_request(request)

        results = []
        for _ in range(len(requests)):
            response = self.manager.get_response(timeout=5)
            results.append(response)

        # Verify results
        self.assertEqual(len(results), 3)
        expected_results = [
            {"result": "HELLO"},
            {"result": 5},
            {"result": "WORLD"},
        ]
        for result, expected in zip(results, expected_results):
            self.assertEqual(result["result"], expected["result"])

    def test_stop_workers(self):
        """Test stopping all worker processes."""
        self.manager.stop_workers()
        with self.assertRaises(RuntimeError) as context:
            self.manager.send_request({"type": "text", "data": "test"})
        self.assertIn("worker processes are not running", str(context.exception))

    def test_empty_response(self):
        """Test handling of empty response queue."""
        response = self.manager.get_response(timeout=1)
        self.assertIsNone(response)


if __name__ == "__main__":
    unittest.main()
