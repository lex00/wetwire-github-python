"""Tests to verify that LINT_RULES.md documentation is complete and accurate."""

import re
from pathlib import Path


class TestLintRulesDocumentation:
    """Verify the LINT_RULES.md documentation is complete."""

    def test_documentation_header_reflects_all_rules(self) -> None:
        """Documentation should state it has 20 rules (WAG001-WAG016, WAG050-WAG053)."""
        docs_path = Path(__file__).parent.parent / "docs" / "LINT_RULES.md"
        content = docs_path.read_text()

        # Check that the intro mentions 20 rules
        assert "20 rules (WAG001-WAG016, WAG050-WAG053)" in content, (
            "Documentation header should mention '20 rules (WAG001-WAG016, WAG050-WAG053)'"
        )

    def test_quick_reference_table_has_all_rules(self) -> None:
        """Quick reference table should list all 20 rules."""
        docs_path = Path(__file__).parent.parent / "docs" / "LINT_RULES.md"
        content = docs_path.read_text()

        # Extract table rows using regex
        table_pattern = r"\| \[WAG(\d+)\]"
        matches = re.findall(table_pattern, content)
        rule_numbers = sorted([int(m) for m in matches])

        expected = list(range(1, 17)) + [50, 51, 52, 53]  # WAG001-WAG016 + WAG050-WAG053
        assert rule_numbers == expected, (
            f"Quick reference table should have all rules WAG001-WAG016 + WAG050-WAG053. "
            f"Found: {rule_numbers}"
        )

    def test_wag013_documented(self) -> None:
        """WAG013 should have full documentation section."""
        docs_path = Path(__file__).parent.parent / "docs" / "LINT_RULES.md"
        content = docs_path.read_text()

        # Check for heading
        assert "### WAG013:" in content, "WAG013 should have a section heading"

        # Check for key phrases from the rule
        assert "inline env" in content.lower(), (
            "WAG013 section should discuss inline env variables"
        )

        # Check for examples
        wag013_section = self._extract_rule_section(content, "WAG013")
        assert "# Bad" in wag013_section or "```python" in wag013_section, (
            "WAG013 should have code examples"
        )
        assert "# Good" in wag013_section, "WAG013 should have good examples"

        # Check for auto-fix mention
        assert "Auto-fix:" in wag013_section, (
            "WAG013 should mention auto-fix availability"
        )

    def test_wag014_documented(self) -> None:
        """WAG014 should have full documentation section."""
        docs_path = Path(__file__).parent.parent / "docs" / "LINT_RULES.md"
        content = docs_path.read_text()

        # Check for heading
        assert "### WAG014:" in content, "WAG014 should have a section heading"

        # Check for key phrases
        assert "matrix" in content.lower(), (
            "WAG014 section should discuss matrix configuration"
        )

        # Check for examples
        wag014_section = self._extract_rule_section(content, "WAG014")
        assert "# Bad" in wag014_section or "```python" in wag014_section, (
            "WAG014 should have code examples"
        )
        assert "# Good" in wag014_section, "WAG014 should have good examples"

        # Check for auto-fix mention
        assert "Auto-fix:" in wag014_section, (
            "WAG014 should mention auto-fix availability"
        )

    def test_wag015_documented(self) -> None:
        """WAG015 should have full documentation section."""
        docs_path = Path(__file__).parent.parent / "docs" / "LINT_RULES.md"
        content = docs_path.read_text()

        # Check for heading
        assert "### WAG015:" in content, "WAG015 should have a section heading"

        # Check for key phrases
        assert "output" in content.lower(), (
            "WAG015 section should discuss outputs"
        )

        # Check for examples
        wag015_section = self._extract_rule_section(content, "WAG015")
        assert "# Bad" in wag015_section or "```python" in wag015_section, (
            "WAG015 should have code examples"
        )
        assert "# Good" in wag015_section, "WAG015 should have good examples"

        # Check for auto-fix mention
        assert "Auto-fix:" in wag015_section, (
            "WAG015 should mention auto-fix availability"
        )

    def test_wag016_documented(self) -> None:
        """WAG016 should have full documentation section."""
        docs_path = Path(__file__).parent.parent / "docs" / "LINT_RULES.md"
        content = docs_path.read_text()

        # Check for heading
        assert "### WAG016:" in content, "WAG016 should have a section heading"

        # Check for key phrases
        assert "reusable" in content.lower(), (
            "WAG016 section should discuss reusable workflows"
        )

        # Check for examples
        wag016_section = self._extract_rule_section(content, "WAG016")
        assert "# Bad" in wag016_section or "```python" in wag016_section, (
            "WAG016 should have code examples"
        )
        assert "# Good" in wag016_section, "WAG016 should have good examples"

        # Check for auto-fix mention
        assert "Auto-fix:" in wag016_section, (
            "WAG016 should mention auto-fix availability"
        )

    def test_all_rules_have_why_section(self) -> None:
        """All documented rules should have a 'Why' explanation."""
        docs_path = Path(__file__).parent.parent / "docs" / "LINT_RULES.md"
        content = docs_path.read_text()

        for rule_num in range(1, 17):
            rule_id = f"WAG{rule_num:03d}"
            section = self._extract_rule_section(content, rule_id)
            if section:  # If the rule has a section
                assert "**Why:**" in section, (
                    f"{rule_id} section should have a **Why:** explanation"
                )

    def _extract_rule_section(self, content: str, rule_id: str) -> str:
        """Extract the documentation section for a specific rule."""
        # Find the section starting with ### WAG{num}:
        pattern = rf"### {rule_id}:.*?(?=###|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(0)
        return ""

    def test_quick_reference_has_descriptions(self) -> None:
        """Quick reference table should have meaningful descriptions."""
        docs_path = Path(__file__).parent.parent / "docs" / "LINT_RULES.md"
        content = docs_path.read_text()

        # Extract quick reference table
        table_start = content.find("## Quick Reference")
        table_end = content.find("\n---", table_start)
        table = content[table_start:table_end]

        # Check that WAG013-WAG016 have entries in the table
        for rule_num in [13, 14, 15, 16]:
            rule_id = f"WAG{rule_num:03d}"
            assert rule_id in table, (
                f"{rule_id} should be in the quick reference table"
            )

        # Verify each has a description (not empty)
        table_rows = re.findall(r"\| \[WAG\d+\].*?\|.*?\|.*?\|", table)
        for row in table_rows:
            parts = row.split("|")
            if len(parts) >= 3:
                description = parts[2].strip()
                assert len(description) > 0, (
                    f"Table row should have a description: {row}"
                )
