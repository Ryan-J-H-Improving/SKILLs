from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from importlib.util import find_spec
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from extract_pdf_figures import output_name, parse_pages, parse_rect  # noqa: E402


class ExtractPdfFiguresTests(unittest.TestCase):
    def test_parse_pages_deduplicates_and_expands_ranges(self) -> None:
        self.assertEqual(parse_pages("1,3-5,3"), [1, 3, 4, 5])

    def test_parse_pages_rejects_invalid_ranges(self) -> None:
        with self.assertRaises(ValueError):
            parse_pages("5-3")
        with self.assertRaises(ValueError):
            parse_pages("0")

    def test_parse_rect_rejects_inverted_coordinates(self) -> None:
        with self.assertRaises(ValueError):
            parse_rect("100,200,50,300")

    def test_crop_names_include_coordinates(self) -> None:
        name = output_name(Path("week02.pdf"), 10, [72.0, 120.5, 540.0, 620.0], "")
        self.assertEqual(name, "week02-p010-crop-72-120p5-540-620.png")


class WorkspaceAndMemoryTests(unittest.TestCase):
    def run_script(self, script: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *args],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_init_creates_registered_source_layout_and_index(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / ".ai-course-tutor"
            self.run_script(
                "init_course_workspace.py",
                "--workspace",
                str(workspace),
                "--course-id",
                "stat5002-2026-s1",
            )
            course_dir = workspace / "courses" / "stat5002-2026-s1"
            for relative in [
                "sources/slides",
                "sources/transcripts",
                "sources/exams",
                "sources/tutorials",
                "sources/assignments",
                "sources/readings",
                "sources/data",
            ]:
                self.assertTrue((course_dir / relative).is_dir())
            self.assertTrue((course_dir / "indexes" / "source-register.md").is_file())
            self.assertIn("stat5002-2026-s1", (workspace / "index.md").read_text("utf-8"))

    @unittest.skipUnless(find_spec("pymupdf"), "PyMuPDF is not installed")
    def test_pdf_crops_are_unique_and_protected_from_overwrite(self) -> None:
        import pymupdf

        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            pdf = temp / "sample.pdf"
            output = temp / "figures"
            document = pymupdf.open()
            page = document.new_page(width=300, height=300)
            page.insert_text((20, 40), "left content")
            page.insert_text((170, 40), "right content")
            document.save(pdf)
            document.close()

            for rect in ["0,0,150,150", "150,0,300,150"]:
                self.run_script(
                    "extract_pdf_figures.py",
                    "--pdf",
                    str(pdf),
                    "--out",
                    str(output),
                    "--pages",
                    "1",
                    "--rect",
                    rect,
                )
            self.assertEqual(len(list(output.glob("*.png"))), 2)

            duplicate = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "extract_pdf_figures.py"),
                    "--pdf",
                    str(pdf),
                    "--out",
                    str(output),
                    "--pages",
                    "1",
                    "--rect",
                    "0,0,150,150",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertNotEqual(duplicate.returncode, 0)
            self.assertIn("output already exists", duplicate.stderr)

    def test_memory_update_replaces_snapshot_and_does_not_create_false_weakness(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            course_dir = Path(temp_dir) / "courses" / "comp5339-2026-s2"
            self.run_script(
                "update_learning_state.py",
                "--course-dir",
                str(course_dir),
                "--mode",
                "learning",
                "--topic",
                "Acquisition undercurrents",
                "--current-lesson",
                "Week 2",
                "--lesson-progress",
                "2/8",
                "--learning-cluster",
                "Secure acquisition design",
                "--narrative-bridge",
                "Acquisition choices create downstream security constraints",
                "--instruction-stage",
                "introduced",
                "--practice-gate",
                "blocked",
                "--practice-checkpoint",
                "1/3 answer actions evidenced",
                "--required-concepts",
                "Security; Privacy",
                "--source-layers",
                "course core",
                "--answer-actions",
                "1",
                "--issue-class",
                "tutor coverage gap",
                "--question-label",
                "independent",
                "--user-performance",
                "Could not answer",
                "--weak-point",
                "Security and privacy",
                "--tutor-coverage-gap",
            )
            memory = course_dir / "memory"
            learning_state = (memory / "learning-state.md").read_text("utf-8")
            self.assertEqual(learning_state.count("course-grounded-tutor:current-state:start"), 1)
            self.assertIn("Independent practice allowed: no", learning_state)
            self.assertIn("Current learning cluster: Secure acquisition design", learning_state)
            self.assertIn("Practice checkpoint: 1/3 answer actions evidenced", learning_state)
            self.assertFalse((memory / "weak-points.md").exists())
            self.assertIn(
                "Tutor coverage gap: yes",
                (memory / "practice-history.md").read_text("utf-8"),
            )
            self.assertIn(
                "Issue class: tutor coverage gap",
                (memory / "practice-history.md").read_text("utf-8"),
            )

    def test_weak_point_is_upserted_instead_of_duplicated(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            course_dir = Path(temp_dir) / "courses" / "stat5002-2026-s1"
            common = [
                "--course-dir",
                str(course_dir),
                "--topic",
                "Standard error",
                "--weak-point",
                "SD vs SE",
            ]
            self.run_script(
                "update_learning_state.py",
                *common,
                "--user-performance",
                "First error",
            )
            self.run_script(
                "update_learning_state.py",
                *common,
                "--user-performance",
                "Later evidence",
            )
            weak_points = (course_dir / "memory" / "weak-points.md").read_text("utf-8")
            self.assertEqual(weak_points.count("### SD vs SE"), 1)
            self.assertIn("Later evidence", weak_points)
            self.assertNotIn("First error", weak_points)


if __name__ == "__main__":
    unittest.main()
