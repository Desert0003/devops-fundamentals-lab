"""خدمة الإبلاغ عن حادث بسيط - تطبيق تدريبي لبرنامج أساسيات هندسة DevOps.

Simple incident report service used across all course labs.
"""
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request

APP_VERSION = "1.1.0"
INCIDENT_TYPES = {"collision", "breakdown", "obstacle", "Sand Storm", "Flood", "other"}

app = Flask(__name__)
_reports = []


def validate_report(data):
    """Return a list of validation errors (empty list means valid)."""
    errors = []
    if not isinstance(data, dict):
        return ["body must be a JSON object"]
    location = str(data.get("location", "")).strip()
    if len(location) < 3:
        errors.append("location is required (3 characters or more)")
    if data.get("type") not in INCIDENT_TYPES:
        errors.append("type must be one of: " + ", ".join(sorted(INCIDENT_TYPES)))
    description = str(data.get("description", ""))
    if len(description) > 500:
        errors.append("description must be 500 characters or less")
    plate = str(data.get("plate", ""))
    if len(plate) > 10:
        errors.append("plate must be 10 characters or less")

    return errors


def create_report(data):
    report = {
        "id": len(_reports) + 1,
        "location": data["location"].strip(),
        "type": data["type"],
        "description": data.get("description", "").strip(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "plate": str(data.get("plate", "")).strip(),
    }
    _reports.append(report)
    return report


@app.get("/")
def index():
    return render_template("index.html", version=APP_VERSION, reports=list(reversed(_reports)))


@app.get("/health")
def health():
    return jsonify(status="ok", version=APP_VERSION)


@app.get("/api/reports")
def list_reports():
    return jsonify(_reports)


@app.post("/api/reports")
def add_report():
    data = request.get_json(silent=True)
    errors = validate_report(data)
    if errors:
        return jsonify(errors=errors), 400
    return jsonify(create_report(data)), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
