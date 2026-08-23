"""Locust Load Testing Suite for MemeGPT.
Specification: 10_Testing/Load_Tests.md
"""

from locust import HttpUser, task, between


class MemeGPTUser(HttpUser):
    """Simulates a typical MemeGPT user session."""
    wait_time = between(1, 3)  # 1-3 seconds between actions

    @task(10)  # 10x weight — most common action
    def search_meme(self):
        self.client.post("/api/v1/search", json={
            "query": "Monday morning feeling",
            "format_preference": "gif",
            "limit": 5
        })

    @task(5)
    def view_trending(self):
        self.client.get("/api/v1/trending?category=all&limit=20")

    @task(3)
    def view_meme_detail(self):
        self.client.get("/api/v1/memes/this-is-fine")

    @task(2)
    def submit_feedback(self):
        self.client.post("/api/v1/feedback", json={
            "query_id": "q_loadtest",
            "meme_id": "meme_042",
            "action": "download"
        })

    @task(1)
    def health_check(self):
        self.client.get("/health")
