"""Tests for CLI path validation security."""

import pytest

from wetwire_github.cli.path_validation import PathValidationError, validate_path


class TestPathTraversalPrevention:
    """Tests for path traversal attack prevention."""

    def test_rejects_parent_directory_traversal(self):
        """Reject paths with ../ traversal attempts."""
        with pytest.raises(PathValidationError, match="traversal"):
            validate_path("../../../etc/passwd")

    def test_rejects_hidden_traversal_in_middle(self):
        """Reject paths with ../ hidden in the middle."""
        with pytest.raises(PathValidationError, match="traversal"):
            validate_path("foo/../../bar")

    def test_rejects_backslash_traversal(self):
        """Reject paths with Windows-style backslash traversal."""
        with pytest.raises(PathValidationError, match="traversal"):
            validate_path("..\\..\\..\\etc\\passwd")

    def test_rejects_encoded_traversal(self):
        """Reject paths with URL-encoded traversal patterns."""
        # Raw .. in path after any decoding
        with pytest.raises(PathValidationError, match="traversal"):
            validate_path("..%2F..%2Fetc%2Fpasswd")


class TestAbsolutePathValidation:
    """Tests for absolute path validation."""

    def test_rejects_absolute_path_outside_project_when_not_allowed(self, tmp_path):
        """Reject absolute paths outside project when allow_absolute=False."""
        # Create a fake "project" directory
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Try to access something outside
        outside_path = tmp_path / "other" / "secret.txt"
        outside_path.parent.mkdir()
        outside_path.write_text("secret")

        with pytest.raises(PathValidationError, match="outside"):
            validate_path(str(outside_path), base_dir=str(project_root), allow_absolute=False)

    def test_allows_absolute_path_outside_project_when_allowed(self, tmp_path):
        """Allow absolute paths outside project when allow_absolute=True (default)."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Access something outside - should be allowed by default
        outside_path = tmp_path / "other" / "file.txt"
        outside_path.parent.mkdir()
        outside_path.write_text("content")

        result = validate_path(str(outside_path), base_dir=str(project_root))
        assert result == outside_path.resolve()

    def test_accepts_absolute_path_within_project(self, tmp_path):
        """Accept absolute paths within the project root."""
        project_root = tmp_path / "project"
        project_root.mkdir()
        valid_file = project_root / "src" / "file.py"
        valid_file.parent.mkdir()
        valid_file.write_text("content")

        result = validate_path(str(valid_file), base_dir=str(project_root))
        assert result == valid_file.resolve()

    def test_rejects_path_to_system_files_when_not_allowed(self, tmp_path):
        """Reject paths to sensitive system files when allow_absolute=False."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        with pytest.raises(PathValidationError, match="outside"):
            validate_path("/etc/passwd", base_dir=str(project_root), allow_absolute=False)


class TestSymlinkProtection:
    """Tests for symlink attack prevention."""

    def test_rejects_symlink_pointing_outside_project(self, tmp_path):
        """Reject symlinks that point outside the project."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Create a file outside
        outside_file = tmp_path / "secret.txt"
        outside_file.write_text("secret")

        # Create a symlink inside project pointing outside
        symlink = project_root / "sneaky_link"
        symlink.symlink_to(outside_file)

        with pytest.raises(PathValidationError, match="symlink|outside"):
            validate_path(str(symlink), base_dir=str(project_root))

    def test_accepts_symlink_within_project(self, tmp_path):
        """Accept symlinks that stay within the project."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Create a file inside
        real_file = project_root / "real.txt"
        real_file.write_text("content")

        # Create a symlink inside project pointing to another inside file
        symlink = project_root / "valid_link"
        symlink.symlink_to(real_file)

        result = validate_path(str(symlink), base_dir=str(project_root))
        assert result.exists()

    def test_rejects_directory_symlink_escape(self, tmp_path):
        """Reject directory symlinks that allow escaping the project."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Create directory outside
        outside_dir = tmp_path / "outside"
        outside_dir.mkdir()
        secret_file = outside_dir / "secret.txt"
        secret_file.write_text("secret")

        # Create a symlink to outside directory
        symlink_dir = project_root / "escape_dir"
        symlink_dir.symlink_to(outside_dir)

        # Try to access file through symlink - when allow_absolute=False,
        # this should be rejected because the resolved path is outside
        with pytest.raises(PathValidationError, match="symlink|outside"):
            validate_path(
                str(symlink_dir / "secret.txt"),
                base_dir=str(project_root),
                allow_absolute=False,
            )


class TestNonExistentPaths:
    """Tests for non-existent path handling."""

    def test_rejects_nonexistent_path_when_must_exist(self, tmp_path):
        """Reject non-existent paths when existence is required."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        with pytest.raises(PathValidationError, match="not exist"):
            validate_path(
                str(project_root / "nonexistent.txt"),
                base_dir=str(project_root),
                must_exist=True,
            )

    def test_accepts_nonexistent_path_when_not_required(self, tmp_path):
        """Accept non-existent paths when existence is not required."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        result = validate_path(
            str(project_root / "newfile.txt"),
            base_dir=str(project_root),
            must_exist=False,
        )
        assert result.parent == project_root.resolve()


class TestSpecialCharacters:
    """Tests for paths with special characters."""

    def test_rejects_null_bytes(self):
        """Reject paths containing null bytes."""
        with pytest.raises(PathValidationError, match="null|invalid"):
            validate_path("file\x00.txt")

    def test_accepts_spaces_in_filename(self, tmp_path):
        """Accept valid paths with spaces."""
        project_root = tmp_path / "project"
        project_root.mkdir()
        file_with_spaces = project_root / "my file.txt"
        file_with_spaces.write_text("content")

        result = validate_path(str(file_with_spaces), base_dir=str(project_root))
        assert result.exists()

    def test_accepts_unicode_filenames(self, tmp_path):
        """Accept valid paths with unicode characters."""
        project_root = tmp_path / "project"
        project_root.mkdir()
        unicode_file = project_root / "archivo_espanol.txt"
        unicode_file.write_text("content")

        result = validate_path(str(unicode_file), base_dir=str(project_root))
        assert result.exists()

    def test_rejects_control_characters(self):
        """Reject paths with control characters."""
        with pytest.raises(PathValidationError, match="invalid|control"):
            validate_path("file\x07.txt")


class TestRelativePathResolution:
    """Tests for relative path handling."""

    def test_resolves_relative_path_within_base(self, tmp_path):
        """Resolve relative paths correctly within base directory."""
        project_root = tmp_path / "project"
        project_root.mkdir()
        subdir = project_root / "src"
        subdir.mkdir()
        file_in_subdir = subdir / "module.py"
        file_in_subdir.write_text("content")

        # When in project root, src/module.py should be valid
        result = validate_path("src/module.py", base_dir=str(project_root))
        assert result == file_in_subdir.resolve()

    def test_normalizes_redundant_separators(self, tmp_path):
        """Normalize paths with redundant separators."""
        project_root = tmp_path / "project"
        project_root.mkdir()
        file_path = project_root / "file.txt"
        file_path.write_text("content")

        result = validate_path("./file.txt", base_dir=str(project_root))
        assert result == file_path.resolve()


class TestDefaultBaseDirectory:
    """Tests for default base directory behavior."""

    def test_uses_cwd_when_no_base_dir_specified(self, tmp_path, monkeypatch):
        """Use current working directory when no base_dir is specified."""
        project_root = tmp_path / "project"
        project_root.mkdir()
        file_path = project_root / "file.txt"
        file_path.write_text("content")

        monkeypatch.chdir(project_root)

        result = validate_path("file.txt")
        assert result == file_path.resolve()


class TestCLIIntegration:
    """Tests for CLI command integration."""

    def test_build_command_validates_package_path(self, tmp_path):
        """Build command should validate package path."""
        from wetwire_github.cli.build import build_workflows

        # Try path traversal in package path
        exit_code, messages = build_workflows(
            package_path="../../../etc",
            output_dir=str(tmp_path / "output"),
        )
        assert exit_code != 0
        assert any("traversal" in msg.lower() or "invalid" in msg.lower() for msg in messages)

    def test_build_command_validates_output_path(self, tmp_path):
        """Build command should validate output path."""
        from wetwire_github.cli.build import build_workflows

        project_root = tmp_path / "project"
        project_root.mkdir()

        exit_code, messages = build_workflows(
            package_path=str(project_root),
            output_dir="../../../tmp/evil",
        )
        assert exit_code != 0
        assert any("traversal" in msg.lower() or "invalid" in msg.lower() for msg in messages)

    def test_validate_command_validates_file_paths(self, tmp_path):
        """Validate command should validate file paths."""
        from wetwire_github.cli.validate import validate_files

        exit_code, output = validate_files(
            file_paths=["../../../etc/passwd"],
        )
        assert exit_code != 0
        assert "traversal" in output.lower() or "invalid" in output.lower()

    def test_import_command_validates_input_paths(self, tmp_path):
        """Import command should validate input file paths."""
        from wetwire_github.cli.import_cmd import import_workflows

        exit_code, messages = import_workflows(
            file_paths=["../../../etc/passwd"],
            output_dir=str(tmp_path / "output"),
        )
        assert exit_code != 0
        assert any("traversal" in msg.lower() or "invalid" in msg.lower() for msg in messages)

    def test_import_command_validates_output_path(self, tmp_path):
        """Import command should validate output directory."""
        from wetwire_github.cli.import_cmd import import_workflows

        workflow_file = tmp_path / "workflow.yml"
        workflow_file.write_text("name: Test\non: push\njobs: {}")

        exit_code, messages = import_workflows(
            file_paths=[str(workflow_file)],
            output_dir="../../../tmp/evil",
        )
        assert exit_code != 0
        assert any("traversal" in msg.lower() or "invalid" in msg.lower() for msg in messages)
