import unittest
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from stack.app.schema.thread import Thread
from stack.app.utils.group_threads import group_threads

class TestGroupThreads(unittest.TestCase):

    def setUp(self):
        self.thread_ids = [str(uuid4()) for _ in range(3)]
        self.user_ids = [str(uuid4()) for _ in range(3)]
        self.assistant_ids = [str(uuid4()) for _ in range(3)]

        # Creating mock threads data with UUIDs
        self.threads = [
            Thread(
                id=self.thread_ids[0],
                user_id=self.user_ids[0],
                assistant_id=self.assistant_ids[0],
                name="Thread 1",
                kwargs=None,
                created_at=datetime(2024, 6, 19, 21, 47, 45, tzinfo=timezone.utc),
                updated_at=datetime(2024, 6, 19, 21, 47, 45, tzinfo=timezone.utc)
            ),
            Thread(
                id=self.thread_ids[1],
                user_id=self.user_ids[1],
                assistant_id=self.assistant_ids[1],
                name="Thread 2",
                kwargs=None,
                created_at=datetime(2024, 6, 19, 21, 16, 3, tzinfo=timezone.utc),
                updated_at=datetime(2024, 6, 19, 21, 16, 3, tzinfo=timezone.utc)
            ),
            Thread(
                id=self.thread_ids[2],
                user_id=self.user_ids[2],
                assistant_id=self.assistant_ids[2],
                name="Thread 3",
                kwargs=None,
                created_at=datetime(2024, 6, 18, 23, 6, 27, tzinfo=timezone.utc),
                updated_at=datetime(2024, 6, 18, 23, 6, 27, tzinfo=timezone.utc)
            ),
        ]

    def test_group_threads_utc(self):
        # Simulate UTC timezone (offset 0)
        result = group_threads(self.threads, 0)
        today_ids = [str(thread.id) for thread in result["Today"]]
        yesterday_ids = [str(thread.id) for thread in result["Yesterday"]]

        print("Today IDs:", today_ids)
        print("Yesterday IDs:", yesterday_ids)

        self.assertIn(self.thread_ids[0], today_ids)
        self.assertIn(self.thread_ids[1], today_ids)
        self.assertIn(self.thread_ids[2], yesterday_ids)

    def test_group_threads_offset_positive(self):
        # Simulate timezone UTC+6 (offset +360 minutes)
        result = group_threads(self.threads, 360)
        today_ids = [str(thread.id) for thread in result["Today"]]
        yesterday_ids = [str(thread.id) for thread in result["Yesterday"]]  # New line to check yesterday's content

        print("Today IDs:", today_ids)
        print("Yesterday IDs:", yesterday_ids)  # Printing yesterday IDs to debug

        self.assertIn(self.thread_ids[0], today_ids)
        self.assertIn(self.thread_ids[1], today_ids)
        self.assertIn(self.thread_ids[2], yesterday_ids)  # This must be yesterday instead today

    def test_group_threads_offset_negative(self):
        # Simulate timezone UTC-6 (offset -360 minutes)
        result = group_threads(self.threads, -360)
        today_ids = [str(thread.id) for thread in result["Today"]]  # Adding to check today's content
        yesterday_ids = [str(thread.id) for thread in result["Yesterday"]]

        print("Today IDs:", today_ids)  # Printing today IDs to debug
        print("Yesterday IDs:", yesterday_ids)

        self.assertIn(self.thread_ids[0], today_ids)  # This should be today's thread
        self.assertIn(self.thread_ids[1], today_ids)  # This also should be today's thread
        self.assertIn(self.thread_ids[2], yesterday_ids)  # This should be yesterday's thread

    def test_group_threads_edge_case_future_date(self):
        edge_thread_id = str(uuid4())
        edge_user_id = str(uuid4())
        edge_assistant_id = str(uuid4())

        # Create a thread that is exactly at 12am UTC as an edge case
        edge_threads = [
            Thread(
                id=edge_thread_id,
                user_id=edge_user_id,
                assistant_id=edge_assistant_id,
                name="Thread 4",
                kwargs=None,
                created_at=datetime(2024, 6, 19, 0, 0, 0, tzinfo=timezone.utc),
                updated_at=datetime(2024, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
            )
        ]
        # Simulate UTC-5 timezone (offset -300 minutes); local time is 7pm of the previous day
        result = group_threads(edge_threads, -300)

        yesterday_ids = [str(thread.id) for thread in result["Yesterday"]]

        print("Yesterday IDs:", yesterday_ids)

        self.assertIn(edge_thread_id, yesterday_ids)

if __name__ == "__main__":
    unittest.main()
