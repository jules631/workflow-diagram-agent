import unittest

from workflow_diagram_agent.generator import build_executive_workflow_diagram, extract_executive_steps


class GeneratorTests(unittest.TestCase):
    def test_extract_steps_dedupes_and_limits(self) -> None:
        text = """
        1. Gather requirements from stakeholders.
        2. Draft implementation approach.
        3. Draft implementation approach.
        4. Review with leadership for approval.
        5. Execute and monitor rollout.
        6. Capture outcomes and next steps.
        """
        steps = extract_executive_steps(text, max_steps=5)
        self.assertLessEqual(len(steps), 5)
        self.assertEqual(len(steps), len(set(step.lower() for step in steps)))

    def test_build_diagram_contains_start_and_end(self) -> None:
        diagram = build_executive_workflow_diagram("Identify issue. Define fix. Review fix.")
        self.assertIn("flowchart TD", diagram)
        self.assertIn('N0(["Start"])', diagram)
        self.assertIn('(["End"])', diagram)


if __name__ == "__main__":
    unittest.main()
