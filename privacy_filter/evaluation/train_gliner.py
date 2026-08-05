"""
GLiNER model fine-tuning script for FinTech Privacy Filter.
Converts dataset annotations to token-level spans and trains the model.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
import spacy

# Add project root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from gliner import GLiNER
from gliner.training import Trainer, TrainingArguments
from gliner.data_processing.collator import SpanDataCollator

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

nlp = spacy.blank("xx")  # Multilingual blank tokenizer


def find_offsets(text, entity_text):
    """Finds character start and end index of a substring in a text."""
    start = text.find(entity_text)
    if start == -1:
        return None
    return start, start + len(entity_text)


def convert_to_gliner_format(text, entities_raw):
    """Converts raw character-level annotations to GLiNER's expected token-level format."""
    doc = nlp(text)
    tokenized_text = [token.text for token in doc]

    ner_spans = []
    for ent in entities_raw:
        offsets = find_offsets(text, ent["text"])
        if not offsets:
            continue
        start_char, end_char = offsets
        start_token = None
        end_token = None

        # Exact matching boundary
        for token in doc:
            if token.idx == start_char:
                start_token = token.i
            if token.idx + len(token) == end_char:
                end_token = token.i

        # Relaxed matching fallback if token boundaries differ
        if start_token is None or end_token is None:
            for token in doc:
                if token.idx >= start_char and start_token is None:
                    start_token = token.i
                if token.idx + len(token) <= end_char:
                    end_token = token.i

        if start_token is not None and end_token is not None:
            ner_spans.append([start_token, end_token, ent["label"].lower()])

    return {"tokenized_text": tokenized_text, "ner": ner_spans}


def run_training(dataset_path: str, output_dir: str, limit: int, epochs: int, batch_size: int):
    """Prepares dataset and runs the fine-tuning loop."""
    logger.info("Loading training dataset from %s...", dataset_path)
    if not os.path.exists(dataset_path):
        logger.error("Dataset not found: %s", dataset_path)
        return

    train_data = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if limit is not None and i >= limit:
                break
            sample = json.loads(line)
            formatted = convert_to_gliner_format(sample["text"], sample["entities"])
            train_data.append(formatted)

    logger.info("Prepared %d samples for training.", len(train_data))

    logger.info("Loading base GLiNER model 'urchade/gliner_large-v2.1'...")
    model = GLiNER.from_pretrained("urchade/gliner_large-v2.1")

    logger.info("Configuring training arguments...")
    training_args = TrainingArguments(
        output_dir=output_dir,
        learning_rate=5e-5,
        per_device_train_batch_size=batch_size,
        num_train_epochs=epochs,
        weight_decay=0.01,
        logging_steps=1,
        save_strategy="no",
        report_to="none"
    )

    logger.info("Initializing SpanDataCollator and Trainer...")
    collator = SpanDataCollator(model.config, data_processor=model.data_processor)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_data,
        data_collator=collator
    )

    logger.info("Starting GLiNER fine-tuning...")
    trainer.train()

    logger.info("Fine-tuning completed. Saving model to %s...", output_dir)
    trainer.save_model(output_dir)
    logger.info("Model saved successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune GLiNER model.")
    parser.add_argument(
        "--dataset-path",
        type=str,
        default=r"C:\Users\SIMRAN\Downloads\gold_standard_fintech_200.jsonl",
        help="Path to JSONL dataset.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(PROJECT_ROOT / "privacy_filter" / "detectors" / "finetuned_gliner"),
        help="Directory to save the fine-tuned model.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Limit number of dataset rows used for training (for speed).",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=1,
        help="Number of training epochs.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=2,
        help="Batch size for training.",
    )

    args = parser.parse_args()
    run_training(args.dataset_path, args.output_dir, args.limit, args.epochs, args.batch_size)
