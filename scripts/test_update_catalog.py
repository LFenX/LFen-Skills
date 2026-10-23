#!/usr/bin/env python3
"""Catalog compatibility tests for legacy and standard skill metadata."""

from __future__ import annotations

import dataclasses
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import update_catalog as catalog


class FrontmatterCompatibilityTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.skill_file = self.root / "skills" / "tools" / "example" / "SKILL.md"
        self.skill_file.parent.mkdir(parents=True)
        self.root_patch = mock.patch.object(catalog, "ROOT", self.root)
        self.root_patch.start()

    def tearDown(self) -> None:
        self.root_patch.stop()
        self.temporary.cleanup()

    def parse(self, english_fields: str, *, encoding: str = "utf-8", newline: str = "\n") -> tuple[str, str, str]:
        content = "---\nname: example\ndescription: 中文说明。\n" + english_fields + "\n---\n# Instructions\n"
        self.skill_file.write_bytes(content.replace("\n", newline).encode(encoding))
        return catalog.parse_frontmatter(self.skill_file)

    def test_legacy_top_level_remains_supported(self) -> None:
        self.assertEqual(self.parse("description_en: English description."), ("example", "中文说明。", "English description."))

    def test_standard_metadata_is_equivalent_to_legacy(self) -> None:
        legacy = self.parse('description_en: "English description."\nmetadata:\n  version: 1.0')
        migrated = self.parse('metadata:\n  description_en: "English description."\n  version: 1.0')
        self.assertEqual(migrated, legacy)

    def test_existing_description_and_name_blocks_remain_supported(self) -> None:
        self.skill_file.write_text(
            "---\nname: example\ndescription: >-\n  中文第一行\n  中文第二行\n"
            "metadata:\n  description_en: English description.\n---\n",
            encoding="utf-8",
        )
        self.assertEqual(catalog.parse_frontmatter(self.skill_file), ("example", "中文第一行 中文第二行", "English description."))

    def test_matching_dual_values_are_accepted(self) -> None:
        self.assertEqual(self.parse('description_en: " English. "\nmetadata:\n  description_en: English.')[2], "English.")

    def test_conflicting_dual_values_are_rejected(self) -> None:
        with self.assertRaisesRegex(catalog.CatalogError, r"description_en.*metadata.description_en.*冲突"):
            self.parse("description_en: Legacy.\nmetadata:\n  description_en: Different.")

    def test_empty_dual_value_is_not_silently_ignored(self) -> None:
        for fields in ('description_en: Legacy.\nmetadata:\n  description_en: ""', 'description_en: ""\nmetadata:\n  description_en: English.'):
            with self.subTest(fields=fields), self.assertRaisesRegex(catalog.CatalogError, "冲突"):
                self.parse(fields)

    def test_metadata_literal_block(self) -> None:
        self.assertEqual(self.parse("metadata:\n  description_en: |-\n    First line.\n    Second line.\n  version: 1")[2], "First line.\nSecond line.")

    def test_metadata_folded_block(self) -> None:
        self.assertEqual(self.parse("metadata:\n  description_en: >-\n    First line.\n    Second line.\n  version: 1")[2], "First line. Second line.")

    def test_quoted_scalars_keep_legacy_escaping(self) -> None:
        self.assertEqual(self.parse("metadata:\n  description_en: 'It''s supported.'")[2], "It's supported.")
        self.assertEqual(self.parse('metadata:\n  description_en: "Quoted \\"value\\"."')[2], 'Quoted "value".')

    def test_metadata_mapping_indentation_is_not_fixed_to_two_spaces(self) -> None:
        for indentation in (1, 4):
            with self.subTest(indentation=indentation):
                self.assertEqual(self.parse("metadata:\n" + " " * indentation + "description_en: English.")[2], "English.")

    def test_comments_do_not_set_metadata_field_indentation(self) -> None:
        for indentation in (0, 1, 3):
            with self.subTest(comment_indentation=indentation):
                comment = " " * indentation + "# English catalog text"
                self.assertEqual(self.parse("metadata:\n" + comment + "\n  version: 1\n" + comment + "\n  description_en: English.")[2], "English.")

    def test_commented_description_is_not_a_metadata_value(self) -> None:
        with self.assertRaises(catalog.CatalogError):
            self.parse("metadata:\n # description_en: Wrong.\n  version: 1")

    def test_literal_comment_text_is_preserved_in_description(self) -> None:
        self.assertEqual(self.parse("metadata:\n  description_en: |-\n    First line.\n    # Literal text.\n  version: 1")[2], "First line.\n# Literal text.")

    def test_bom_and_crlf_remain_supported(self) -> None:
        self.assertEqual(self.parse("metadata:\n  description_en: English.", encoding="utf-8-sig", newline="\r\n")[2], "English.")

    def test_other_top_level_mapping_is_not_metadata(self) -> None:
        with self.assertRaises(catalog.CatalogError):
            self.parse("other:\n  description_en: Wrong.")

    def test_nested_metadata_value_is_not_a_direct_child(self) -> None:
        with self.assertRaises(catalog.CatalogError):
            self.parse("metadata:\n  nested:\n    description_en: Wrong.")

    def test_nested_metadata_value_does_not_conflict_with_legacy(self) -> None:
        self.assertEqual(self.parse("description_en: Legacy.\nmetadata:\n  nested:\n    description_en: Wrong.")[2], "Legacy.")

    def test_metadata_scope_ends_before_next_top_level_mapping(self) -> None:
        with self.assertRaises(catalog.CatalogError):
            self.parse("metadata:\n  version: 1\nother:\n  description_en: Wrong.")

    def test_metadata_sibling_block_cannot_inject_an_english_field(self) -> None:
        with self.assertRaises(catalog.CatalogError):
            self.parse("metadata:\n  notes: |\n    description_en: Wrong.")

    def test_empty_metadata_does_not_break_legacy(self) -> None:
        self.assertEqual(self.parse("description_en: Legacy.\nmetadata:\n")[2], "Legacy.")

    def test_missing_or_empty_english_description_is_rejected(self) -> None:
        for fields in ("metadata:\n  version: 1", 'metadata:\n  description_en: " "', "description_en:"):
            with self.subTest(fields=fields), self.assertRaises(catalog.CatalogError):
                self.parse(fields)


class RepositoryRenderingCompatibilityTest(unittest.TestCase):
    def test_metadata_migration_preserves_all_generated_content(self) -> None:
        taxonomy = catalog.load_taxonomy()
        skills = catalog.discover_skills()
        assignments = catalog.validate_taxonomy(taxonomy, skills)
        workflow = skills["run-governed-product-workflow"]
        skill_file = workflow.directory / "SKILL.md"
        original = skill_file.read_text(encoding="utf-8-sig")
        metadata_line = next(line for line in original.splitlines() if line.startswith("  description_en:"))
        legacy = original.replace(metadata_line + "\n", "", 1).replace("metadata:\n", metadata_line.lstrip() + "\nmetadata:\n", 1)
        with mock.patch.object(Path, "read_text", return_value=legacy):
            name, description, description_en = catalog.parse_frontmatter(skill_file)
        legacy_skills = dict(skills)
        legacy_skills[workflow.name] = dataclasses.replace(workflow, name=name, description=description, description_en=description_en)
        self.assertEqual(legacy_skills, skills)
        self.assertEqual(catalog.render_catalog(taxonomy, legacy_skills), catalog.render_catalog(taxonomy, skills))
        self.assertEqual(catalog.render_index(taxonomy, legacy_skills, assignments), catalog.render_index(taxonomy, skills, assignments))
        for lang in ("zh", "en"):
            with self.subTest(language=lang):
                self.assertEqual(catalog.render_skill_table(taxonomy, legacy_skills, lang), catalog.render_skill_table(taxonomy, skills, lang))


if __name__ == "__main__":
    unittest.main()
