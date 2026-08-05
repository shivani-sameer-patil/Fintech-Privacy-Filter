"""
Evaluation runner for FinTech Privacy Filter.
Compares pipeline predictions against ground truth dataset labels.
"""

import argparse
import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

from privacy_filter.detectors.pipeline import FinTechPrivacyPipeline

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Normalize pipeline and ground truth labels to a unified standard for comparison
LABEL_MAPPING: Dict[str, str] = {
    "ACCOUNT_NUMBER": "BANK_ACCOUNT",
    "ORG": "ORGANIZATION",
}

LANGUAGE_MAP: Dict[str, str] = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    "ml": "Malayalam",
    "gu": "Gujarati",
    "bn": "Bengali",
    "or": "Odia",
    "pa": "Punjabi",
    "as": "Assamese",
    "ur": "Urdu",
}


def normalize_label(label: str) -> str:
    """Normalizes an entity label string."""
    lbl = str(label).upper().strip()
    return LABEL_MAPPING.get(lbl, lbl)


def evaluate_document(
    gt_entities: List[Dict], pred_entities: List
) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]], List[Tuple[str, str]]]:
    """Compares predictions with ground-truth entities using exact text and normalized label matching.

    Returns:
        tp_list: Matched entity pairs (True Positives)
        fp_list: Unmatched predictions (False Positives)
        fn_list: Unmatched ground truths (False Negatives)
    """
    gt_list = [(e["text"].strip(), normalize_label(e["label"])) for e in gt_entities]
    pred_list = [(e.text.strip(), normalize_label(e.type)) for e in pred_entities]

    tp_matched = []
    fp_matched = []

    # Copy list for matching
    gt_remaining = list(gt_list)

    for pred in pred_list:
        pred_text, pred_label = pred
        # Find first exact match in gt_remaining
        match_idx = -1
        for idx, gt in enumerate(gt_remaining):
            gt_text, gt_label = gt
            if pred_text == gt_text and pred_label == gt_label:
                match_idx = idx
                break

        if match_idx != -1:
            tp_matched.append((pred_text, pred_label))
            gt_remaining.pop(match_idx)
        else:
            fp_matched.append((pred_text, pred_label))

    fn_matched = list(gt_remaining)

    return tp_matched, fp_matched, fn_matched


def update_counter(counters: Dict[str, Dict[str, int]], key: str, metric: str) -> None:
    """Helper to update metric counts in nested dict."""
    if key not in counters:
        counters[key] = {"tp": 0, "fp": 0, "fn": 0}
    counters[key][metric] += 1


def compute_metrics(tp: int, fp: int, fn: int) -> Dict[str, any]:
    """Computes standard precision, recall, and F1-score metrics."""
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return {
        "True Positives": tp,
        "False Positives": fp,
        "False Negatives": fn,
        "Precision": round(precision, 4),
        "Recall": round(recall, 4),
        "F1-Score": round(f1, 4),
    }


def run_evaluation(dataset_path: str, limit: int, output_dir: str) -> None:
    """Executes full evaluation on the dataset and saves report outputs."""
    logger.info("Initializing Fintech Privacy Filter pipeline...")
    pipeline = FinTechPrivacyPipeline()

    logger.info("Loading evaluation dataset from %s...", dataset_path)
    if not os.path.exists(dataset_path):
        logger.error("Dataset file not found: %s", dataset_path)
        return

    entity_counters: Dict[str, Dict[str, int]] = {}
    language_counters: Dict[str, Dict[str, int]] = {}

    total_tp = 0
    total_fp = 0
    total_fn = 0

    error_analysis_rows: List[Dict] = []
    processed_count = 0
    start_time = time.perf_counter()

    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            if limit is not None and processed_count >= limit:
                break

            sample = json.loads(line)
            doc_id = sample.get("id", processed_count + 1)
            lang_code = sample.get("language", "unknown")
            lang_name = LANGUAGE_MAP.get(lang_code, lang_code)
            text = sample.get("text", "")
            gt_entities = sample.get("entities", [])

            # Run pipeline
            pipeline_output = pipeline.process(text)
            pred_entities = pipeline_output.detected_entities

            # Run evaluation matching
            tp_list, fp_list, fn_list = evaluate_document(gt_entities, pred_entities)

            # Update overall scores
            total_tp += len(tp_list)
            total_fp += len(fp_list)
            total_fn += len(fn_list)

            # Update entity-level counters
            for _, label in tp_list:
                update_counter(entity_counters, label, "tp")
            for _, label in fp_list:
                update_counter(entity_counters, label, "fp")
            for _, label in fn_list:
                update_counter(entity_counters, label, "fn")

            # Update language-level counters
            for _ in tp_list:
                update_counter(language_counters, lang_name, "tp")
            for _ in fp_list:
                update_counter(language_counters, lang_name, "fp")
            for _ in fn_list:
                update_counter(language_counters, lang_name, "fn")

            # Process Error Analysis categories (WRONG_LABEL, MISS, FALSE_POSITIVE)
            unmatched_gt = list(fn_list)
            unmatched_pred = list(fp_list)

            # 1. Resolve WRONG_LABEL: exact match of text, different label
            for gt_item in list(unmatched_gt):
                gt_text, gt_label = gt_item
                match_pred = None
                for pred_item in unmatched_pred:
                    p_text, p_label = pred_item
                    if p_text == gt_text:
                        match_pred = pred_item
                        break

                if match_pred:
                    error_analysis_rows.append({
                        "document_id": doc_id,
                        "language": lang_name,
                        "ground_truth": f"{gt_text}:{gt_label}",
                        "prediction": f"{match_pred[0]}:{match_pred[1]}",
                        "error_type": "WRONG_LABEL",
                    })
                    unmatched_gt.remove(gt_item)
                    unmatched_pred.remove(match_pred)

            # 2. Resolve MISS: Ground truths not predicted at all
            for gt_item in unmatched_gt:
                error_analysis_rows.append({
                    "document_id": doc_id,
                    "language": lang_name,
                    "ground_truth": f"{gt_item[0]}:{gt_item[1]}",
                    "prediction": "",
                    "error_type": "MISS",
                })

            # 3. Resolve FALSE_POSITIVE: Predictions that do not exist in ground truths
            for pred_item in unmatched_pred:
                error_analysis_rows.append({
                    "document_id": doc_id,
                    "language": lang_name,
                    "ground_truth": "",
                    "prediction": f"{pred_item[0]}:{pred_item[1]}",
                    "error_type": "FALSE_POSITIVE",
                })

            processed_count += 1
            if processed_count % 100 == 0:
                logger.info("Processed %d documents...", processed_count)

    elapsed_time = time.perf_counter() - start_time
    logger.info("Processed %d documents in %.2f seconds.", processed_count, elapsed_time)

    # 1. Compute entity metrics DataFrame
    entity_rows = []
    for entity_type, counts in entity_counters.items():
        metrics = compute_metrics(counts["tp"], counts["fp"], counts["fn"])
        entity_rows.append({
            "Entity Type": entity_type,
            **metrics
        })
    entity_df = pd.DataFrame(entity_rows) if entity_rows else pd.DataFrame(
        columns=["Entity Type", "True Positives", "False Positives", "False Negatives", "Precision", "Recall", "F1-Score"]
    )
    if not entity_df.empty:
        entity_df = entity_df.sort_values(by="F1-Score", ascending=False)

    # 2. Compute language metrics DataFrame (ensuring all target languages are present)
    language_rows = []
    target_languages = list(LANGUAGE_MAP.values())
    for lang in target_languages:
        counts = language_counters.get(lang, {"tp": 0, "fp": 0, "fn": 0})
        metrics = compute_metrics(counts["tp"], counts["fp"], counts["fn"])
        language_rows.append({
            "Language": lang,
            **metrics
        })
    # Capture any unexpected languages not in standard map
    for lang, counts in language_counters.items():
        if lang not in target_languages:
            metrics = compute_metrics(counts["tp"], counts["fp"], counts["fn"])
            language_rows.append({
                "Language": lang,
                **metrics
            })
    language_df = pd.DataFrame(language_rows)

    # 3. Compute error analysis DataFrame
    error_df = pd.DataFrame(error_analysis_rows) if error_analysis_rows else pd.DataFrame(
        columns=["document_id", "language", "ground_truth", "prediction", "error_type"]
    )

    # 4. Save outputs
    os.makedirs(output_dir, exist_ok=True)

    # Save overall JSON report
    overall_metrics = compute_metrics(total_tp, total_fp, total_fn)
    report_data = {
        "configuration": {
            "dataset_path": dataset_path,
            "limit": limit,
            "total_documents_processed": processed_count,
            "execution_time_seconds": round(elapsed_time, 2),
        },
        "overall_metrics": overall_metrics,
    }

    report_path = os.path.join(output_dir, "evaluation_report.json")
    with open(report_path, "w", encoding="utf-8") as json_f:
        json.dump(report_data, json_f, indent=2)

    # Save CSVs
    entity_df.to_csv(os.path.join(output_dir, "entity_metrics.csv"), index=False)
    language_df.to_csv(os.path.join(output_dir, "language_metrics.csv"), index=False)
    error_df.to_csv(os.path.join(output_dir, "error_analysis.csv"), index=False)

    logger.info("Saved evaluation files to directory: %s", output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Fintech Privacy Filter.")
    parser.add_argument(
        "--dataset-path",
        type=str,
        default=r"C:\Users\SIMRAN\Downloads\multilingual_fintech_dataset_10000.jsonl",
        help="Path to JSONL evaluation dataset.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of processed dataset records.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(Path(__file__).resolve().parent),
        help="Directory to save evaluation reports and CSVs.",
    )

    args = parser.parse_args()
    run_evaluation(args.dataset_path, args.limit, args.output_dir)
