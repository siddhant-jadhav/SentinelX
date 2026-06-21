"""
SentinelX — Frontend Validation Test Suite
Validates frontend file structure, syntax, components, and configuration.
"""
import os
import ast
import sys
import pytest

# Project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")


# ═══════════════════════════════════════════════════════════════
# File Structure Validation
# ═══════════════════════════════════════════════════════════════

class TestFrontendStructure:
    """Validate frontend directory structure."""

    def test_app_entry_exists(self):
        """Main app.py entry point exists."""
        assert os.path.isfile(os.path.join(FRONTEND_DIR, "app.py"))

    def test_assets_directory_exists(self):
        """Assets directory exists."""
        assert os.path.isdir(os.path.join(FRONTEND_DIR, "assets"))

    def test_css_file_exists(self):
        """Custom CSS file exists."""
        css_path = os.path.join(FRONTEND_DIR, "assets", "styles.css")
        assert os.path.isfile(css_path)
        # CSS should not be empty
        with open(css_path) as f:
            content = f.read()
        assert len(content) > 100, "CSS file appears too small"

    def test_components_directory(self):
        """Components directory exists with required files."""
        components_dir = os.path.join(FRONTEND_DIR, "components")
        assert os.path.isdir(components_dir)

        required_components = [
            "sidebar.py",
            "threat_card.py",
            "metric_card.py",
            "auth_ui.py",
            "charts.py",
        ]
        for comp in required_components:
            path = os.path.join(components_dir, comp)
            assert os.path.isfile(path), f"Missing component: {comp}"

    def test_pages_directory(self):
        """Pages directory exists with expected page files."""
        pages_dir = os.path.join(FRONTEND_DIR, "pages")
        assert os.path.isdir(pages_dir)

        expected_pages = [
            "1_Dashboard.py",
            "2_Threat_Feed.py",
            "3_Search.py",
            "4_Submit_Threat.py",
            "5_Community_Threats.py",
            "6_Analytics.py",
            "7_Admin_Panel.py",
        ]
        for page in expected_pages:
            path = os.path.join(pages_dir, page)
            assert os.path.isfile(path), f"Missing page: {page}"

    def test_utils_directory(self):
        """Utils directory exists with required files."""
        utils_dir = os.path.join(FRONTEND_DIR, "utils")
        assert os.path.isdir(utils_dir)

        required_utils = ["api_client.py", "helpers.py"]
        for util in required_utils:
            path = os.path.join(utils_dir, util)
            assert os.path.isfile(path), f"Missing util: {util}"

    def test_streamlit_config_exists(self):
        """Streamlit config.toml exists."""
        config_path = os.path.join(PROJECT_ROOT, ".streamlit", "config.toml")
        assert os.path.isfile(config_path)


# ═══════════════════════════════════════════════════════════════
# Python Syntax Validation
# ═══════════════════════════════════════════════════════════════

class TestFrontendSyntax:
    """Validate all frontend Python files have valid syntax."""

    @staticmethod
    def _get_python_files():
        """Collect all .py files in the frontend directory."""
        py_files = []
        for root, dirs, files in os.walk(FRONTEND_DIR):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for f in files:
                if f.endswith(".py"):
                    py_files.append(os.path.join(root, f))
        return py_files

    def test_all_files_parse(self):
        """All frontend Python files should parse without SyntaxError."""
        errors = []
        for filepath in self._get_python_files():
            try:
                with open(filepath) as f:
                    ast.parse(f.read())
            except SyntaxError as e:
                rel = os.path.relpath(filepath, PROJECT_ROOT)
                errors.append(f"{rel}: {e}")

        assert not errors, "Syntax errors found:\n" + "\n".join(errors)

    def test_no_empty_files(self):
        """No frontend Python files should be empty."""
        for filepath in self._get_python_files():
            with open(filepath) as f:
                content = f.read().strip()
            rel = os.path.relpath(filepath, PROJECT_ROOT)
            assert len(content) > 0, f"Empty file: {rel}"


# ═══════════════════════════════════════════════════════════════
# Import Validation
# ═══════════════════════════════════════════════════════════════

class TestFrontendImports:
    """Validate key frontend modules can be imported."""

    def test_import_helpers(self):
        """frontend.utils.helpers module imports cleanly."""
        from frontend.utils.helpers import (
            page_header,
            severity_badge,
            source_badge,
            status_badge,
            indicator_display,
            format_date,
            format_relative_time,
            risk_score_bar,
        )
        assert callable(page_header)
        assert callable(severity_badge)

    def test_import_api_client(self):
        """frontend.utils.api_client module imports cleanly."""
        from frontend.utils import api_client
        assert hasattr(api_client, "get_threats")
        assert hasattr(api_client, "login")
        assert hasattr(api_client, "search_indicators")
        assert hasattr(api_client, "get_analytics_overview")

    def test_backend_url_configurable(self):
        """BACKEND_URL should be configurable via environment."""
        from frontend.utils import api_client
        assert api_client.BACKEND_URL is not None
        assert "localhost" in api_client.BACKEND_URL or "backend" in api_client.BACKEND_URL


# ═══════════════════════════════════════════════════════════════
# Helper Function Validation
# ═══════════════════════════════════════════════════════════════

class TestHelperFunctions:
    """Validate frontend helper functions produce correct output."""

    def test_severity_badge_html(self):
        """severity_badge returns valid HTML."""
        from frontend.utils.helpers import severity_badge
        for sev in ["Critical", "High", "Medium", "Low", "Info"]:
            html = severity_badge(sev)
            assert sev in html
            assert "<span" in html
            assert "style=" in html

    def test_source_badge_html(self):
        """source_badge returns valid HTML."""
        from frontend.utils.helpers import source_badge
        for src in ["OTX", "Community"]:
            html = source_badge(src)
            assert src in html
            assert "<span" in html

    def test_status_badge_html(self):
        """status_badge returns valid HTML."""
        from frontend.utils.helpers import status_badge
        for status in ["Pending", "Approved", "Rejected"]:
            html = status_badge(status)
            assert status in html

    def test_page_header_html(self):
        """page_header returns valid HTML structure."""
        from frontend.utils.helpers import page_header
        html = page_header("Test Page", "Description", "🔍")
        assert "Test Page" in html
        assert "Description" in html
        assert "🔍" in html
        assert "<div" in html

    def test_format_date(self):
        """format_date handles various inputs."""
        from frontend.utils.helpers import format_date
        assert format_date(None) == "N/A"
        assert format_date("") == "N/A"
        result = format_date("2024-01-15T10:30:00Z")
        assert "2024" in result

    def test_risk_score_bar(self):
        """risk_score_bar returns progress bar HTML."""
        from frontend.utils.helpers import risk_score_bar
        html = risk_score_bar(7.5)
        assert "7.5" in html
        assert "width:" in html

    def test_indicator_display(self):
        """indicator_display returns monospace formatted HTML."""
        from frontend.utils.helpers import indicator_display
        html = indicator_display("192.168.1.1", "IPv4")
        assert "192.168.1.1" in html
        assert "monospace" in html.lower() or "JetBrains" in html


# ═══════════════════════════════════════════════════════════════
# CSS Validation
# ═══════════════════════════════════════════════════════════════

class TestCSSValidation:
    """Basic CSS validation checks."""

    def test_css_has_root_variables(self):
        """CSS defines custom properties in :root."""
        css_path = os.path.join(FRONTEND_DIR, "assets", "styles.css")
        with open(css_path) as f:
            content = f.read()
        assert ":root" in content
        assert "--primary" in content

    def test_css_has_font_import(self):
        """CSS imports Google Fonts."""
        css_path = os.path.join(FRONTEND_DIR, "assets", "styles.css")
        with open(css_path) as f:
            content = f.read()
        assert "@import" in content or "fonts.googleapis" in content

    def test_css_balanced_braces(self):
        """CSS has balanced curly braces."""
        css_path = os.path.join(FRONTEND_DIR, "assets", "styles.css")
        with open(css_path) as f:
            content = f.read()
        open_count = content.count("{")
        close_count = content.count("}")
        assert open_count == close_count, (
            f"Unbalanced braces: {open_count} open vs {close_count} close"
        )


# ═══════════════════════════════════════════════════════════════
# Streamlit Config Validation
# ═══════════════════════════════════════════════════════════════

class TestStreamlitConfig:
    """Validate Streamlit configuration."""

    def test_config_has_theme(self):
        """config.toml defines a theme."""
        config_path = os.path.join(PROJECT_ROOT, ".streamlit", "config.toml")
        with open(config_path) as f:
            content = f.read()
        assert "[theme]" in content
        assert "primaryColor" in content

    def test_config_port(self):
        """config.toml sets port to 8503."""
        config_path = os.path.join(PROJECT_ROOT, ".streamlit", "config.toml")
        with open(config_path) as f:
            content = f.read()
        assert "8503" in content

    def test_config_headless(self):
        """config.toml enables headless mode."""
        config_path = os.path.join(PROJECT_ROOT, ".streamlit", "config.toml")
        with open(config_path) as f:
            content = f.read()
        assert "headless = true" in content


# ═══════════════════════════════════════════════════════════════
# Dockerfile Validation
# ═══════════════════════════════════════════════════════════════

class TestDockerfiles:
    """Validate Docker configuration files exist and are well-formed."""

    def test_backend_dockerfile_exists(self):
        """backend/Dockerfile exists."""
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "backend", "Dockerfile"))

    def test_frontend_dockerfile_exists(self):
        """frontend/Dockerfile exists."""
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "frontend", "Dockerfile"))

    def test_docker_compose_exists(self):
        """docker-compose.yml exists."""
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "docker-compose.yml"))

    def test_dockerignore_exists(self):
        """.dockerignore exists."""
        assert os.path.isfile(os.path.join(PROJECT_ROOT, ".dockerignore"))

    def test_docker_compose_has_services(self):
        """docker-compose.yml defines backend and frontend services."""
        compose_path = os.path.join(PROJECT_ROOT, "docker-compose.yml")
        with open(compose_path) as f:
            content = f.read()
        assert "backend:" in content
        assert "frontend:" in content
        assert "8003" in content
        assert "8503" in content
