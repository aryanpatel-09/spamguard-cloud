import json
import re

SPAM_RULES = [
    (re.compile(r"\b(won|winner|win|prize|lottery|jackpot|reward|gift card|free iphone|cash)\b", re.I), 32, "Prize / cash lure"),
    (re.compile(r"\b(claim now|act now|urgent|immediately|limited time|expires|last chance|hurry)\b", re.I), 24, "Urgency trigger"),
    (re.compile(r"\b(click this link|click here|tap here|verify now|login now|update kyc|kyc|suspended|blocked)\b", re.I), 28, "Phishing / account lure"),
    (re.compile(r"(https?://[^\s]+|bit\.ly|tinyurl\.com|goo\.gl|t\.co)", re.I), 18, "External / shortened URL"),
    (re.compile(r"\b(otp|pin|cvv|password|bank account|upi|credit card)\b", re.I), 22, "Sensitive credential request"),
    (re.compile(r"\b(reply yes|congratulations|selected|100% free|guaranteed|no cost)\b", re.I), 18, "Promotional spam phrasing"),
    (re.compile(r"[!]{2,}|[$₹]\s?\d{3,}"), 12, "Aggressive punctuation / money figure"),
]

SAFE_RULES = [
    (re.compile(r"\b(meeting|notes|agenda|project|schedule|tomorrow|homework|class|terraform|github|deploy)\b", re.I), -18, "Work / academic context"),
    (re.compile(r"\b(hey|hi|thanks|thank you|see you|let me know|coffee|lunch)\b", re.I), -14, "Normal conversational tone"),
]


def analyze_message(text: str) -> dict:
    clean = (text or "").strip()
    if not clean:
        return {"verdict": "Not spam", "confidence": 50, "signals": ["Empty message"]}

    score = 12
    signals = []

    for pattern, weight, label in SPAM_RULES:
        if pattern.search(clean):
            score += weight
            signals.append(label)

    letters = re.sub(r"[^a-zA-Z]", "", clean)
    if len(letters) >= 10:
        upper_count = sum(1 for ch in clean if ch.isupper())
        if upper_count / len(letters) > 0.45:
            score += 14
            signals.append("Excessive uppercase")

    for pattern, weight, label in SAFE_RULES:
        if pattern.search(clean):
            score += weight
            if not signals:
                signals.append(label)

    clamped = max(4, min(99, score))
    if clamped >= 55:
        verdict = "Spam"
        confidence = clamped
    elif clamped >= 36:
        verdict = "Suspicious"
        confidence = clamped + 15
    else:
        verdict = "Not spam"
        confidence = 100 - clamped

    if not signals:
        signals.append("No spam triggers found" if verdict == "Not spam" else "Mixed heuristic score")

    return {
        "verdict": verdict,
        "confidence": min(99, max(52, confidence)),
        "signals": signals,
    }


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    method = (
        event.get("requestContext", {}).get("http", {}).get("method")
        or event.get("httpMethod")
        or "POST"
    )
    if method == "OPTIONS":
        return _response(200, {"ok": True})

    try:
        raw_body = event.get("body") or "{}"
        payload = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
    except json.JSONDecodeError:
        return _response(400, {"error": "Invalid JSON payload"})

    message = (payload.get("message") or "").strip()
    if not message:
        return _response(400, {"error": "Field 'message' is required"})

    result = analyze_message(message)
    return _response(200, result)
