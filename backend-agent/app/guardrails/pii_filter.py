import re


PII_PATTERNS = [
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("phone_mobile", re.compile(r"1[3-9]\d{9}")),
    ("phone_landline", re.compile(r"\d{3,4}-\d{7,8}")),
    ("id_card", re.compile(r"\d{17}[\dXx]")),
]


def detect_and_filter_pii(text: str) -> tuple[str, list[dict]]:
    detections = []
    filtered = text or ""

    for pii_type, pattern in PII_PATTERNS:
        for match in pattern.finditer(text or ""):
            detections.append(
                {
                    "type": pii_type,
                    "value": match.group(),
                    "position": match.span(),
                }
            )

    for detection in sorted(detections, key=lambda item: item["position"][0], reverse=True):
        start, end = detection["position"]
        filtered = filtered[:start] + "[已隐藏]" + filtered[end:]

    return filtered, detections
