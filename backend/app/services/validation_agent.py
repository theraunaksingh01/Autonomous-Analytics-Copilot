class ValidationAgent:

    def run(self, result):
        """
        Returns:
        (is_valid: bool, reason: str, error_context: str)
        """

        if result is None:
            return False, "None result", "Execution returned None"

        if isinstance(result, (list, dict)) and len(result) == 0:
            return False, "Empty result", "Query returned empty output"

        if hasattr(result, "empty") and result.empty:
            return False, "Empty dataframe", "DataFrame is empty"

        if isinstance(result, str) and "error" in result.lower():
            return False, "Execution error", result

        return True, "Valid", ""