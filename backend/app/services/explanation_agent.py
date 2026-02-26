# app/services/explanation_agent.py

import pandas as pd
from app.services.summary_engine import generate_summary
from app.services.confidence_engine import evaluate_confidence

class ExplanationAgent:

    def run(self, question: str, result, file_path: str):
        """
        Handles:
        - Load dataset (required by summary_engine)
        - Generate summary
        - Calculate confidence
        """

        # 1️⃣ Load dataset
        df = pd.read_csv(file_path)

        # 2️⃣ Generate summary (match exact signature)
        summary = generate_summary(df, result, question)

        # 3️⃣ Confidence
        confidence = evaluate_confidence(question, result)

        # Normalize to 0–1 safely
        if isinstance(confidence, (int, float)):
            if confidence > 1:
                confidence = confidence / 100.0
            confidence = max(0, min(confidence, 1))
        else:
            confidence = 0.5  # fallback safe default

        return summary, confidence