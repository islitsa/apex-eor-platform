"""
Real-time Feedback and Learning System
Collects star ratings and learns from user feedback
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


class FeedbackSystem:
    """
    Collects and manages user feedback for generated dashboards
    """

    def __init__(self, feedback_db_path: str = "data/learning/feedback.json"):
        self.feedback_db_path = Path(feedback_db_path)
        self.feedback_db_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing feedback
        self.feedback_data = self._load_feedback()

        # Component categories for rating
        self.component_categories = {
            "layout": "Overall screen layout and organization",
            "colors": "Color scheme and visual design",
            "pipeline_flow": "Pipeline flow visualization",
            "sor_cards": "Source of Record status cards",
            "kpi_metrics": "Key performance indicators display",
            "buttons": "Button functionality and placement",
            "controls": "Pipeline controls (checkboxes, options)",
            "logs": "Logs display and formatting",
            "responsiveness": "How responsive the UI feels",
            "data_accuracy": "Accuracy of displayed data"
        }

    def _load_feedback(self) -> Dict:
        """Load feedback from disk"""
        if self.feedback_db_path.exists():
            with open(self.feedback_db_path, 'r') as f:
                return json.load(f)
        return {
            "dashboard_ratings": {},
            "component_ratings": defaultdict(lambda: {"ratings": [], "avg": 0}),
            "pattern_performance": defaultdict(lambda: {"uses": 0, "avg_rating": 0, "ratings": []}),
            "improvement_suggestions": []
        }

    def _save_feedback(self):
        """Save feedback to disk"""
        # Convert defaultdict to regular dict for JSON serialization
        data = {
            "dashboard_ratings": self.feedback_data["dashboard_ratings"],
            "component_ratings": dict(self.feedback_data["component_ratings"]),
            "pattern_performance": dict(self.feedback_data["pattern_performance"]),
            "improvement_suggestions": self.feedback_data["improvement_suggestions"]
        }

        with open(self.feedback_db_path, 'w') as f:
            json.dump(data, f, indent=2)

    def collect_dashboard_rating(
        self,
        dashboard_id: str,
        component_ratings: Dict[str, int],
        overall_rating: int,
        comments: str = "",
        patterns_used: List[str] = None
    ) -> Dict:
        """
        Collect comprehensive rating for a dashboard

        Args:
            dashboard_id: Unique dashboard identifier
            component_ratings: Dict of {component: rating (1-5)}
            overall_rating: Overall rating (1-5)
            comments: User feedback comments
            patterns_used: List of pattern IDs used in this dashboard

        Returns:
            Feedback summary
        """

        timestamp = datetime.now().isoformat()

        # Store dashboard rating
        self.feedback_data["dashboard_ratings"][dashboard_id] = {
            "overall_rating": overall_rating,
            "component_ratings": component_ratings,
            "comments": comments,
            "timestamp": timestamp,
            "patterns_used": patterns_used or []
        }

        # Update component averages
        for component, rating in component_ratings.items():
            if component not in self.feedback_data["component_ratings"]:
                self.feedback_data["component_ratings"][component] = {
                    "ratings": [],
                    "avg": 0
                }

            self.feedback_data["component_ratings"][component]["ratings"].append({
                "rating": rating,
                "dashboard_id": dashboard_id,
                "timestamp": timestamp
            })

            # Calculate new average
            all_ratings = [r["rating"] for r in self.feedback_data["component_ratings"][component]["ratings"]]
            self.feedback_data["component_ratings"][component]["avg"] = sum(all_ratings) / len(all_ratings)

        # Update pattern performance
        if patterns_used:
            for pattern_id in patterns_used:
                if pattern_id not in self.feedback_data["pattern_performance"]:
                    self.feedback_data["pattern_performance"][pattern_id] = {
                        "uses": 0,
                        "avg_rating": 0,
                        "ratings": []
                    }

                self.feedback_data["pattern_performance"][pattern_id]["uses"] += 1
                self.feedback_data["pattern_performance"][pattern_id]["ratings"].append({
                    "rating": overall_rating,
                    "dashboard_id": dashboard_id,
                    "timestamp": timestamp
                })

                # Calculate new average
                all_ratings = [r["rating"] for r in self.feedback_data["pattern_performance"][pattern_id]["ratings"]]
                self.feedback_data["pattern_performance"][pattern_id]["avg_rating"] = sum(all_ratings) / len(all_ratings)

        # Save to disk
        self._save_feedback()

        # Return summary
        return self.get_feedback_summary()

    def get_feedback_summary(self) -> Dict:
        """Get summary of all feedback"""

        total_dashboards = len(self.feedback_data["dashboard_ratings"])

        if total_dashboards == 0:
            return {
                "total_dashboards_rated": 0,
                "overall_avg": 0,
                "component_averages": {},
                "top_patterns": [],
                "needs_improvement": []
            }

        # Calculate overall average
        all_overall_ratings = [d["overall_rating"] for d in self.feedback_data["dashboard_ratings"].values()]
        overall_avg = sum(all_overall_ratings) / len(all_overall_ratings)

        # Get component averages
        component_avgs = {
            comp: data["avg"]
            for comp, data in self.feedback_data["component_ratings"].items()
        }

        # Get top performing patterns
        pattern_list = [
            {
                "pattern_id": pid,
                "avg_rating": data["avg_rating"],
                "uses": data["uses"]
            }
            for pid, data in self.feedback_data["pattern_performance"].items()
            if data["uses"] > 0
        ]

        top_patterns = sorted(pattern_list, key=lambda x: x["avg_rating"], reverse=True)[:5]

        # Identify components needing improvement (< 3 stars)
        needs_improvement = [
            {"component": comp, "avg_rating": avg}
            for comp, avg in component_avgs.items()
            if avg < 3.0
        ]

        return {
            "total_dashboards_rated": total_dashboards,
            "overall_avg": overall_avg,
            "component_averages": component_avgs,
            "top_patterns": top_patterns,
            "needs_improvement": sorted(needs_improvement, key=lambda x: x["avg_rating"])
        }

    def get_improvement_recommendations(self) -> List[Dict]:
        """
        Get recommendations for improving patterns based on feedback
        """

        recommendations = []

        # Check component ratings
        for component, data in self.feedback_data["component_ratings"].items():
            if data["avg"] < 3.0 and len(data["ratings"]) >= 3:
                recommendations.append({
                    "type": "component_improvement",
                    "component": component,
                    "current_rating": data["avg"],
                    "issue": self.component_categories.get(component, "Unknown component"),
                    "priority": "high" if data["avg"] < 2.0 else "medium",
                    "suggestion": f"Improve {component} - currently rated {data['avg']:.1f}/5"
                })

        # Check pattern performance
        for pattern_id, data in self.feedback_data["pattern_performance"].items():
            if data["avg_rating"] < 3.0 and data["uses"] >= 3:
                recommendations.append({
                    "type": "pattern_improvement",
                    "pattern_id": pattern_id,
                    "current_rating": data["avg_rating"],
                    "uses": data["uses"],
                    "priority": "high" if data["avg_rating"] < 2.0 else "medium",
                    "suggestion": f"Pattern {pattern_id} needs improvement - rated {data['avg_rating']:.1f}/5"
                })

        # Sort by priority and rating
        recommendations.sort(key=lambda x: (
            0 if x["priority"] == "high" else 1,
            x.get("current_rating", 0)
        ))

        return recommendations

    def generate_feedback_form(self) -> str:
        """
        Generate Gradio code for feedback collection form

        Returns:
            Gradio code for feedback form
        """

        form_code = '''
# Feedback Collection Form
with gr.Accordion("Rate This Dashboard", open=False):
    gr.Markdown("### Help us improve! Rate each component:")

    feedback_ratings = {}

    with gr.Row():
        with gr.Column():
            feedback_ratings["layout"] = gr.Slider(
                minimum=1, maximum=5, step=1, value=3,
                label="Layout & Organization"
            )
            feedback_ratings["colors"] = gr.Slider(
                minimum=1, maximum=5, step=1, value=3,
                label="Color Scheme"
            )
            feedback_ratings["pipeline_flow"] = gr.Slider(
                minimum=1, maximum=5, step=1, value=3,
                label="Pipeline Flow Viz"
            )
            feedback_ratings["sor_cards"] = gr.Slider(
                minimum=1, maximum=5, step=1, value=3,
                label="SOR Status Cards"
            )
            feedback_ratings["kpi_metrics"] = gr.Slider(
                minimum=1, maximum=5, step=1, value=3,
                label="KPI Metrics"
            )

        with gr.Column():
            feedback_ratings["buttons"] = gr.Slider(
                minimum=1, maximum=5, step=1, value=3,
                label="Button Functionality"
            )
            feedback_ratings["controls"] = gr.Slider(
                minimum=1, maximum=5, step=1, value=3,
                label="Pipeline Controls"
            )
            feedback_ratings["logs"] = gr.Slider(
                minimum=1, maximum=5, step=1, value=3,
                label="Logs Display"
            )
            feedback_ratings["responsiveness"] = gr.Slider(
                minimum=1, maximum=5, step=1, value=3,
                label="Responsiveness"
            )
            feedback_ratings["data_accuracy"] = gr.Slider(
                minimum=1, maximum=5, step=1, value=3,
                label="Data Accuracy"
            )

    feedback_overall = gr.Slider(
        minimum=1, maximum=5, step=1, value=3,
        label="Overall Rating"
    )

    feedback_comments = gr.Textbox(
        label="Additional Comments",
        placeholder="What would you like to see improved?",
        lines=3
    )

    submit_feedback_btn = gr.Button("Submit Feedback", variant="primary")
    feedback_status = gr.Markdown("")

    def submit_feedback(*ratings_and_comments):
        # Extract ratings
        component_ratings = {
            "layout": ratings_and_comments[0],
            "colors": ratings_and_comments[1],
            "pipeline_flow": ratings_and_comments[2],
            "sor_cards": ratings_and_comments[3],
            "kpi_metrics": ratings_and_comments[4],
            "buttons": ratings_and_comments[5],
            "controls": ratings_and_comments[6],
            "logs": ratings_and_comments[7],
            "responsiveness": ratings_and_comments[8],
            "data_accuracy": ratings_and_comments[9]
        }
        overall = ratings_and_comments[10]
        comments = ratings_and_comments[11]

        # Save feedback
        import requests
        try:
            response = requests.post("http://localhost:8000/feedback", json={
                "dashboard_id": "generated_dashboard_opus",
                "component_ratings": component_ratings,
                "overall_rating": overall,
                "comments": comments,
                "patterns_used": ["gradio-complete-pipeline-dashboard-v2"]
            })

            if response.status_code == 200:
                return "Thank you for your feedback! Your ratings help us improve."
            else:
                return "Feedback saved locally (server offline)"
        except:
            # Save locally if server not running
            import json
            from pathlib import Path
            feedback_file = Path("data/learning/local_feedback.json")
            feedback_file.parent.mkdir(parents=True, exist_ok=True)

            feedback = {
                "timestamp": str(datetime.now()),
                "component_ratings": component_ratings,
                "overall_rating": overall,
                "comments": comments
            }

            existing = []
            if feedback_file.exists():
                with open(feedback_file, 'r') as f:
                    existing = json.load(f)

            existing.append(feedback)

            with open(feedback_file, 'w') as f:
                json.dump(existing, f, indent=2)

            return "Feedback saved locally! Thank you."

    submit_feedback_btn.click(
        fn=submit_feedback,
        inputs=[
            feedback_ratings["layout"],
            feedback_ratings["colors"],
            feedback_ratings["pipeline_flow"],
            feedback_ratings["sor_cards"],
            feedback_ratings["kpi_metrics"],
            feedback_ratings["buttons"],
            feedback_ratings["controls"],
            feedback_ratings["logs"],
            feedback_ratings["responsiveness"],
            feedback_ratings["data_accuracy"],
            feedback_overall,
            feedback_comments
        ],
        outputs=[feedback_status]
    )
'''

        return form_code


if __name__ == "__main__":
    # Test feedback system
    feedback = FeedbackSystem()

    # Simulate collecting feedback
    feedback.collect_dashboard_rating(
        dashboard_id="test_dashboard_1",
        component_ratings={
            "layout": 3,
            "colors": 2,
            "pipeline_flow": 4,
            "sor_cards": 4,
            "kpi_metrics": 5,
            "buttons": 2,
            "controls": 3,
            "logs": 4,
            "responsiveness": 3,
            "data_accuracy": 5
        },
        overall_rating=3,
        comments="Layout needs work, buttons don't function well. Colors are weird.",
        patterns_used=["gradio-complete-pipeline-dashboard-v2"]
    )

    # Get summary
    summary = feedback.get_feedback_summary()
    print("\nFeedback Summary:")
    print(f"  Dashboards rated: {summary['total_dashboards_rated']}")
    print(f"  Overall average: {summary['overall_avg']:.1f}/5")

    print("\n  Component Averages:")
    for comp, avg in summary['component_averages'].items():
        print(f"    {comp}: {avg:.1f}/5")

    # Get recommendations
    recommendations = feedback.get_improvement_recommendations()
    print("\n  Improvement Recommendations:")
    for rec in recommendations:
        print(f"    [{rec['priority']}] {rec['suggestion']}")
