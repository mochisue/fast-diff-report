import os
import random
import string
from typing import List, Tuple

import diff_match_patch
import dominate
from dominate.tags import *
from dominate.util import raw


class FastDiffReport(diff_match_patch.diff_match_patch):
    def __init__(self, wrapcolumn: int = None):
        super().__init__()
        self.wrapcolumn = wrapcolumn
        self.STYLE_RAW = """\
        table.diff {font-family:Courier; border:medium;}
        .diff_header {background-color:#e0e0e0}
        td.diff_header {text-align:right}
        .diff_next {background-color:#c0c0c0}
        .diff_add {background-color:#aaffaa}
        .diff_chg {background-color:#ffff77}
        .diff_sub {background-color:#ffaaaa}
"""

    def make_file(self, text1: str, text2: str, context: bool = False):
        doc = dominate.document(title="Font Table HTML")
        diff_table = self.get_diff_html_table(text1, text2, context)
        with doc.head:
            meta(charset="utf-8")
            style(raw(self.STYLE_RAW))
        with doc.body:
            raw(diff_table)
        return doc.render()

    def get_diff_html_table(self, text1: str, text2: str, context: bool = False):
        self.old_original_lines = text1.splitlines()
        if text1.endswith(os.linesep):
            self.old_original_lines.append("")
        self.new_original_lines = text2.splitlines()
        if text2.endswith(os.linesep):
            self.new_original_lines.append("")
        diffs = self.diff_main(text1, text2)
        self.diff_cleanupSemantic(diffs)
        return self._get_diff_html_table(diffs, context)

    def _get_diff_html_table(self, diffs: List[Tuple[bool, str]], context: bool):
        html_table = table(cls="diff", cellspacing="0", cellpadding="0", rules="groups")
        with html_table:
            colgroup()
            colgroup()
            colgroup()
            colgroup()
            colgroup()
            old_lines, new_lines, old_row_number_lines, new_row_number_lines = self._get_diff_lines(diffs, context)

            jump_links = []
            jump_link_lines = []
            pre_jump = ""
            for old_line, new_line in zip(old_lines, new_lines):
                if old_line == new_line == "":
                    jump = pre_jump
                elif old_line != new_line:
                    jump = "n"
                else:
                    jump = ""
                if pre_jump != jump:
                    jump_link_lines.append(jump)
                    if jump:
                        jump_links.append(self.random_name())
                else:
                    jump_link_lines.append("")
                pre_jump = jump

            if not jump_link_lines[0]:
                jump_links.append(self.random_name())

            with tbody():
                jump_link_count = 0
                for i, value in enumerate(zip(old_lines, new_lines, old_row_number_lines, new_row_number_lines, jump_link_lines)):
                    old_line, new_line, old_row_number_line, new_row_number_line, jump_link_line = value
                    with tr():
                        td(old_row_number_line, cls="diff_header")
                        td(raw(old_line), nowrap="nowrap")
                        if i == 0:
                            with td(cls="diff_next", id=jump_links[jump_link_count - 1]):
                                a("f", href=f"#{jump_links[jump_link_count]}")
                            jump_link_count += 1
                        else:
                            if jump_link_line:
                                if (len(jump_links) - 1) == jump_link_count:
                                    val = "t"
                                else:
                                    val = "n"
                                with td(cls="diff_next", id=jump_links[jump_link_count - 1]):
                                    a(val, href=f"#{jump_links[jump_link_count]}")
                                jump_link_count += 1
                            else:
                                td("", cls="diff_next")
                        td(new_row_number_line, cls="diff_header")
                        td(raw(new_line), nowrap="nowrap")
        return html_table.render()

    def random_name(self, n=8):
        return "".join(random.choices(string.ascii_letters + string.digits, k=n))

    def convert_to_html_text(self, text: str, tag: str = "{}"):
        html_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace(" ", "&nbsp;")
        return tag.format(html_text)

    def _get_diff_lines(self, diffs: List[Tuple[bool, str]], context: bool):
        old_plain_lines = []
        new_plain_lines = []
        old_html_lines = []
        new_html_lines = []
        last_old_plain_text = ""
        last_new_plain_text = ""
        last_old_html_text = ""
        last_new_html_text = ""

        old_row_number_lines = []
        new_row_number_lines = []
        omit_rows = []

        DEL_TAG = '<del class="diff_sub">{}</del>'
        INS_TAG = '<ins class="diff_add">{}</ins>'

        for (flag, data) in diffs:
            lines = data.splitlines()

            if self.wrapcolumn:
                old_lines = []
                new_lines = []
                for i, line in enumerate(lines[:]):
                    if i == 0:
                        old_split_lines = []
                        old_top_line_count = self.wrapcolumn - len(last_old_plain_text)
                        old_split_lines.append(line[:old_top_line_count])
                        if len(line) > old_top_line_count:
                            edit_line = line[old_top_line_count:]
                            if edit_line:
                                old_split_lines.extend([edit_line[j : j + self.wrapcolumn] for j in range(0, len(edit_line), self.wrapcolumn)])
                            else:
                                old_split_lines.append("")

                        new_split_lines = []
                        new_top_line_count = self.wrapcolumn - len(last_new_plain_text)
                        new_split_lines.append(line[:new_top_line_count])
                        if len(line) > new_top_line_count:
                            edit_line = line[new_top_line_count:]
                            if edit_line:
                                new_split_lines.extend([edit_line[j : j + self.wrapcolumn] for j in range(0, len(edit_line), self.wrapcolumn)])
                            else:
                                new_split_lines.append("")
                        while len(old_split_lines) < len(new_split_lines):
                            old_split_lines.append("")
                        while len(new_split_lines) < len(old_split_lines):
                            new_split_lines.append("")
                        old_lines.extend(old_split_lines)
                        new_lines.extend(new_split_lines)
                    else:
                        edit_line = line
                        if line:
                            split_lines = [edit_line[j : j + self.wrapcolumn] for j in range(0, len(edit_line), self.wrapcolumn)]
                            old_lines.extend(split_lines)
                            new_lines.extend(split_lines)
                        else:
                            old_lines.append("")
                            new_lines.append("")
            else:
                old_lines = lines
                new_lines = lines

            if data.endswith(os.linesep):
                old_lines.append("")
                new_lines.append("")

            html_tag = INS_TAG if flag == self.DIFF_INSERT else DEL_TAG if flag == self.DIFF_DELETE else "{}"

            for i, v in enumerate(zip(old_lines, new_lines)):
                old_line, new_line = v
                if i == 0:
                    old_plain_text = last_old_plain_text + old_line
                    new_plain_text = last_new_plain_text + new_line
                    old_html_text = last_old_html_text + self.convert_to_html_text(old_line, html_tag)
                    new_html_text = last_new_html_text + self.convert_to_html_text(new_line, html_tag)
                else:
                    old_plain_text = old_line
                    new_plain_text = new_line
                    old_html_text = self.convert_to_html_text(old_line, html_tag)
                    new_html_text = self.convert_to_html_text(new_line, html_tag)

                if flag == self.DIFF_DELETE:
                    old_plain_lines.append(old_plain_text)
                    old_html_lines.append(old_html_text)
                elif flag == self.DIFF_INSERT:
                    new_plain_lines.append(new_plain_text)
                    new_html_lines.append(new_html_text)
                elif flag == self.DIFF_EQUAL:
                    while len(old_html_lines) < len(new_html_lines):
                        old_plain_lines.append(None)
                        old_html_lines.append("")
                    while len(new_html_lines) < len(old_html_lines):
                        new_plain_lines.append(None)
                        new_html_lines.append("")
                    old_plain_lines.append(old_plain_text)
                    old_html_lines.append(old_html_text)
                    new_plain_lines.append(new_plain_text)
                    new_html_lines.append(new_html_text)
                else:
                    raise Exception("Unknonw")
            else:
                if flag == self.DIFF_DELETE:
                    last_old_plain_text = old_plain_lines.pop(-1)
                    last_old_html_text = old_html_lines.pop(-1)
                elif flag == self.DIFF_INSERT:
                    last_new_plain_text = new_plain_lines.pop(-1)
                    last_new_html_text = new_html_lines.pop(-1)
                elif flag == self.DIFF_EQUAL:
                    last_old_plain_text = old_plain_lines.pop(-1)
                    last_old_html_text = old_html_lines.pop(-1)
                    last_new_plain_text = new_plain_lines.pop(-1)
                    last_new_html_text = new_html_lines.pop(-1)
            if context:
                if flag == self.DIFF_EQUAL:
                    if len(old_lines) > 5:
                        omit_rows.append((len(old_plain_lines) - len(old_lines) + 4, len(old_plain_lines) - 2))

        else:
            old_plain_lines.append(last_old_plain_text)
            old_html_lines.append(last_old_html_text)
            new_plain_lines.append(last_new_plain_text)
            new_html_lines.append(last_new_html_text)
            while len(old_html_lines) < len(new_html_lines):
                old_plain_lines.append(None)
                old_html_lines.append("")
            while len(new_html_lines) < len(old_html_lines):
                new_plain_lines.append(None)
                new_html_lines.append("")

        old_row_number_lines = self._get_line_numbers(self.old_original_lines, old_plain_lines)
        new_row_number_lines = self._get_line_numbers(self.new_original_lines, new_plain_lines)

        if context:
            separation = "~" * self.wrapcolumn if self.wrapcolumn else "~" * 20
            for start, end in reversed(omit_rows):
                old_html_lines = old_html_lines[:start] + [separation] + old_html_lines[end:]
                new_html_lines = new_html_lines[:start] + [separation] + new_html_lines[end:]
                old_row_number_lines = old_row_number_lines[:start] + [""] + old_row_number_lines[end:]
                new_row_number_lines = new_row_number_lines[:start] + [""] + new_row_number_lines[end:]
        return old_html_lines, new_html_lines, old_row_number_lines, new_row_number_lines

    def _get_line_numbers(self, original_lines: List[str], custom_lines: List[str]):
        line_numbers = []
        line_count = 0
        original_line = original_lines.pop(0)
        for custom_line in custom_lines:
            if custom_line is None:
                line_numbers.append("")
                continue
            if original_line == custom_line or (custom_line and original_line.startswith(custom_line)):
                line_count += 1
                line_numbers.append(line_count)
                if original_lines:
                    original_line = original_lines.pop(0)
                else:
                    break
            else:
                line_numbers.append("")
        if len(line_numbers) < len(custom_lines):
            line_numbers.extend([""] * (len(custom_lines) - len(line_numbers)))
        return line_numbers


def sample(text1: str, text2: str, out_html_path: str):
    fast_diff_report = FastDiffReport(wrapcolumn=60)
    res = fast_diff_report.make_file(text1, text2, context=False)

    with open(out_html_path, mode="w", encoding="utf-8") as f:
        f.write(res)
