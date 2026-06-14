import re

from scrapers.utils import make_question_record

OPTION_RE = re.compile(r"^[A-Da-d][\).:\-]\s*(.+)$")
ANSWER_RE = re.compile(
    r"(?i)(?:✅\s*)?(?:correct\s*(?:answer|option)|answer)\s*[:\-]?\s*([A-Da-d])\b"
)
NUMBERED_QUESTION_RE = re.compile(r"^\d+[\).:\-]\s*(.+)$")
SKIP_LINE_RE = re.compile(
    r"^(enroll now|share|comments?|discuss|tags?:|related articles|popular programs|"
    r"explore courses|home\s*[›>]|updated on|gyansetu team|web development).*$",
    re.I,
)
EMOJI_SECTION_RE = re.compile(r"^[\U0001F300-\U0001FAFF🔸]\s*(.+)$")
QUIZ_SECTION_RE = re.compile(r"^[A-Z][A-Za-z0-9 /+()&\-]+ Quiz$")


def _extract_subdomain(line):
    text = line.strip()
    emoji_match = EMOJI_SECTION_RE.match(text)
    if emoji_match:
        return emoji_match.group(1).strip()
    if QUIZ_SECTION_RE.match(text):
        return text.replace(" Quiz", "").strip()
    return ""


def _normalize_option_lines(lines):
    options = {}
    for line in lines:
        match = OPTION_RE.match(line.strip())
        if not match:
            continue
        letter = line.strip()[0].upper()
        options[letter] = match.group(1).strip()
    ordered = [options.get(letter, "") for letter in ("A", "B", "C", "D")]
    if not any(ordered):
        return None
    return ordered


def parse_mcqs_from_lines(lines, domain="", default_subdomain="", metadata=None):
    metadata = metadata or {}
    questions = []
    question_lines = []
    option_lines = []
    current_subdomain = default_subdomain or metadata.get("subdomain", "")

    def flush_question(answer_letter="", explanation=""):
        nonlocal question_lines, option_lines
        options = _normalize_option_lines(option_lines)
        question = " ".join(question_lines).strip()
        if question and options:
            questions.append(
                make_question_record(
                    question,
                    options,
                    answer_letter,
                    explanation,
                    domain=domain or metadata.get("domain", ""),
                    subdomain=current_subdomain,
                    company_tags=metadata.get("companyTags"),
                )
            )
        question_lines = []
        option_lines = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line or SKIP_LINE_RE.match(line):
            continue

        subdomain = _extract_subdomain(line)
        if subdomain and not option_lines:
            current_subdomain = subdomain
            question_lines = []
            continue

        answer_match = ANSWER_RE.search(line)
        if answer_match and option_lines:
            flush_question(answer_match.group(1).upper())
            continue

        if OPTION_RE.match(line):
            option_lines.append(line)
            continue

        if option_lines:
            numbered = NUMBERED_QUESTION_RE.match(line)
            if numbered:
                flush_question()
                question_lines = [numbered.group(1).strip()]
            else:
                question_lines.append(line)
            option_lines = []
            continue

        numbered = NUMBERED_QUESTION_RE.match(line)
        if numbered:
            question_lines = [numbered.group(1).strip()]
        else:
            question_lines.append(line)

    return questions
