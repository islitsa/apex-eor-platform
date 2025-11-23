"""
Telemetry Server - Collects Real Usage Data from Generated Dashboards
This is the Opus pattern for learning from ACTUAL usage
"""

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path
import uvicorn

app = FastAPI(title="Dashboard Telemetry Server")

# Storage
TELEMETRY_DB = Path("data/learning/telemetry.json")
TELEMETRY_DB.parent.mkdir(parents=True, exist_ok=True)


class TelemetryEvent(BaseModel):
    """Telemetry event from generated dashboard"""
    generation_id: str
    event_type: str
    data: Dict[str, Any]
    timestamp: str


class FeedbackSubmission(BaseModel):
    """User feedback submission"""
    dashboard_id: str
    component_ratings: Dict[str, int]
    overall_rating: int
    comments: str
    patterns_used: list


def load_telemetry() -> Dict:
    """Load telemetry data"""
    if TELEMETRY_DB.exists():
        with open(TELEMETRY_DB, 'r') as f:
            return json.load(f)
    return {
        "dashboards": {},
        "events": [],
        "performance_metrics": {}
    }


def save_telemetry(data: Dict):
    """Save telemetry data"""
    with open(TELEMETRY_DB, 'w') as f:
        json.dump(data, f, indent=2)


@app.post("/telemetry")
async def receive_telemetry(event: TelemetryEvent, background_tasks: BackgroundTasks):
    """
    Receive telemetry from generated dashboards
    This is called automatically by injected code
    """

    print(f"[TELEMETRY] {event.event_type} from {event.generation_id}")

    # Process in background
    background_tasks.add_task(process_telemetry, event)

    return {"status": "received"}


@app.post("/feedback")
async def receive_feedback(feedback: FeedbackSubmission, background_tasks: BackgroundTasks):
    """
    Receive user feedback from dashboards
    This is the Opus learning system!
    """

    print(f"[FEEDBACK] Dashboard: {feedback.dashboard_id}, Overall: {feedback.overall_rating}/5")
    print(f"[FEEDBACK] Comments: {feedback.comments}")

    # Process in background
    background_tasks.add_task(process_feedback, feedback)

    return {"status": "received", "message": "Thank you for your feedback!"}


def process_telemetry(event: TelemetryEvent):
    """Process telemetry event"""

    telemetry = load_telemetry()

    # Initialize dashboard if needed
    if event.generation_id not in telemetry["dashboards"]:
        telemetry["dashboards"][event.generation_id] = {
            "created_at": event.timestamp,
            "events": [],
            "metrics": {
                "rendered": False,
                "render_time_ms": None,
                "button_clicks": 0,
                "errors": [],
                "interactions": []
            }
        }

    dashboard = telemetry["dashboards"][event.generation_id]

    # Record event
    dashboard["events"].append({
        "type": event.event_type,
        "data": event.data,
        "timestamp": event.timestamp
    })

    # Update metrics based on event type
    if event.event_type == "render_success":
        dashboard["metrics"]["rendered"] = True
        dashboard["metrics"]["render_time_ms"] = event.data.get("render_time_ms")

    elif event.event_type == "button_click":
        dashboard["metrics"]["button_clicks"] += 1
        dashboard["metrics"]["interactions"].append({
            "type": "click",
            "button": event.data.get("button"),
            "timestamp": event.timestamp
        })

    elif event.event_type == "error":
        dashboard["metrics"]["errors"].append(event.data)

    elif event.event_type == "refresh":
        dashboard["metrics"]["interactions"].append({
            "type": "refresh",
            "timestamp": event.timestamp
        })

    # Add to global events
    telemetry["events"].append({
        "generation_id": event.generation_id,
        "type": event.event_type,
        "timestamp": event.timestamp
    })

    # Save
    save_telemetry(telemetry)

    # Analyze for immediate issues
    analyze_for_issues(event.generation_id, dashboard)


def process_feedback(feedback: FeedbackSubmission):
    """Process user feedback"""

    # Load feedback database
    feedback_db_path = Path("data/learning/feedback.json")
    feedback_db_path.parent.mkdir(parents=True, exist_ok=True)

    if feedback_db_path.exists():
        with open(feedback_db_path, 'r') as f:
            feedback_db = json.load(f)
    else:
        feedback_db = {
            "submissions": [],
            "pattern_ratings": {},
            "component_averages": {}
        }

    # Add submission
    submission = {
        "dashboard_id": feedback.dashboard_id,
        "overall_rating": feedback.overall_rating,
        "component_ratings": feedback.component_ratings,
        "comments": feedback.comments,
        "patterns_used": feedback.patterns_used,
        "timestamp": datetime.now().isoformat()
    }

    feedback_db["submissions"].append(submission)

    # Update pattern ratings
    for pattern in feedback.patterns_used:
        if pattern not in feedback_db["pattern_ratings"]:
            feedback_db["pattern_ratings"][pattern] = {"ratings": [], "average": 0}

        feedback_db["pattern_ratings"][pattern]["ratings"].append(feedback.overall_rating)
        feedback_db["pattern_ratings"][pattern]["average"] = sum(
            feedback_db["pattern_ratings"][pattern]["ratings"]
        ) / len(feedback_db["pattern_ratings"][pattern]["ratings"])

    # Update component averages
    for component, rating in feedback.component_ratings.items():
        if component not in feedback_db["component_averages"]:
            feedback_db["component_averages"][component] = {"ratings": [], "average": 0}

        feedback_db["component_averages"][component]["ratings"].append(rating)
        feedback_db["component_averages"][component]["average"] = sum(
            feedback_db["component_averages"][component]["ratings"]
        ) / len(feedback_db["component_averages"][component]["ratings"])

    # Save
    with open(feedback_db_path, 'w') as f:
        json.dump(feedback_db, f, indent=2)

    # Print summary
    avg_rating = sum(feedback.component_ratings.values()) / len(feedback.component_ratings)
    print(f"[FEEDBACK SUMMARY] Avg Component Rating: {avg_rating:.2f}/5")
    print(f"[FEEDBACK SUMMARY] Total Submissions: {len(feedback_db['submissions'])}")

    # Check for low ratings (trigger improvement)
    if feedback.overall_rating <= 2:
        print(f"[ALERT] Low rating detected! Pattern needs improvement.")


def analyze_for_issues(generation_id: str, dashboard: Dict):
    """Immediate analysis for critical issues"""

    metrics = dashboard["metrics"]

    # Check for failures
    if not metrics["rendered"]:
        print(f"[ALERT] Dashboard {generation_id} failed to render!")

    if metrics["errors"]:
        print(f"[ALERT] Dashboard {generation_id} has {len(metrics['errors'])} errors:")
        for error in metrics["errors"][:3]:
            print(f"  - {error}")

    # Check for performance issues
    if metrics["render_time_ms"] and metrics["render_time_ms"] > 5000:
        print(f"[WARNING] Slow render: {metrics['render_time_ms']}ms")


@app.post("/feedback")
async def receive_feedback(feedback: FeedbackSubmission):
    """
    Receive user feedback ratings
    """

    print(f"[FEEDBACK] Received for {feedback.dashboard_id}")
    print(f"  Overall: {feedback.overall_rating}/5")
    print(f"  Components: {feedback.component_ratings}")

    # Load feedback system
    from src.learning.feedback_system import FeedbackSystem
    fs = FeedbackSystem()

    # Store feedback
    summary = fs.collect_dashboard_rating(
        dashboard_id=feedback.dashboard_id,
        component_ratings=feedback.component_ratings,
        overall_rating=feedback.overall_rating,
        comments=feedback.comments,
        patterns_used=feedback.patterns_used
    )

    print(f"  Overall avg now: {summary['overall_avg']:.1f}/5")

    # Check for improvements needed
    if feedback.overall_rating < 3:
        print(f"[ACTION] Low rating - triggering improvement analysis")
        recommendations = fs.get_improvement_recommendations()
        if recommendations:
            print(f"  Top priority: {recommendations[0]['suggestion']}")

    return {
        "status": "received",
        "summary": summary
    }


@app.get("/telemetry/dashboard/{generation_id}")
async def get_dashboard_telemetry(generation_id: str):
    """Get telemetry for a specific dashboard"""

    telemetry = load_telemetry()

    if generation_id not in telemetry["dashboards"]:
        return {"error": "Dashboard not found"}

    return telemetry["dashboards"][generation_id]


@app.get("/telemetry/summary")
async def get_telemetry_summary():
    """Get summary of all telemetry"""

    telemetry = load_telemetry()

    total_dashboards = len(telemetry["dashboards"])
    rendered_count = sum(1 for d in telemetry["dashboards"].values() if d["metrics"]["rendered"])
    total_clicks = sum(d["metrics"]["button_clicks"] for d in telemetry["dashboards"].values())
    total_errors = sum(len(d["metrics"]["errors"]) for d in telemetry["dashboards"].values())

    return {
        "total_dashboards": total_dashboards,
        "rendered_successfully": rendered_count,
        "render_success_rate": rendered_count / total_dashboards if total_dashboards > 0 else 0,
        "total_button_clicks": total_clicks,
        "total_errors": total_errors,
        "recent_events": telemetry["events"][-10:]
    }


@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "Dashboard Telemetry Server",
        "status": "running",
        "endpoints": {
            "POST /telemetry": "Receive telemetry events",
            "POST /feedback": "Receive user feedback",
            "GET /telemetry/summary": "Get telemetry summary",
            "GET /telemetry/dashboard/{id}": "Get specific dashboard data"
        }
    }


if __name__ == "__main__":
    print("="*70)
    print("TELEMETRY SERVER - Opus Learning System")
    print("="*70)
    print("\nStarting server on http://localhost:8000")
    print("This server collects:")
    print("  - Render success/failure")
    print("  - Button clicks")
    print("  - Errors")
    print("  - User feedback ratings")
    print("\nDashboards will automatically send telemetry when they run.")
    print("="*70)

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
