import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "l2_session_csv.py"
HEADER = [
    "session_id",
    "date_utc",
    "lambda",
    "theta_prime",
    "ratio",
    "spectral_concentration",
    "STATE",
    "GAP",
    "STATUS",
    "NEXT",
    "notes",
]


def run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def read_rows(path: Path) -> list[list[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.reader(handle))


class L2SessionCsvTest(unittest.TestCase):
    def test_init_only_writes_exact_header(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "l2_sessions.csv"
            result = run_tool("--out", str(out), "--init-only")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(read_rows(out), [HEADER])

    def test_append_preserves_undefined_literal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "l2_sessions.csv"
            result = run_tool(
                "--out",
                str(out),
                "--session-id",
                "S002",
                "--date-utc",
                "2026-05-28T20:00:00Z",
                "--spectral-concentration",
                "0.12",
                "--state",
                "L2-2",
                "--gap",
                "GAP-2",
                "--status",
                "FAIL",
                "--next",
                "rerun",
                "--notes",
                "auto-filled UNDEFINED",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            rows = read_rows(out)
            self.assertEqual(rows[0], HEADER)
            self.assertEqual(
                rows[1],
                [
                    "S002",
                    "2026-05-28T20:00:00Z",
                    "UNDEFINED",
                    "UNDEFINED",
                    "UNDEFINED",
                    "0.12",
                    "L2-2",
                    "GAP-2",
                    "FAIL",
                    "rerun",
                    "auto-filled UNDEFINED",
                ],
            )

    def test_rejects_bad_numeric_value(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "l2_sessions.csv"
            result = run_tool("--out", str(out), "--lambda", "not-a-number")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("lambda must be numeric or UNDEFINED", result.stderr)


if __name__ == "__main__":
    unittest.main()
