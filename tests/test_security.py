"""
Security verification tests for CampusPilot.
Ensures secrets are never bundled into frontend assets or exposed in client responses.
"""

import os
import glob
import pytest
from backend.config import settings

def test_no_secrets_in_frontend_dist():
    """Verify built frontend assets do not contain server secrets or service role keys."""
    dist_js_files = glob.glob("client/dist/assets/*.js")
    assert len(dist_js_files) > 0, "Frontend dist assets must exist. Run npm run build."

    forbidden_patterns = [
        "service_role",
        "SUPABASE_SERVICE_ROLE_KEY",
        "DATABASE_URL",
        "JWT_SECRET",
        "postgresql://"
    ]

    for fpath in dist_js_files:
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            for pattern in forbidden_patterns:
                assert pattern not in content, f"Security violation: Secret '{pattern}' found in {fpath}"

def test_gitignore_protects_env():
    """Verify that .gitignore excludes .env files from version control."""
    gitignore_path = ".gitignore"
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert ".env" in content, ".gitignore must explicitly ignore .env"
