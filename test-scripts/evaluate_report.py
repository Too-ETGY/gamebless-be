import asyncio
import json
import pathlib
import time
import logging
from typing import List, Dict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
DATASET_PATH = pathlib.Path(__file__).parent.parent / "data" / "evaluation_dataset.json"

# FastAPI service imports
from app.db.firebase import init_firebase, get_firestore
from app.db.repositories.domain_repo import DomainRepository
from app.services.domain_service import report_domain

async def evaluate_entry(url: str) -> bool:
    """Check if a URL is blocked using the fast check service.
    Returns True if the domain is considered gambling (blocked)."""
    repo: DomainRepository = DomainRepository(get_firestore())
    return await report_domain(url, repo)

async def evaluate_async() -> None:
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data: List[Dict] = json.load(f)

    tp = fp = tn = fn = 0
    request_counter = 0
    max_requests_per_day = 34  # free tier daily limit (now increased to 40)
    min_interval = 60 / 5  # 5 requests per minute => 12 seconds
    for entry in data:
        # enforce daily limit
        if request_counter >= max_requests_per_day:
            logger.warning("Reached daily Gemini request limit (20) – stopping evaluation")
            break
        # enforce rpm limit
        now = time.time()
        if request_counter > 0:
            elapsed = now - evaluate_async.last_time
            sleep_needed = max(0, min_interval - elapsed)
            if sleep_needed > 0:
                await asyncio.sleep(sleep_needed)
        evaluate_async.last_time = time.time()

        true_label: bool = entry.get("is_gambling", False)
        pred_label: bool = await evaluate_entry(entry["url"])
        request_counter += 1
        if pred_label and true_label:
            tp += 1
        elif pred_label and not true_label:
            fp += 1
        elif not pred_label and not true_label:
            tn += 1
        else:
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    print("--- Evaluation Results ---")
    print(f"Total samples: {len(data)}")
    print(f"TP: {tp}, FP: {fp}, TN: {tn}, FN: {fn}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")

if __name__ == "__main__":
    init_firebase()
    evaluate_async.last_time = 0
    asyncio.run(evaluate_async())
