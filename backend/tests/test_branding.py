import unittest

from app.core.config import Settings


class BrandingTests(unittest.TestCase):
    def test_default_application_name_is_learnloop(self) -> None:
        self.assertEqual(Settings().app_name, "LearnLoop API")
