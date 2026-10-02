"""story.py 的行为测试：在临时工作区上验证账本写入规则与命令输出。

运行：python -m unittest test_story（在本目录下）。
"""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

import story


class StoryTestCase(unittest.TestCase):
    """每个用例使用独立的临时工作区，并提供命令执行与账本读取辅助。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        # 写命令要求 .agent 已存在；缺失场景由 AgentDirGuardTests 单独构造。
        (self.root / ".agent").mkdir()

    def run_cmd(self, *argv):
        """执行命令，返回 (退出码, stdout, stderr)。"""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = story.main(["--cwd", str(self.root), *argv])
            except SystemExit as exit_request:  # 用法错误由解析器直接退出
                code = exit_request.code
        return code, out.getvalue(), err.getvalue()

    def ok(self, *argv):
        """执行命令并断言成功，返回 stdout。"""
        code, out, err = self.run_cmd(*argv)
        self.assertEqual(code, 0, err)
        return out

    def fail(self, *argv):
        """执行命令并断言以退出码 1 失败，返回 stderr。"""
        code, _, err = self.run_cmd(*argv)
        self.assertEqual(code, 1)
        self.assertTrue(err.startswith("error: "), err)
        return err

    def path(self, relative):
        return self.root / relative

    def text(self, relative):
        return self.path(relative).read_text(encoding="utf-8")

    def doc(self, relative):
        return yaml.safe_load(self.text(relative))

    def setup_milestone(self, name="切片1"):
        self.ok("milestone", "create", name)

    def ledger_path(self, slug="主题A"):
        return f".agent/story/{slug}/index.yaml"

    def write(self, relative, content):
        """直接写入原始文本，用于构造手写或损坏的账本。"""
        target = self.path(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


class MilestoneTests(StoryTestCase):
    def test_create_writes_date_unquoted_and_switches_current(self):
        self.setup_milestone("切片1")
        self.ok("milestone", "create", "切片2")
        text = self.text(".agent/milestones.yaml")
        self.assertIn("current: 切片2", text)
        self.assertRegex(text, r"created: \d{4}-\d{2}-\d{2}\n")
        self.assertNotIn("'", text)

    def test_no_switch_keeps_current(self):
        self.setup_milestone("切片1")
        self.ok("milestone", "create", "切片2", "--no-switch")
        self.assertEqual(self.doc(".agent/milestones.yaml")["current"], "切片1")

    def test_use_and_errors(self):
        self.setup_milestone("切片1")
        self.ok("milestone", "create", "切片2")
        self.ok("milestone", "use", "切片1")
        self.assertEqual(self.doc(".agent/milestones.yaml")["current"], "切片1")
        self.fail("milestone", "use", "不存在")
        self.fail("milestone", "create", "切片1")
        self.fail("milestone", "create", "a/b")


class NextIdTests(StoryTestCase):
    def test_requirement_ids_are_sequential_and_omit_empty_fields(self):
        self.setup_milestone()
        self.assertEqual(self.ok("next-id", "主题A", "requirement", "第一").strip(), "requirement 1 主题A 待设计")
        self.ok("next-id", "主题A", "requirement", "第二", "--file", "切片1/需求2_第二.md")
        data = self.doc(self.ledger_path())
        self.assertEqual(data["requirement"], 2)
        self.assertEqual(data["bug"], 0)
        self.assertNotIn("bugs", data)
        self.assertEqual(list(data["items"][0]), ["id", "title", "milestone", "status"])
        self.assertEqual(data["items"][1]["file"], "切片1/需求2_第二.md")
        self.assertNotIn("null", self.text(self.ledger_path()))
        self.assertIn("\n  - id: 1", self.text(self.ledger_path()))

    def test_counter_wins_over_directory_contents(self):
        self.setup_milestone()
        (self.root / ".agent/story/主题A/切片1").mkdir(parents=True)
        (self.root / ".agent/story/主题A/切片1/需求9_历史.md").write_text("x", encoding="utf-8")
        self.ok("next-id", "主题A", "requirement", "新")
        self.assertEqual(self.doc(self.ledger_path())["items"][0]["id"], 1)

    def test_bug_req_is_integer_and_omitted_when_absent(self):
        self.setup_milestone()
        self.ok("next-id", "主题A", "bug", "有关联", "--req", "3")
        self.ok("next-id", "主题A", "bug", "无关联")
        bugs = self.doc(self.ledger_path())["bugs"]
        self.assertEqual(bugs[0]["req"], 3)
        self.assertNotIn("req", bugs[1])
        self.assertEqual(bugs[0]["status"], "已确认")
        self.assertEqual(list(bugs[0]), ["id", "title", "req", "milestone", "status"])

    def test_file_id_placeholder_is_replaced_and_printed(self):
        self.setup_milestone()
        out = self.ok("next-id", "主题A", "requirement", "标题", "--file", "切片1/需求{id}_标题.md")
        self.assertEqual(out.strip(), "requirement 1 主题A 待设计 切片1/需求1_标题.md")
        out = self.ok("next-id", "主题A", "bug", "缺陷", "--file", "切片1/bug/Bug{id}_缺陷.md")
        self.assertEqual(out.strip(), "bug 1 主题A 已确认 切片1/bug/Bug1_缺陷.md")
        data = self.doc(self.ledger_path())
        self.assertEqual(data["items"][0]["file"], "切片1/需求1_标题.md")
        self.assertEqual(data["bugs"][0]["file"], "切片1/bug/Bug1_缺陷.md")
        self.ok("next-id", "主题A", "requirement", "第二", "--file", "切片1/需求{id}_第二.md")
        self.assertEqual(self.doc(self.ledger_path())["items"][1]["file"], "切片1/需求2_第二.md")

    def test_errors_leave_files_untouched(self):
        self.fail("next-id", "主题A", "requirement", "无 milestone")
        self.assertFalse(self.path(".agent/story").exists())
        self.setup_milestone()
        self.fail("next-id", "quick", "requirement", "保留名")
        self.fail("next-id", "主题A", "requirement", "坏状态", "--status", "乱写")
        self.fail("next-id", "主题A", "requirement", "带 req", "--req", "1")
        self.assertFalse(self.path(self.ledger_path()).exists())


class SetStatusTests(StoryTestCase):
    def setUp(self):
        super().setUp()
        self.setup_milestone()
        self.ok("next-id", "主题A", "requirement", "需求一")
        self.ok("next-id", "主题A", "bug", "缺陷一")

    def entry(self, kind="items"):
        return self.doc(self.ledger_path())[kind][0]

    def set(self, *extra):
        return self.ok("set-status", "--kind", "requirement", "--slug", "主题A", "--id", "1", *extra)

    def test_normal_status_clears_stack(self):
        self.set("--status", "已确认")
        self.set("--status", "阻塞")
        self.assertEqual(self.entry()["prior_status"], ["已确认"])
        self.set("--status", "已完成")
        self.assertNotIn("prior_status", self.entry())

    def test_repeated_block_does_not_push_again(self):
        self.set("--status", "实现中")
        out = self.set("--status", "阻塞")
        self.assertIn("进入前: 实现中", out)
        self.set("--status", "阻塞")
        self.assertEqual(self.entry()["prior_status"], ["实现中"])
        self.set("--restore")
        self.assertEqual(self.entry()["status"], "实现中")
        self.assertNotIn("prior_status", self.entry())

    def test_review_state_is_not_a_status(self):
        self.fail("set-status", "--kind", "requirement", "--slug", "主题A", "--id", "1", "--status", "Review 中")

    def test_restore_with_empty_stack_fails_without_writing(self):
        before = self.text(self.ledger_path())
        self.fail("set-status", "--kind", "requirement", "--slug", "主题A", "--id", "1", "--restore")
        self.assertEqual(self.text(self.ledger_path()), before)

    def test_keywords_replace_and_clear_keep_status(self):
        self.set("--status", "已确认")
        self.set("--keywords", "story.py, 账本脚本，story.py")
        self.assertEqual(self.entry()["keywords"], ["story.py", "账本脚本"])
        self.assertEqual(self.entry()["status"], "已确认")
        self.assertEqual(list(self.entry()), ["id", "title", "milestone", "status", "keywords"])
        self.set("--keywords", "")
        self.assertNotIn("keywords", self.entry())

    def test_review_paths_written_and_cleared(self):
        self.set("--review-kind", "code", "--review-path", "切片1/review/需求1_代码review.md")
        self.assertEqual(self.entry()["code_review"], "切片1/review/需求1_代码review.md")
        self.set("--clear-review")
        self.assertNotIn("code_review", self.entry())
        self.fail("set-status", "--kind", "requirement", "--slug", "主题A", "--id", "1", "--review-kind", "code")

    def test_bug_status_enum_and_field_restrictions(self):
        self.ok("set-status", "--kind", "bug", "--slug", "主题A", "--id", "1", "--status", "已修复")
        self.assertEqual(self.entry("bugs")["status"], "已修复")
        self.fail("set-status", "--kind", "bug", "--slug", "主题A", "--id", "1", "--status", "阻塞")
        self.fail("set-status", "--kind", "bug", "--slug", "主题A", "--id", "1", "--keywords", "a")

    def test_argument_validation(self):
        self.fail("set-status", "--kind", "requirement", "--slug", "主题A", "--id", "1")
        self.fail("set-status", "--kind", "requirement", "--slug", "主题A", "--id", "1", "--status", "已确认", "--restore")
        self.fail("set-status", "--kind", "requirement", "--slug", "主题A", "--id", "9", "--status", "已确认")

    def test_unknown_keys_dropped_and_existing_fields_preserved(self):
        path = self.path(self.ledger_path())
        data = self.doc(self.ledger_path())
        data["items"][0].update({"continues": [2], "extra": "x"})
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        self.set("--status", "已确认")
        entry = self.entry()
        self.assertEqual(entry["continues"], [2])
        self.assertNotIn("extra", entry)


class QuickTests(StoryTestCase):
    def test_quick_status_update_and_restrictions(self):
        self.setup_milestone()
        quick = self.path(".agent/story/quick/切片1/index.yaml")
        quick.parent.mkdir(parents=True)
        quick.write_text("items:\n  - title: 修日志\n    status: 已确认\n", encoding="utf-8")
        self.ok("set-status", "--kind", "quick", "--title", "修日志", "--status", "已完成")
        self.assertEqual(self.doc(".agent/story/quick/切片1/index.yaml"), {"items": [{"title": "修日志", "status": "已完成"}]})
        self.fail("set-status", "--kind", "quick", "--title", "修日志", "--restore")
        self.fail("set-status", "--kind", "quick", "--title", "不存在", "--status", "已完成")
        self.fail("set-status", "--kind", "quick", "--title", "修日志", "--status", "阻塞")


class QuickCreateTests(StoryTestCase):
    QUICK = ".agent/story/quick/切片1/index.yaml"

    def setUp(self):
        super().setUp()
        self.setup_milestone()

    def create(self, *extra):
        return self.ok("set-status", "--kind", "quick", "--title", "新任务", "--create", *extra)

    def test_create_defaults_to_confirmed(self):
        self.assertEqual(self.create().strip(), "quick 新任务 已确认")
        self.ok("set-status", "--kind", "quick", "--title", "第二个", "--create", "--status", "待确认")
        self.assertEqual(self.doc(self.QUICK), {"items": [
            {"title": "新任务", "status": "已确认"}, {"title": "第二个", "status": "待确认"}]})
        self.assertIn("quick 切片1: 新任务, 第二个", self.ok("init"))

    def test_create_errors_leave_file_untouched(self):
        self.create()
        before = self.text(self.QUICK)
        self.fail("set-status", "--kind", "quick", "--title", "新任务", "--create")
        self.fail("set-status", "--kind", "quick", "--title", "别的", "--create", "--status", "阻塞")
        self.fail("set-status", "--kind", "quick", "--title", "新任务")  # 更新已有条目必须给 --status
        self.fail("set-status", "--kind", "quick", "--title", "别的", "--create", "--keywords", "a")
        self.fail("set-status", "--kind", "requirement", "--slug", "主题A", "--id", "1", "--create")
        self.assertEqual(self.text(self.QUICK), before)


class InitDetailsTests(StoryTestCase):
    def test_init_slug_lists_all_populated_fields(self):
        self.setup_milestone()
        self.ok("next-id", "主题A", "requirement", "有文档", "--file", "切片1/需求{id}_有文档.md")
        self.ok("set-status", "--kind", "requirement", "--slug", "主题A", "--id", "1", "--keywords", "词一,词二",
                "--review-kind", "code", "--review-path", "切片1/review/r.md")
        self.ok("next-id", "主题A", "requirement", "无文档")
        self.ok("next-id", "主题A", "bug", "缺陷", "--req", "1", "--file", "切片1/bug/Bug{id}_缺陷.md")
        data = self.doc(self.ledger_path())
        data["items"][0]["continued_by"] = [2]
        data["items"][1]["continues"] = [1]
        self.write(self.ledger_path(), yaml.safe_dump(data, allow_unicode=True, sort_keys=False))
        lines = self.ok("init", "主题A").splitlines()
        self.assertIn("1 有文档 待设计 file=切片1/需求1_有文档.md keywords=词一,词二 continued_by=2 code_review=切片1/review/r.md", lines)
        self.assertIn("2 无文档 待设计 continues=1", lines)
        self.assertIn("bug1 缺陷 已确认 req=1 file=切片1/bug/Bug1_缺陷.md", lines)


class AgentDirGuardTests(StoryTestCase):
    def setUp(self):
        super().setUp()
        self.path(".agent").rmdir()

    def test_write_commands_refuse_to_create_agent_dir(self):
        for argv in (
            ("milestone", "create", "切片1"),
            ("next-id", "主题A", "requirement", "标题", "--milestone", "切片1"),
            ("set-status", "--kind", "quick", "--title", "t", "--create", "--milestone", "切片1"),
        ):
            self.assertIn(".agent 不存在", self.fail(*argv))
        self.assertFalse(self.path(".agent").exists())

    def test_read_commands_still_work(self):
        self.assertIn("agent no", self.ok("init"))
        self.assertEqual(self.ok("status").strip(), "无条目")
        self.assertEqual(self.ok("search", "任意词").strip(), "无命中")


class ReadOnlyCommandTests(StoryTestCase):
    def setUp(self):
        super().setUp()
        self.setup_milestone()
        self.ok("next-id", "缓存优化", "requirement", "磁盘缓存策略", "--file", "切片1/需求1_磁盘缓存策略.md")
        self.ok("set-status", "--kind", "requirement", "--slug", "缓存优化", "--id", "1", "--keywords", "磁盘缓存,LRU")
        self.ok("next-id", "登录改造", "requirement", "登录流程")
        self.ok("set-status", "--kind", "requirement", "--slug", "登录改造", "--id", "1", "--status", "已确认")
        self.ok("set-status", "--kind", "requirement", "--slug", "登录改造", "--id", "1", "--status", "阻塞")

    def test_search_ranks_and_filters_generic_terms(self):
        out = self.ok("search", "LRU").strip().splitlines()
        self.assertEqual(out, ["缓存优化/1 磁盘缓存策略 [待设计·切片1] 切片1/需求1_磁盘缓存策略.md"])
        self.assertEqual(self.ok("search", "不存在的词").strip(), "无命中")
        self.fail("search", "设计", "x")

    def test_search_ignores_quick_directory(self):
        quick = self.path(".agent/story/quick/切片1/index.yaml")
        quick.parent.mkdir(parents=True)
        quick.write_text("items:\n  - title: 缓存清理\n    status: 已确认\n", encoding="utf-8")
        self.assertNotIn("quick", self.ok("search", "缓存清理"))

    def test_status_groups_with_stack_note(self):
        out = self.ok("status")
        self.assertIn("待设计 1\n  缓存优化/1 磁盘缓存策略\n", out)
        self.assertIn("阻塞 1\n  登录改造/1 登录流程 (进入前: 已确认)\n", out)

    def test_status_quick_and_missing_current(self):
        self.assertEqual(self.ok("status", "--kind", "quick").strip(), "无条目")
        (self.root / ".agent/milestones.yaml").unlink()
        self.fail("status", "--kind", "quick")

    def test_init_reports_environment_and_topic(self):
        out = self.ok("init", "缓存优化")
        self.assertIn("agent yes", out)
        self.assertIn("current 切片1", out)
        self.assertIn("topics 登录改造 缓存优化", out)
        self.assertIn("topic 缓存优化 root=.agent/story/缓存优化 ledger=.agent/story/缓存优化/index.yaml dir=.agent/story/缓存优化/切片1", out)
        self.assertIn("1 磁盘缓存策略 待设计", out)

    def test_init_warnings(self):
        empty = tempfile.TemporaryDirectory()
        self.addCleanup(empty.cleanup)
        self.root = Path(empty.name)
        self.assertIn("! 工作目录下没有 .agent", self.ok("init"))
        (self.root / ".agent").mkdir()
        self.assertIn("! 缺少 .agent/milestones.yaml", self.ok("init"))
        self.setup_milestone()
        self.assertIn("! 没有正式主题 不存在", self.ok("init", "不存在"))


class SearchRankingTests(StoryTestCase):
    def setUp(self):
        super().setUp()
        self.setup_milestone()
        self.ok("next-id", "主题B", "requirement", "缓存")  # 标题全等 + keywords 精确
        self.ok("set-status", "--kind", "requirement", "--slug", "主题B", "--id", "1", "--keywords", "缓存")
        self.ok("next-id", "主题B", "requirement", "磁盘缓存清理")  # 仅标题包含
        self.ok("next-id", "主题B", "requirement", "缓存扩容")  # 仅标题包含，与上一条同分
        self.ok("set-status", "--kind", "requirement", "--slug", "主题B", "--id", "2", "--status", "已确认")

    def labels(self, *argv):
        return [line.split(" ")[0] for line in self.ok("search", *argv).splitlines() if not line.startswith("!")]

    def test_score_then_slug_and_id_order(self):
        self.assertEqual(self.labels("缓存"), ["主题B/1", "主题B/2", "主题B/3"])

    def test_limit_truncates_with_notice(self):
        out = self.ok("search", "缓存", "--limit", "2")
        self.assertEqual(len(out.splitlines()), 3)
        self.assertIn("! 共 3 条命中，仅显示前 2 条", out)
        self.fail("search", "缓存", "--limit", "0")

    def test_status_and_slug_filters(self):
        self.assertEqual(self.labels("缓存", "--status", "已确认"), ["主题B/2"])
        self.assertEqual(self.ok("search", "缓存", "--slug", "主题C").strip(), "无命中")


class SearchBugTests(StoryTestCase):
    def setUp(self):
        super().setUp()
        self.setup_milestone()
        self.ok("next-id", "主题D", "requirement", "登录崩溃修复")
        self.ok("next-id", "主题D", "bug", "登录崩溃", "--req", "1", "--file", "切片1/bug/Bug{id}_登录崩溃.md")
        self.ok("next-id", "主题D", "bug", "支付超时")

    def test_bug_hit_uses_bug_label_and_sorts_after_requirement_on_tie(self):
        lines = self.ok("search", "登录崩溃").splitlines()
        self.assertEqual([line.split(" ")[0] for line in lines], ["主题D/1", "主题D/bug1"])
        self.assertEqual(lines[1], "主题D/bug1 登录崩溃 [已确认·切片1] 切片1/bug/Bug1_登录崩溃.md")

    def test_bug_without_file_and_status_filter(self):
        self.assertEqual(self.ok("search", "支付超时").strip(), "主题D/bug2 支付超时 [已确认·切片1] -")
        self.ok("set-status", "--kind", "bug", "--slug", "主题D", "--id", "2", "--status", "修复中")
        self.assertEqual(self.ok("search", "支付超时", "--status", "已确认").strip(), "无命中")
        self.assertIn("主题D/bug2", self.ok("search", "支付超时", "--status", "修复中"))


class LedgerConsistencyTests(StoryTestCase):
    def test_counter_below_max_id_is_rejected_and_file_untouched(self):
        self.setup_milestone()
        self.write(".agent/story/主题A/index.yaml",
                   "requirement: 1\nbug: 0\nitems:\n"
                   "  - {id: 1, title: a, milestone: 切片1, status: 待设计}\n"
                   "  - {id: 2, title: b, milestone: 切片1, status: 待设计}\n")
        before = self.text(".agent/story/主题A/index.yaml")
        self.assertIn("计数器（1）小于已有最大编号（2）", self.fail("next-id", "主题A", "requirement", "c"))
        self.assertEqual(self.text(".agent/story/主题A/index.yaml"), before)

    def test_bug_counter_and_duplicate_ids_are_rejected(self):
        self.setup_milestone()
        self.write(".agent/story/主题A/index.yaml",
                   "requirement: 0\nbug: 0\nbugs:\n  - {id: 1, title: x, milestone: 切片1, status: 已确认}\n")
        self.assertIn("bug 计数器（0）小于已有最大编号（1）", self.fail("status"))
        self.write(".agent/story/主题A/index.yaml",
                   "requirement: 2\nbug: 0\nitems:\n"
                   "  - {id: 1, title: a, milestone: 切片1, status: 待设计}\n"
                   "  - {id: 1, title: b, milestone: 切片1, status: 待设计}\n")
        self.assertIn("id 有重复", self.fail("status"))

    def test_legacy_key_is_rejected_with_hint(self):
        self.setup_milestone()
        self.write(".agent/story/主题A/index.yaml",
                   "需求: 1\nbug: 0\nitems:\n  - {id: 1, title: a, milestone: 切片1, status: 待设计}\n")
        self.assertIn("旧键 需求", self.fail("next-id", "主题A", "requirement", "c"))


class WriteFormatTests(StoryTestCase):
    def test_long_title_with_spaces_is_not_folded(self):
        self.setup_milestone()
        title = " ".join(["long"] * 40)
        self.ok("next-id", "主题A", "requirement", title)
        self.assertIn(f"title: {title}\n", self.text(self.ledger_path()))
        self.assertEqual(self.doc(self.ledger_path())["items"][0]["title"], title)

    def test_backslashes_in_paths_are_normalized(self):
        self.setup_milestone()
        self.ok("next-id", "主题A", "requirement", "标题", "--file", "切片1\\需求{id}_标题.md")
        self.ok("set-status", "--kind", "requirement", "--slug", "主题A", "--id", "1",
                "--review-kind", "design", "--review-path", "切片1\\review\\r.md")
        entry = self.doc(self.ledger_path())["items"][0]
        self.assertEqual(entry["file"], "切片1/需求1_标题.md")
        self.assertEqual(entry["design_review"], "切片1/review/r.md")


class LedgerValidationTests(StoryTestCase):
    """损坏账本必须走 `error:` 通道，并且不改动任何文件。"""

    HEADER = "requirement: 1\nbug: 0\n"

    def ledger(self, body, header=HEADER):
        self.write(self.ledger_path(), header + body)
        return self.text(self.ledger_path())

    def test_non_string_title_is_rejected_on_search(self):
        self.setup_milestone()
        self.ledger("items:\n  - id: 1\n    title: true\n    milestone: 切片1\n    status: 待设计\n")
        self.assertIn("title 必须是字符串", self.fail("search", "true"))

    def test_missing_id_is_rejected_and_file_untouched(self):
        self.setup_milestone()
        before = self.ledger("items:\n  - title: 无id\n    milestone: 切片1\n    status: 待设计\n")
        self.assertIn("缺少整数 id", self.fail("set-status", "--kind", "requirement", "--slug", "主题A", "--id", "1", "--status", "设计中"))
        self.assertEqual(self.text(self.ledger_path()), before)

    def test_boolean_counter_is_not_treated_as_one(self):
        self.setup_milestone()
        before = self.ledger("", header="requirement: true\nbug: 0\n")
        self.assertIn("requirement 必须是非负整数", self.fail("next-id", "主题A", "requirement", "标题"))
        self.assertEqual(self.text(self.ledger_path()), before)

    def test_negative_counter_and_structure_errors(self):
        self.setup_milestone()
        self.ledger("", header="requirement: -1\nbug: 0\n")
        self.fail("status")
        self.ledger("items: {a: 1}\n")
        self.fail("status")
        self.ledger("- 1\n- 2\n", header="")
        self.fail("status")
        self.ledger("items:\n  - id: 1\n    title: t\n    milestone: 切片1\n    status: 阻塞\n    prior_status: 已确认\n")
        self.assertIn("prior_status 必须是列表", self.fail("status"))

    def test_invalid_quick_ledger(self):
        self.setup_milestone()
        self.write(".agent/story/quick/切片1/index.yaml", "items:\n  - title: 缺状态\n")
        self.fail("status", "--kind", "quick")

    def test_empty_ledger_file_is_a_valid_empty_ledger(self):
        self.setup_milestone()
        self.write(self.ledger_path(), "")
        self.assertEqual(self.ok("next-id", "主题A", "requirement", "首条").strip(), "requirement 1 主题A 待设计")


class MilestoneValidationTests(StoryTestCase):
    def milestones(self, created):
        self.write(".agent/milestones.yaml", f"current: 切片1\nmilestones:\n  切片1:\n    created: {created}\n")
        return self.text(".agent/milestones.yaml")

    def test_invalid_created_blocks_write_but_not_diagnosis(self):
        before = self.milestones("not-a-date")
        self.assertIn("created 缺失或不是 YYYY-MM-DD", self.fail("milestone", "create", "切片2"))
        self.assertEqual(self.text(".agent/milestones.yaml"), before)
        self.assertIn("current 切片1", self.ok("init"))

    def test_missing_created_is_rejected_on_write(self):
        self.write(".agent/milestones.yaml", "current: 切片1\nmilestones:\n  切片1: {}\n")
        self.fail("milestone", "use", "切片1")
        self.assertNotIn("null", self.text(".agent/milestones.yaml"))

    def test_timestamp_is_normalized_to_date(self):
        self.milestones("2026-01-01T12:00:00")
        self.ok("milestone", "create", "切片2")
        text = self.text(".agent/milestones.yaml")
        self.assertIn("created: 2026-01-01\n", text)
        self.assertNotIn("12:00", text)

    def test_milestones_must_be_mapping(self):
        self.write(".agent/milestones.yaml", "current: 切片1\nmilestones: [a, b]\n")
        self.fail("milestone", "create", "切片2")


class IoAndUsageTests(StoryTestCase):
    def test_read_failure_uses_error_channel(self):
        self.setup_milestone()
        self.ok("next-id", "主题A", "requirement", "标题")
        with mock.patch.object(Path, "read_text", side_effect=PermissionError("locked")):
            self.assertIn("无法读取", self.fail("status"))

    def test_replace_failure_cleans_temp_file(self):
        self.setup_milestone()
        with mock.patch.object(story.os, "replace", side_effect=PermissionError("locked")):
            self.assertIn("无法写入", self.fail("next-id", "主题A", "requirement", "标题"))
        self.assertEqual(list(self.root.rglob("*.tmp")), [])
        self.assertFalse(self.path(self.ledger_path()).exists())

    def test_usage_errors_exit_with_one_and_error_prefix(self):
        self.fail()
        self.fail("search")
        self.fail("milestone", "rename", "x")
        self.fail("next-id", "主题A", "requirement", "标题", "--req", "abc")


class ReservedNameTests(StoryTestCase):
    def test_windows_reserved_names_are_rejected(self):
        self.setup_milestone()
        for name in ("CON", "nul", "COM1", "lpt9.txt"):
            self.assertIn("保留名", self.fail("next-id", name, "requirement", "标题"))
            self.assertIn("保留名", self.fail("milestone", "create", name))
        self.assertFalse(self.path(".agent/story").exists())

    def test_similar_names_are_allowed(self):
        self.setup_milestone()
        self.ok("next-id", "CONSOLE", "requirement", "标题")
        self.ok("milestone", "create", "COM10")


if __name__ == "__main__":
    unittest.main()
