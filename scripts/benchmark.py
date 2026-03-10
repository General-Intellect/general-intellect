"""
Benchmark the LSH store at 10k memories.
Target: p99 query latency < 50ms

Usage:
    python -m scripts.benchmark
"""
import random
import statistics
import sys
import time

sys.path.insert(0, ".")

from server.memory.encoder import encoder
from server.memory.store import MemoryStore

CONTENTS = [
    "User prefers email over SMS for notifications",
    "Customer is on the Pro plan, renewing in March",
    "User has two dogs named Max and Bella",
    "Billing address is in Austin, Texas",
    "User speaks Spanish and English",
    "Preferred contact time is after 5pm EST",
    "Account was created in 2022",
    "User is interested in enterprise features",
    "Last support ticket was about API rate limits",
    "User wants to be notified about new model releases",
]

QUERIES = [
    "what are this user's notification preferences?",
    "when does their subscription renew?",
    "what pets does the user have?",
    "where is the user located?",
    "what language does the user speak?",
]


def main():
    print("Loading encoder model...")
    encoder.load()
    print("Model loaded.\n")

    store = MemoryStore()
    n = 10_000

    print(f"Writing {n:,} memories...")
    t0 = time.time()
    for i in range(n):
        store.write(
            agent_id="bench-agent",
            namespace="bench-ns",
            content=random.choice(CONTENTS) + f" (record {i})",
            metadata={"i": i},
        )
    write_elapsed = time.time() - t0
    print(f"Write complete: {write_elapsed:.2f}s ({write_elapsed / n * 1000:.2f}ms/write)\n")

    print("Running 200 queries...")
    latencies = []
    for _ in range(200):
        query = random.choice(QUERIES)
        t0 = time.perf_counter()
        store.query(agent_id="bench-agent", namespace="bench-ns", query=query, top_k=3)
        latencies.append((time.perf_counter() - t0) * 1000)

    latencies.sort()
    print(f"  p50:  {statistics.median(latencies):.1f}ms")
    print(f"  p95:  {latencies[int(len(latencies) * 0.95)]:.1f}ms")
    print(f"  p99:  {latencies[int(len(latencies) * 0.99)]:.1f}ms")
    print(f"  max:  {max(latencies):.1f}ms")

    p99 = latencies[int(len(latencies) * 0.99)]
    if p99 < 50:
        print(f"\n  PASS — p99 {p99:.1f}ms < 50ms target")
    else:
        print(f"\n  FAIL — p99 {p99:.1f}ms exceeds 50ms target")


if __name__ == "__main__":
    main()
