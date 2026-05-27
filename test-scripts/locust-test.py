import random
import json
import pathlib
from locust import HttpUser, task, between
from typing import List, Dict

# Load URLs at module level — simpler and avoids EventHook issues
URLS_POOL = []

data_path = pathlib.Path(__file__).parent.parent / "data" / "evaluation_dataset.json"
try:
    with open(data_path, "r", encoding="utf-8") as f:
        data: List[Dict] = json.load(f)
    URLS_POOL = [entry["url"] for entry in data]
    print(f"Loaded {len(URLS_POOL)} URLs for testing.")
except FileNotFoundError:
    print("evaluation_dataset.json not found — using fallback URLs.")
    URLS_POOL = [
        "google.com", "detik.com", "github.com",
        "bola88.com", "slot777.com", "pokerstars.com",
    ]


class GameblessUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.plain_headers = {
            "Content-Type": "application/json",
        }

    @task(5)
    def check_domain(self):
        """Most frequent task — mimics browser extension checking a URL."""
        url = random.choice(URLS_POOL)
        with self.client.get(
            f"/api/v1/domains/check?url={url}",
            headers=self.plain_headers,
            name="/api/v1/domains/check",
            catch_response=True,
        ) as response:
            if response.status_code == 500:
                response.failure(f"500 error: {response.text[:100]}")
            elif response.elapsed.total_seconds() > 3:
                response.failure("Slow response > 3s")
            else:
                response.success()