"""Tests to verify that EXPRESSIONS.md documentation exists and is complete."""

from pathlib import Path


class TestExpressionsDocumentation:
    """Verify the EXPRESSIONS.md documentation exists and is referenced."""

    def test_expressions_md_exists(self) -> None:
        """EXPRESSIONS.md file should exist in docs/ directory."""
        docs_path = Path(__file__).parent.parent / "docs" / "EXPRESSIONS.md"
        assert docs_path.exists(), (
            "docs/EXPRESSIONS.md should exist (referenced in LINT_RULES.md)"
        )

    def test_expressions_md_has_content(self) -> None:
        """EXPRESSIONS.md should have meaningful content."""
        docs_path = Path(__file__).parent.parent / "docs" / "EXPRESSIONS.md"
        content = docs_path.read_text()

        # Should be substantial documentation (at least 5000 characters)
        assert len(content) > 5000, (
            "EXPRESSIONS.md should contain substantial documentation"
        )

    def test_lint_rules_references_expressions_md(self) -> None:
        """LINT_RULES.md should reference EXPRESSIONS.md."""
        lint_rules_path = Path(__file__).parent.parent / "docs" / "LINT_RULES.md"
        content = lint_rules_path.read_text()

        assert "EXPRESSIONS.md" in content, (
            "LINT_RULES.md should reference EXPRESSIONS.md"
        )
        assert "[Expression Contexts](EXPRESSIONS.md)" in content, (
            "LINT_RULES.md should have a proper markdown link to EXPRESSIONS.md"
        )

    def test_expressions_md_covers_contexts(self) -> None:
        """EXPRESSIONS.md should document all expression contexts."""
        docs_path = Path(__file__).parent.parent / "docs" / "EXPRESSIONS.md"
        content = docs_path.read_text()

        # Should cover all major contexts
        expected_contexts = [
            "GitHub Context",
            "Secrets Context",
            "Matrix Context",
            "Env Context",
            "Runner Context",
            "Inputs Context",
            "Needs Context",
            "Steps Context",
        ]

        for context in expected_contexts:
            assert context in content, (
                f"EXPRESSIONS.md should document {context}"
            )

    def test_expressions_md_covers_condition_builders(self) -> None:
        """EXPRESSIONS.md should document condition builder functions."""
        docs_path = Path(__file__).parent.parent / "docs" / "EXPRESSIONS.md"
        content = docs_path.read_text()

        # Should cover all condition builders
        expected_conditions = [
            "always()",
            "failure()",
            "success()",
            "cancelled()",
        ]

        for condition in expected_conditions:
            assert condition in content, (
                f"EXPRESSIONS.md should document {condition} condition builder"
            )

    def test_expressions_md_has_examples(self) -> None:
        """EXPRESSIONS.md should include practical examples."""
        docs_path = Path(__file__).parent.parent / "docs" / "EXPRESSIONS.md"
        content = docs_path.read_text()

        # Should have code examples
        assert "```python" in content, (
            "EXPRESSIONS.md should have Python code examples"
        )

        # Should have multiple examples
        python_blocks = content.count("```python")
        assert python_blocks >= 10, (
            f"EXPRESSIONS.md should have at least 10 code examples, found {python_blocks}"
        )

    def test_expressions_md_documents_operators(self) -> None:
        """EXPRESSIONS.md should document expression operators."""
        docs_path = Path(__file__).parent.parent / "docs" / "EXPRESSIONS.md"
        content = docs_path.read_text()

        # Should cover operators
        assert "Comparison Operators" in content or "comparison" in content.lower(), (
            "EXPRESSIONS.md should document comparison operators"
        )
        assert "Logical Operators" in content or "logical" in content.lower(), (
            "EXPRESSIONS.md should document logical operators"
        )

    def test_expressions_md_has_practical_examples(self) -> None:
        """EXPRESSIONS.md should have a practical examples section."""
        docs_path = Path(__file__).parent.parent / "docs" / "EXPRESSIONS.md"
        content = docs_path.read_text()

        # Should have practical examples section
        assert "Practical Examples" in content or "Example" in content, (
            "EXPRESSIONS.md should have a practical examples section"
        )

    def test_expressions_md_mentions_github_properties(self) -> None:
        """EXPRESSIONS.md should document GitHub context properties."""
        docs_path = Path(__file__).parent.parent / "docs" / "EXPRESSIONS.md"
        content = docs_path.read_text()

        # Should mention common GitHub properties
        expected_properties = [
            "GitHub.ref",
            "GitHub.sha",
            "GitHub.actor",
            "GitHub.event_name",
            "GitHub.repository",
        ]

        for prop in expected_properties:
            assert prop in content, (
                f"EXPRESSIONS.md should document {prop}"
            )

    def test_expressions_md_has_see_also_section(self) -> None:
        """EXPRESSIONS.md should have a See Also section with links."""
        docs_path = Path(__file__).parent.parent / "docs" / "EXPRESSIONS.md"
        content = docs_path.read_text()

        assert "## See Also" in content or "See Also" in content, (
            "EXPRESSIONS.md should have a See Also section"
        )
