"""
FinTech Privacy Filter Benchmarking Framework.

Measures Precision, Recall, F1-Score, Throughput, and Latencies
across English and native Indian language documents.
Generates an automated Markdown report with performance metrics.
"""

import os
import sys
import time
import tracemalloc
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple

# Add project root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from privacy_filter.detectors.pipeline import FinTechPrivacyPipeline

# Representative test dataset for validation
BENCHMARK_DATASET = [
    {
        "text": "My Aadhaar card number is 2345 6789 0123. Please check it.",
        "expected": [{"type": "AADHAAR", "text": "2345 6789 0123"}]
    },
    {
        "text": "Send the OTP 482910 to verify my bank account ending in 9876543210.",
        "expected": [
            {"type": "OTP", "text": "482910"},
            {"type": "ACCOUNT_NUMBER", "text": "9876543210"}
        ]
    },
    {
        "text": "Here is my card number: 4111 2222 3333 4444 and CVV is 123.",
        "expected": [
            {"type": "CARD", "text": "4111 2222 3333 4444"},
            {"type": "CVV", "text": "123"}
        ]
    },
    {
        "text": "श्री राजेश कुमार का मोबाइल नंबर 9876543210 है।",
        "expected": [
            {"type": "PERSON", "text": "श्री राजेश कुमार"},
            {"type": "PHONE", "text": "9876543210"}
        ]
    },
    {
        "text": "Please transfer 5000 rupees to upi handle rajesh@okaxis.",
        "expected": [
            {"type": "AMOUNT", "text": "5000 rupees"},
            {"type": "UPI", "text": "rajesh@okaxis"}
        ]
    },
    {
        "text": "ಕನ್ನಡದಲ್ಲಿ ನನ್ನ ಹೆಸರು ಶ್ರೀಮತಿ ಲತಾ ಕುಮಾರಿ. ನನ್ನ ಆಧಾರ್ ಸಂಖ್ಯೆ 234567890123.",
        "expected": [
            {"type": "PERSON", "text": "ಶ್ರೀಮತಿ ಲತಾ ಕುಮಾರಿ"},
            {"type": "AADHAAR", "text": "234567890123"}
        ]
    },
    {
        "text": "This is a random 12 digit number: 987612345098 which is my loan account.",
        "expected": [{"type": "LOAN_ACCOUNT", "text": "987612345098"}]
    },
    {
        "text": "User admin logged in with password SecretPass123! and PIN 4821.",
        "expected": [
            {"type": "PASSWORD", "text": "SecretPass123!"},
            {"type": "MPIN", "text": "4821"}
        ]
    }
]


def evaluate_metrics(detected: List[Dict[str, Any]], expected: List[Dict[str, Any]]) -> Tuple[int, int, int]:
    """Calculates True Positives, False Positives, and False Negatives."""
    tp, fp, fn = 0, 0, 0
    
    # Map by (type, text)
    det_set = {(e["type"], e["text"].strip()) for e in detected}
    exp_set = {(e["type"], e["text"].strip()) for e in expected}

    # True Positives: matches in both
    tp = len(det_set.intersection(exp_set))
    
    # False Positives: detected but not expected
    fp = len(det_set - exp_set)
    
    # False Negatives: expected but not detected
    fn = len(exp_set - det_set)
    
    return tp, fp, fn


def run_benchmark():
    print("Initializing FinTech Privacy Pipeline...")
    pipeline = FinTechPrivacyPipeline()

    total_tp, total_fp, total_fn = 0, 0, 0
    latencies = []
    total_chars = 0
    
    # Track RAM usage
    tracemalloc.start()
    mem_start, _ = tracemalloc.get_traced_memory()
    
    start_time = time.perf_counter()

    for idx, item in enumerate(BENCHMARK_DATASET):
        text = item["text"]
        total_chars += len(text)
        
        # Profile single run latency
        t_start = time.perf_counter()
        output = pipeline.process(text)
        t_end = time.perf_counter()
        
        latency = (t_end - t_start) * 1000.0
        latencies.append(latency)

        # Convert detected entities to comparable format
        detected_entities = [{"type": e.type, "text": e.text} for e in output.detected_entities]
        
        print(f"Doc {idx}: {ascii(text)}")
        print(f"  Detected: {ascii(detected_entities)}")
        print(f"  Expected: {ascii(item['expected'])}")
        
        tp, fp, fn = evaluate_metrics(detected_entities, item["expected"])
        total_tp += tp
        total_fp += fp
        total_fn += fn

    total_duration = time.perf_counter() - start_time
    mem_end, mem_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Calculations
    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    avg_latency = sum(latencies) / len(latencies)
    latencies_sorted = sorted(latencies)
    p50 = latencies_sorted[len(latencies_sorted) // 2]
    p95 = latencies_sorted[int(len(latencies_sorted) * 0.95)]
    p99 = latencies_sorted[int(len(latencies_sorted) * 0.99)]
    
    throughput_docs = len(BENCHMARK_DATASET) / total_duration
    throughput_chars = total_chars / total_duration
    ram_used_mb = (mem_peak - mem_start) / (1024 * 1024)

    # Generate Report
    report = f"""# FinTech Privacy Filter Benchmarking Report

Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Performance Telemetry Summary
| Metric | Value |
| :--- | :--- |
| **Precision** | {precision:.2%} |
| **Recall** | {recall:.2%} |
| **F1 Score** | {f1:.2%} |
| **Throughput (Docs/sec)** | {throughput_docs:.2f} doc/s |
| **Throughput (Chars/sec)** | {throughput_chars:.2f} char/s |
| **Peak Memory Allocation** | {ram_used_mb:.2f} MB |

## Latency Percentiles
| Percentile | Latency (ms) |
| :--- | :--- |
| **Average** | {avg_latency:.2f} ms |
| **P50 (Median)** | {p50:.2f} ms |
| **P95** | {p95:.2f} ms |
| **P99** | {p99:.2f} ms |

## Confusion Matrix Counts
- **True Positives (TP):** {total_tp}
- **False Positives (FP):** {total_fp}
- **False Negatives (FN):** {total_fn}

---
*Report auto-generated by the FinTech Privacy Filter benchmarking engine.*
"""
    
    # Save report to artifacts directory if running under GEMINI session
    artifacts_dir = Path("C:/Users/SIMRAN/.gemini/antigravity-ide/brain/a4f55c2d-99da-499e-87f6-f14404fefe84")
    if artifacts_dir.exists():
        report_file = artifacts_dir / "benchmark_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Benchmark report saved to: {report_file}")
    else:
        print("Artifacts directory not found. Printing report:")
        print(report)

    # Print clean summary to terminal
    print("\n================ BENCHMARK RESULTS ================")
    print(f"F1 Score:   {f1:.2%}")
    print(f"Precision:  {precision:.2%}")
    print(f"Recall:     {recall:.2%}")
    print(f"P50 Latency: {p50:.2f} ms")
    print(f"Peak RAM:   {ram_used_mb:.2f} MB")
    print("===================================================\n")


if __name__ == "__main__":
    run_benchmark()
