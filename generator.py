import json
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# ==========================================
# CONFIG
# ==========================================

load_dotenv(Path(__file__).parent / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise Exception(
        "Set GEMINI_API_KEY in .env file or as an environment variable"
    )

client = genai.Client(api_key=API_KEY)

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
OUTPUT_DIR = "output"

Path(OUTPUT_DIR).mkdir(exist_ok=True)

# ==========================================
# TOPICS
# ==========================================

TOPICS = {
    "frontend": [
        "JavaScript Fundamentals",
        "Hoisting",
        "Closures",
        "Scope Chain",
        "Prototype Inheritance",
        "Execution Context",
        "Promises",
        "Async Await",
        "Event Loop",
        "Microtask vs Macrotask",
    ],
    "backend": [
        "HTTP Methods",
        "HTTP Headers",
        "Status Codes",
        "REST APIs",
        "API Design",
        "JWT",
        "OAuth",
        "Cookies",
        "Sessions",
        "Authentication",
    ],
    "react": [
        "Components",
        "Props",
        "State",
        "Hooks",
        "useEffect",
    ],
    "nodejs": [
        "Event Loop",
        "Streams",
        "Buffers",
        "Express",
        "Middleware",
    ],
    "database": [
        "SQL Basics",
        "Joins",
        "Normalization",
        "Indexes",
        "MongoDB",
    ],
}

DOMAIN_LABELS = {
    "frontend": "Full Stack Development",
    "backend": "Full Stack Development",
    "react": "Full Stack Development",
    "nodejs": "Full Stack Development",
    "database": "Full Stack Development",
}

# ==========================================
# PROMPT
# ==========================================

with open("prompt.txt", "r", encoding="utf-8") as f:
    MASTER_PROMPT = f.read()

# ==========================================
# HELPERS
# ==========================================


def extract_json(text):
    text = text.strip()
    text = re.sub(r"^```json", "", text, flags=re.MULTILINE)
    text = re.sub(r"```$", "", text, flags=re.MULTILINE)

    start = text.find("[")
    end = text.rfind("]")

    if start == -1 or end == -1:
        raise Exception("JSON not found in model response")

    return text[start : end + 1]


def normalize_questions(questions, domain, subdomain, topic):
    normalized = []
    for item in questions:
        record = {
            "domain": item.get("domain") or domain,
            "subdomain": item.get("subdomain") or subdomain,
            "topic": item.get("topic") or topic,
            "difficulty": item.get("difficulty", ""),
            "question": item.get("question", ""),
            "opt1": item.get("opt1", ""),
            "opt2": item.get("opt2", ""),
            "opt3": item.get("opt3", ""),
            "opt4": item.get("opt4", ""),
            "Correct Opt": item.get("Correct Opt", ""),
            "Explaination": item.get("Explaination", ""),
            "imageLink": item.get("imageLink", ""),
            "companyTags": item.get("companyTags") or [],
        }
        normalized.append(record)
    return normalized


def generate_topic(topic, domain, subdomain):
    prompt = (
        MASTER_PROMPT.replace("{{TOPIC}}", topic)
        .replace("{{DOMAIN}}", domain)
        .replace("{{SUBDOMAIN}}", subdomain)
    )

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )

    raw = response.text
    json_text = extract_json(raw)
    data = json.loads(json_text)
    return normalize_questions(data, domain, subdomain, topic)


# ==========================================
# MAIN
# ==========================================

all_questions = []

for subdomain, topics in TOPICS.items():
    domain = DOMAIN_LABELS.get(subdomain, "Full Stack Development")
    print(f"\nGenerating {subdomain} ({domain})")

    domain_questions = []

    for topic in topics:
        print(f"Topic -> {topic}")
        success = False

        for attempt in range(3):
            try:
                questions = generate_topic(topic, domain, subdomain)
                domain_questions.extend(questions)
                all_questions.extend(questions)
                success = True
                print(f"OK {len(questions)} questions")
                break
            except Exception as e:
                print(f"Retry {attempt + 1}: {e}")
                time.sleep(5)

        if not success:
            print(f"Failed topic {topic}")

        time.sleep(2)

    file_path = os.path.join(OUTPUT_DIR, f"{subdomain}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(domain_questions, f, indent=4, ensure_ascii=False)

    print(f"Saved {file_path}")

with open(os.path.join(OUTPUT_DIR, "all_questions.json"), "w", encoding="utf-8") as f:
    json.dump(all_questions, f, indent=4, ensure_ascii=False)

print("\nDONE")
print(f"Total Questions: {len(all_questions)}")
