# app/services/orchestrator.py

import time

from app.services.planning_agent import PlanningAgent
from app.services.execution_agent import ExecutionAgent
from app.services.explanation_agent import ExplanationAgent
from app.services.memory_engine import update_memory
from app.services.validation_agent import ValidationAgent
import numpy as np
import pandas as pd


def make_json_safe(obj):
    """
    Recursively convert numpy/pandas objects
    into JSON-serializable Python types.
    """

    # Pandas DataFrame → list of dicts
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")

    # Pandas Series → dict
    if isinstance(obj, pd.Series):
        return obj.to_dict()

    # numpy integer
    if isinstance(obj, (np.integer,)):
        return int(obj)

    # numpy float
    if isinstance(obj, (np.floating,)):
        return float(obj)

    # dict
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}

    # list
    if isinstance(obj, list):
        return [make_json_safe(v) for v in obj]

    return obj


class Orchestrator:

    def __init__(self, db):
        self.db = db
        self.planner = PlanningAgent(db)
        self.executor = ExecutionAgent()
        self.explainer = ExplanationAgent()
        self.validator = ValidationAgent()

    def run(self, file_path: str, question: str, file_id: int):

        start_time = time.time()

        max_retries = 2
        attempt = 0
        feedback = ""

        while attempt <= max_retries:
        
            # Planning with feedback
            plan = self.planner.run(question, file_id, file_path, feedback)

            # Execution
            result = self.executor.run(plan, file_path, question)

            # Validation
            is_valid, reason, error_context = self.validator.run(result)

            if is_valid:
                break
            
            attempt += 1
            feedback = str(error_context)[:300]

        # 4️⃣ Explanation
        summary, confidence = self.explainer.run(question, result, file_path)

        update_memory(self.db, file_id, question, result)

        latency = round(time.time() - start_time, 3)

        safe_result = make_json_safe(result)

        return {
            "plan": plan,
            "answer": safe_result,
            "summary": summary,
            "confidence": confidence,
            "latency": latency,
            "attempts": attempt
        }