from __future__ import annotations

import unittest

from scripts.run_evals import validate_article_markdown


PUBLISH_CONTRACT = {
    "complete_article": True,
    "next_action": "publish",
    "artifact_only": True,
    "semantic_structure_review": True,
}


class ArticleMarkdownTests(unittest.TestCase):
    def assertErrors(self, text: str, *expected: str) -> None:
        self.assertEqual(validate_article_markdown(text, PUBLISH_CONTRACT), list(expected))

    def test_shallow_article_passes(self) -> None:
        self.assertErrors(
            "# タイトル\n\n導入です。\n\n## 方法\n\n方法を説明します。\n\n### 条件\n\n条件です。\n\n## 結果\n\n結果です。"
        )

    def test_h3_requires_h2(self) -> None:
        self.assertErrors("# タイトル\n\n### 条件\n\n条件です。", "orphan-h3")

    def test_deep_heading_is_rejected(self) -> None:
        self.assertErrors("# タイトル\n\n## 方法\n\n#### 詳細\n\n本文です。", "heading-too-deep", "empty-heading-chain")

    def test_missing_and_multiple_h1(self) -> None:
        self.assertErrors("## 方法\n\n本文です。", "missing-h1", "h1-not-first")
        self.assertErrors("# 一つ\n\n本文です。\n\n# 二つ\n\n本文です。", "multiple-h1")

    def test_h1_must_be_first(self) -> None:
        self.assertErrors("以下は成稿です。\n\n# タイトル\n\n本文です。", "h1-not-first", "artifact-wrapper-present")

    def test_empty_heading_chain_is_rejected(self) -> None:
        self.assertErrors("# タイトル\n\n## 方法\n\n### 条件\n\n本文です。", "empty-heading-chain")

    def test_code_block_is_ignored_for_heading_checks(self) -> None:
        self.assertErrors("# タイトル\n\n## 方法\n\n```markdown\n# example\n#### code\n```\n\n本文です。")

    def test_excerpt_does_not_require_h1(self) -> None:
        contract = dict(PUBLISH_CONTRACT)
        contract["complete_article"] = False
        self.assertEqual(validate_article_markdown("## 一つの章\n\n本文です。", contract), [])

    def test_other_scene_contract_is_not_article_contract(self) -> None:
        contract = dict(PUBLISH_CONTRACT)
        contract["complete_article"] = False
        self.assertEqual(validate_article_markdown("本文だけです。", contract), [])


if __name__ == "__main__":
    unittest.main()
