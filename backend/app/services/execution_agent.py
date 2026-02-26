import pandas as pd
from app.services.code_generator import generate_code
from app.services.sandbox import execute_code


class ExecutionAgent:

    def run(self, plan, file_path: str, question: str):
        """
        Handles:
        - Load dataset
        - Code generation
        - Safe execution
        """

        # 1️⃣ Load dataframe
        df = pd.read_csv(file_path)

        # 2️⃣ Generate python code string
        code = generate_code(df, question, plan)

        # 3️⃣ Execute using correct signature: (df, code)
        result = execute_code(df, code)

        return result