import json
import os
import tempfile
import unittest
from pathlib import Path

from report_catalog import list_reports, resolve_relative_pdf


class ReportCatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        os.environ["CLIMATE_REPORTING_DATA_ROOT"] = str(self.root)

        run = self.root / "runs" / "daily" / "2026-06-29"
        pdf = run / "07_pdf" / "fic1" / "daily.pdf"
        pdf.parent.mkdir(parents=True)
        pdf.write_bytes(b"%PDF-test")
        (run / "manifest.json").write_text(
            json.dumps(
                {
                    "kind": "daily",
                    "report_date": "2026-06-29",
                    "status": "complete",
                    "window": {
                        "start_utc": "2026-05-01T04:00:00+00:00",
                        "end_utc": "2026-06-30T03:59:59+00:00",
                    },
                    "stages": {
                        "pdf": {
                            "result": [
                                {"site": "fic1-rengo-agritorre", "generated": True, "path": str(pdf)}
                            ]
                        }
                    },
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        os.environ.pop("CLIMATE_REPORTING_DATA_ROOT", None)
        self.temp_dir.cleanup()

    def test_lists_only_authorized_generated_reports(self):
        reports = list_reports({"fic1-rengo-agritorre"})
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0]["kind"], "daily")
        self.assertEqual(reports[0]["relative_path"], "runs/daily/2026-06-29/07_pdf/fic1/daily.pdf")

        self.assertEqual(list_reports({"other-site"}), [])

    def test_rejects_path_traversal(self):
        self.assertIsNone(resolve_relative_pdf("../../etc/passwd"))


if __name__ == "__main__":
    unittest.main()
