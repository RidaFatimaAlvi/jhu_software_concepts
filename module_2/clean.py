import json
import re

INPUT_FILE = "module_2/applicant_data.json"
OUTPUT_FILE = "module_2/applicant_data_for_llm.json"

DEGREES = ["Masters", "PhD", "MBA", "MFA", "JD", "PsyD", "EdD", "Other"]

# This regex captures each applicant row from the rendered raw_text.
ENTRY_PATTERN = re.compile(
    r"(?P<university>[^\n]+)\n"
    r"(?P<program>[^\n]+?(?:Masters|PhD|MBA|MFA|JD|PsyD|EdD|Other))\n"
    r"(?P<date_added>[A-Z][a-z]+ \d{1,2}, \d{4})\n"
    r"(?P<status>(?:Accepted|Rejected|Wait listed|Interview) on [A-Z][a-z]+ \d{1,2})\n"
    r"Total comments\n"
    r"(?P<term>(?:Fall|Spring|Summer|Winter) \d{4})\n"
    r"(?P<student_type>American|International|Other)"
    r"(?P<extra>(?:\n(?![A-Z][^\n]+\n[^\n]+(?:Masters|PhD|MBA|MFA|JD|PsyD|EdD|Other)\n[A-Z][a-z]+ \d{1,2}, \d{4}).*)*)",
    re.MULTILINE,
)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    records = json.load(f)

cleaned = []
seen_programs = set()

for record in records:
    raw_text = record.get("raw_text", "")

    for match in ENTRY_PATTERN.finditer(raw_text):
        university = match.group("university").strip()
        program_line = match.group("program").strip()
        date_added = match.group("date_added").strip()
        status = match.group("status").strip()
        term = match.group("term").strip()
        student_type = match.group("student_type").strip()
        extra = match.group("extra") or ""

        degree = ""

        for d in DEGREES:
            if program_line.endswith(d):
                degree = d
                break

        gpa = ""
        gpa_match = re.search(r"\bGPA\s+([0-9.]+)", extra)
        if gpa_match:
            gpa = f"GPA {gpa_match.group(1)}"

        comments = ""

        for line in extra.split("\n"):
            line = line.strip()

            if not line:
                continue

            if line.startswith("GPA"):
                continue

            if line.startswith("GRE"):
                continue

            if line in ["American", "International", "Other"]:
                continue

            if re.match(r"(Fall|Spring|Summer|Winter)\s+\d{4}", line):
                continue

            comments = line
            break

        output_record = {
            "program": f"{program_line}, {university}",
            "comments": comments,
            "date_added": date_added,
            "url": record.get("url"),
            "status": status,
            "term": term,
            "US/International": student_type,
            "GPA": gpa,
            "Degree": degree
        }

        record_key = (
            output_record["program"],
            output_record["date_added"],
            output_record["status"]
        )

        if record_key not in seen_programs:
            cleaned.append(output_record)
            seen_programs.add(record_key)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(cleaned, f, indent=4)

print(f"Saved {len(cleaned)} cleaned records to {OUTPUT_FILE}")

if cleaned:
    print(json.dumps(cleaned[0], indent=4))