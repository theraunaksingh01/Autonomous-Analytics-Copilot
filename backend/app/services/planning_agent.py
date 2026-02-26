import pandas as pd
from app.services.planner import plan_analysis
from app.services.memory_engine import build_memory_context


class PlanningAgent:

    def __init__(self, db):
        self.db = db

    def run(self, question: str, file_id: int, file_path: str, feedback: str = ""):

        import pandas as pd
        df = pd.read_csv(file_path)

        memory_context = build_memory_context(self.db, file_id)

        # Inject feedback into planning
        if feedback:
            question = f"""
            Previous attempt failed with due to reason:
            {feedback[:300]}


            Re-plan correctly for the original question.

            Original Question:
            {question}
            """

        plan = plan_analysis(df, question, memory_context)

        return plan