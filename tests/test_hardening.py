import importlib
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class HardeningTests(unittest.TestCase):
    def test_database_module_imports_without_database_config(self):
        old_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            for key in [
                "DATABASE_URL",
                "DB_NAME",
                "DB_USER",
                "DB_PASSWORD",
                "DB_HOST",
                "DB_PORT",
                "POSTGRES_DB",
                "POSTGRES_USER",
                "POSTGRES_PASSWORD",
            ]:
                os.environ.pop(key, None)
            os.environ["SKIP_DOTENV"] = "1"

            sys.modules.pop("config.database", None)
            module = importlib.import_module("config.database")

            self.assertIsNotNone(module.Base)
            self.assertIsNone(module.engine)
            self.assertIsNone(module.SessionLocal)

            os.chdir(old_cwd)

    def test_slug_generation_removes_accents_and_symbols(self):
        from services.gemini_service import _gerar_slug

        slug = _gerar_slug("Olá, mundo! 2026 — Segurança")
        self.assertEqual(slug, "ola-mundo-2026-seguranca")


if __name__ == "__main__":
    unittest.main()
