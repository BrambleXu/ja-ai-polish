from __future__ import annotations

import unittest

from scripts.run_evals import validate_line_integrity


CONTRACT = {
    "enabled": True,
    "scene": "public-writing",
    "allow_intentional_line_breaks": False,
    "semantic_review": True,
}


class LineIntegrityTests(unittest.TestCase):
    def assertErrors(self, text: str, *expected: str) -> None:
        self.assertEqual(validate_line_integrity(text, CONTRACT), list(expected))

    def test_wrapped_prose_and_dangling_comma(self) -> None:
        self.assertErrors("一方で、\n文章の違和感が残ります。", "dangling-comma-break", "wrapped-prose")

    def test_inline_emphasis_does_not_hide_a_split_sentence(self) -> None:
        self.assertErrors(
            "LLMに長い文章を全部書いてもらうというより、\n\n"
            "**自分で書く → AIに少し整えてもらう → 最後は自分で判断する**\n\n"
            "くらいの使い方が、自分には一番合っています。",
            "dangling-comma-break",
            "wrapped-prose",
        )

    def test_complete_emphasized_paragraph_is_allowed(self) -> None:
        self.assertErrors("**これは独立した文です。**\n\n次の段落です。")

    def test_inline_emphasis_inside_one_prose_line_is_allowed(self) -> None:
        self.assertErrors(
            "LLMに長い文章を全部書いてもらうというより、"
            "**自分で書く → AIに少し整えてもらう → 最後は自分で判断する**"
            "くらいの使い方が、自分には一番合っています。"
        )

    def test_intentional_social_break_is_allowed(self) -> None:
        contract = dict(CONTRACT)
        contract["scene"] = "social-post"
        contract["allow_intentional_line_breaks"] = True
        self.assertEqual(validate_line_integrity("第一印象：\n\n速い。とにかく速い。", contract), [])

    def test_requested_social_break_after_comma_is_allowed(self) -> None:
        contract = dict(CONTRACT)
        contract["scene"] = "social-post"
        contract["allow_intentional_line_breaks"] = True
        self.assertEqual(validate_line_integrity("この結果は、\n\n予想以上でした。", contract), [])

    def test_adjacent_chat_wrap_is_rejected(self) -> None:
        contract = dict(CONTRACT)
        contract["scene"] = "chat-message"
        contract["allow_intentional_line_breaks"] = True
        self.assertEqual(
            validate_line_integrity("確認したところ、\n原因はタイムアウトでした。", contract),
            ["dangling-comma-break", "wrapped-prose"],
        )

    def test_real_paragraphs_are_allowed(self) -> None:
        self.assertErrors("一つ目の段落です。\n\n二つ目の段落です。")

    def test_excess_blank_lines(self) -> None:
        self.assertErrors("段落です。\n\n\n次の段落です。", "excess-blank-lines")

    def test_incomplete_list_intro_and_suffix(self) -> None:
        self.assertErrors(
            "たとえば、\n\n- 丁寧すぎる\n- 抽象的です\n\nといった文章です。",
            "incomplete-block-introduction",
            "block-suffix-continuation",
        )

    def test_complete_list_intro_is_allowed(self) -> None:
        self.assertErrors("特徴は次のとおりです。\n\n- 丁寧すぎる\n- 抽象的です")

    def test_complete_quote_is_allowed(self) -> None:
        self.assertErrors("次の引用を確認してください。\n\n> 文法は正しい。意味も通じる。")

    def test_code_and_repository_blocks_are_opaque(self) -> None:
        self.assertErrors(
            "たとえば、\n\n```python\nvalue = (\n    1\n)\n```\n\n- `npm test`",
        )

    def test_code_block_breaks_sentence_context(self) -> None:
        self.assertErrors("前置きです。\n\n```python\nprint(1)\n```\n\n- 実行結果")

    def test_real_scene_boundaries_are_allowed(self) -> None:
        self.assertErrors("件名：日程変更\n\nお世話になっております。\n\n8月4日を変更します。")

    def test_disabled_contract_does_not_check_text(self) -> None:
        contract = dict(CONTRACT)
        contract["enabled"] = False
        self.assertEqual(validate_line_integrity("一行目、\n二行目です。", contract), [])


if __name__ == "__main__":
    unittest.main()
