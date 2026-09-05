from pathlib import Path
import unittest

from dotenv import dotenv_values

from app.core.config import Settings


class BrandingTests(unittest.TestCase):
    def test_default_application_name_is_learnloop(self) -> None:
        self.assertEqual(Settings().app_name, "LearnLoop API")

    def test_env_template_uses_learnloop_database(self) -> None:
        project_root = Path(__file__).resolve().parents[2]
        values = dotenv_values(project_root / "backend" / ".env.example")

        self.assertEqual(values["DATABASE_URL"], "sqlite:///./learnloop.db")
