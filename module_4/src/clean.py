"""Clean raw Grad Cafe records into the Module 3 schema."""

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_FILE = BASE_DIR / "applicant_data.json"
OUTPUT_FILE = BASE_DIR / "applicant_data_for_llm.json"
DEGREES = ["Masters", "PhD", "MBA", "MFA", "JD", "PsyD", "EdD", "Other"]

ENTRY_PATTERN = re.compile(
    r"(?P<university>[^\n]+)\n"
    r"(?P<program>[^\n]+?(?:Masters|PhD|MBA|MFA|JD|PsyD|EdD|Other))\n"
    r"(?P<date_added>[A-Z][a-z]+ \d{1,2}, \d{4})\n"
    r"(?P<status>(?:Accepted|Rejected|Wait listed|Interview)"
    r" on [A-Z][a-z]+ \d{1,2})\n"
    r"Total comments\n"
    r"(?P<term>(?:Fall|Spring|Summer|Winter) \d{4})\n"
    r"(?P<student_type>American|International|Other)"
    r"(?P<extra>(?:\n(?![A-Z][^\n]+\n[^\n]+"
    r"(?:Masters|PhD|MBA|MFA|JD|PsyD|EdD|Other)\n"
    r"[A-Z][a-z]+ \d{1,2}, \d{4}).*)*)",
    re.MULTILINE,
)


def extract_metric(label, text):
    """Return the metric following ``label``, or an empty string."""
    match = re.search(rf"\b{label}\s+([0-9.]+)", text)
    return match.group(1) if match else ""


def clean_records(records):
    """Extract unique structured applicants from raw page text."""
    cleaned = []
    seen_programs = set()

    for record in records:
        raw_text = record.get("raw_text", "")

        for match in ENTRY_PATTERN.finditer(raw_text):
            program_line = match.group("program").strip()
            extra = match.group("extra") or ""
            degree = next(
                (item for item in DEGREES if program_line.endswith(item)),
                "",
            )
            comments = ""

            for line in extra.split("\n"):
                line = line.strip()
                if not line:
                    continue
                if line.startswith(("GPA", "GRE")):
                    continue
                if line in ["American", "International", "Other"]:
                    continue
                if re.match(r"(Fall|Spring|Summer|Winter)\s+\d{4}", line):
                    continue
                comments = line
                break

            output_record = {
                "program": (
                    f"{program_line}, {match.group('university').strip()}"
                ),
                "comments": comments,
                "date_added": match.group("date_added").strip(),
                "url": record.get("url"),
                "status": match.group("status").strip(),
                "term": match.group("term").strip(),
                "US/International": match.group("student_type").strip(),
                "GPA": extract_metric("GPA", extra),
                "GRE": extract_metric("GRE", extra),
                "GRE V": extract_metric("GRE V", extra),
                "GRE AW": extract_metric("GRE AW", extra),
                "Degree": degree,
            }
            record_key = (
                output_record["program"],
                output_record["date_added"],
                output_record["status"],
            )

            if record_key not in seen_programs:
                cleaned.append(output_record)
                seen_programs.add(record_key)

    return cleaned


def clean_file(input_file=INPUT_FILE, output_file=OUTPUT_FILE):
    """Read raw JSON, clean it, and write cleaned JSON."""
    with Path(input_file).open(encoding="utf-8") as file:
        records = json.load(file)

    cleaned = clean_records(records)

    with Path(output_file).open("w", encoding="utf-8") as file:
        json.dump(cleaned, file, indent=4)

    return cleaned


if __name__ == "__main__":  # pragma: no cover - command-line helper
    results = clean_file()
    print(f"Saved {len(results)} cleaned records to {OUTPUT_FILE}")
