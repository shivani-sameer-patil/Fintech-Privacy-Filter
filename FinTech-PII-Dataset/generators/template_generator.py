import argparse
import re
import json
from pathlib import Path

from variation_generator import vary
from utils import ENTITY_GENERATORS, PLACEHOLDER_PATTERN


def fill_template(template: str, language="english"):
    """
    Replace placeholders like {PERSON}, {PAN}, etc.
    and return the filled text along with entity annotations.
    """

    entities = []
    generated_cache = {}

    placeholders = re.findall(
        PLACEHOLDER_PATTERN,
        template
    )

    for placeholder in placeholders:

        if placeholder not in ENTITY_GENERATORS:
            print(f"Warning: No generator found for '{placeholder}'")
            continue

        # Generate entity only once per document
        generator = ENTITY_GENERATORS[placeholder]

        try:
            entity = generator(language)
        except TypeError:
            entity = generator()

        if entity is None:
            raise ValueError(
                f"Generator for '{placeholder}' returned None"
            )

        generated_cache[placeholder] = entity

        entity = generated_cache[placeholder]

        if isinstance(entity, str):
            value = entity
            label = None
        else:
            value = entity["value"]
            label = entity["label"]

        template = template.replace(
            "{" + placeholder + "}",
            value
        )

        if label is not None:
            entities.append(
                {
                    "text": value,
                    "label": label
                }
            )

    return template, entities


if __name__ == "__main__":

    SAMPLES_PER_TEMPLATE = 100

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--type",
        default="kyc",
        help="Document type"
    )

    parser.add_argument(
        "--language",
        default="english",
        choices=[
            "english",
            "hindi",
            "kannada"
        ],
        help="Dataset language"
    )

    args = parser.parse_args()

    template_folder = (
        Path("templates")
        / args.language
        / args.type
    )

    if not template_folder.exists():
        raise FileNotFoundError(
            f"Template folder '{template_folder}' not found."
        )

    template_files = sorted(
        template_folder.glob("*.txt")
    )

    output_path = Path(
        f"data/{args.language}_{args.type}.jsonl"
    )

    total_documents = 0

    with open(
        output_path,
        "w",
        encoding="utf8"
    ) as f:

        for template_file in template_files:

            original_template = template_file.read_text(
                encoding="utf8"
            )

            for _ in range(SAMPLES_PER_TEMPLATE):

                total_documents += 1

                template = original_template

                # Randomize labels
                template = vary(template)

                # Replace placeholders
                text, entities = fill_template(
                    template,
                    args.language
                )

                sample = {

                    "id":
                        f"{args.language}_{args.type}_{total_documents:06d}",

                    "language":
                        args.language,

                    "document_type":
                        args.type,

                    "source":
                        "synthetic",

                    "difficulty":
                        "easy",

                    "template":
                        template_file.name,

                    "text":
                        text,

                    "entities":
                        entities
                }

                f.write(
                    json.dumps(
                        sample,
                        ensure_ascii=False
                    )
                )

                f.write("\n")

    print("=" * 60)
    print("DATASET GENERATION COMPLETE")
    print("=" * 60)
    print(f"Language            : {args.language}")
    print(f"Document Type       : {args.type}")
    print(f"Templates Used      : {len(template_files)}")
    print(f"Samples per Template: {SAMPLES_PER_TEMPLATE}")
    print(f"Total Documents     : {total_documents}")
    print(f"Output File         : {output_path}")
    print("=" * 60)