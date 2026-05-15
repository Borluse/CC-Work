"""
Code Review Report Generator
============================

读取 YAML 输入 + 模板 HTML，输出最终的代码 Review 报告 HTML。
为兼容历史，仍接受 .json 后缀的输入（YAML 是 JSON 的超集）。

用法:
    python generate.py <input.yaml> <output.html>
"""

from __future__ import annotations
import sys
import re
from pathlib import Path
from html import escape as _esc

import yaml

TEMPLATE_FILE = Path(__file__).parent / "template.html"

# ---------- 内联代码渲染 ----------
# 将文本中 `xxx` 转成 <code>xxx</code>; **xxx** 转 <strong>; 其余 HTML 转义。
# 顺序: 先转义 -> 再替换 markdown 标记 (避免标记被转义掉)
_CODE_RE = re.compile(r"`([^`]+)`")
_STRONG_RE = re.compile(r"\*\*([^*]+)\*\*")


def md_inline(text: str) -> str:
    """支持 `code` 和 **strong** 的极简 inline 渲染。
    其余字符按 HTML 转义,避免 < > & 破坏结构。
    """
    if text is None:
        return ""
    s = _esc(str(text), quote=False)
    # 注意 `code` 内部不再做 ** 处理
    parts = []
    last = 0
    for m in _CODE_RE.finditer(s):
        parts.append(_STRONG_RE.sub(r"<strong>\1</strong>", s[last:m.start()]))
        # code 内部不二次转义(已经转过)
        parts.append(f"<code>{m.group(1)}</code>")
        last = m.end()
    parts.append(_STRONG_RE.sub(r"<strong>\1</strong>", s[last:]))
    return "".join(parts)


def raw(text: str) -> str:
    """已经是 HTML 片段,直接用; None -> 空串."""
    return "" if text is None else str(text)


# ---------- 各区块渲染 ----------

SEV_CLASS = {"crit": "crit", "warn": "warn", "opt": "opt"}
SEV_GLYPH = {"crit": "!", "warn": "~", "opt": "+"}
SEV_LABEL = {"crit": "必须修改", "warn": "建议修改", "opt": "可选优化"}
SEV_EN = {"crit": "Blocking", "warn": "Suggested", "opt": "Optional"}


def render_topbar(d: dict) -> str:
    return f"""
  <div class="topbar">
    <div class="left">
      <span>{md_inline(d.get('doc_id', ''))}</span>
      <span style="color:var(--text-4)">·</span>
      <span>{md_inline(d.get('module_path', ''))}</span>
    </div>
    <div class="right">
      <span class="pulse"></span>
      <span>{md_inline(d.get('alert', ''))}</span>
    </div>
  </div>
"""


def render_header(d: dict) -> str:
    h = d.get("header", {})
    eyebrow = md_inline(h.get("eyebrow", ""))
    eyebrow_num = md_inline(h.get("eyebrow_num", ""))
    title_accent = md_inline(h.get("title_accent", ""))
    title_main = md_inline(h.get("title_main", ""))
    subtitle = md_inline(h.get("subtitle", ""))
    lede = md_inline(h.get("lede", ""))

    # 右上角结论徽章（与 §03 verdict 同源,镜像突出展示）
    v = d.get("verdict", {})
    status_big = md_inline(v.get("status_big", ""))
    status_small = md_inline(v.get("status_small", ""))
    verdict_badge = ""
    if status_big or status_small:
        verdict_badge = (
            '    <a class="header-verdict" href="#verdict" aria-label="跳到结论">'
            f'<div class="big">{status_big}</div>'
            f'<div class="small">{status_small}</div>'
            '</a>\n'
        )

    meta_html = []
    for item in h.get("meta", []):
        tint = item.get("tint", "")
        span2 = " span2" if item.get("span2") else ""
        cls = f"{tint}{span2}".strip()
        cls_attr = f' class="{cls}"' if cls else ""
        dd_cls = f' class="{item.get("dd_class")}"' if item.get("dd_class") else ""
        # dd 内可含 <br>;支持 list -> 用 <br> 连接
        val = item.get("value", "")
        if isinstance(val, list):
            val = "<br>".join(md_inline(v) for v in val)
        else:
            val = md_inline(val)
        meta_html.append(
            f'      <div{cls_attr}><dt>{md_inline(item.get("label",""))}</dt>'
            f'<dd{dd_cls}>{val}</dd></div>'
        )
    meta = "\n".join(meta_html)

    return f"""
  <header class="header">
{verdict_badge}    <div class="eyebrow">
      <span class="num">{eyebrow_num}</span>
      <span>{eyebrow}</span>
    </div>
    <h1>
      <span class="accent">{title_accent}</span>{title_main}<br>
      <span class="small">{subtitle}</span>
    </h1>
    <p class="lede">{lede}</p>

    <dl class="meta">
{meta}
    </dl>
  </header>
"""


def render_summary(d: dict) -> str:
    s = d.get("summary", {})
    paragraphs = "\n    ".join(
        f"<p>{md_inline(p)}</p>" for p in s.get("paragraphs", [])
    )

    risks_html = []
    for r in s.get("key_risks", []):
        sev = SEV_CLASS.get(r.get("severity", "warn"), "warn")
        risks_html.append(f"""      <div class="row {sev}">
        <span class="label"><span class="marker"></span>{md_inline(r.get('label',''))}</span>
        <span class="text">{md_inline(r.get('text',''))}</span>
      </div>""")
    risks = "\n".join(risks_html)

    return f"""
  <section class="summary">
    <h2>
      <span class="h2-num">§01</span>
      <span class="h2-text">总体评价</span>
      <span class="h2-en">Overview</span>
    </h2>
    {paragraphs}

    <div class="key-risks">
{risks}
    </div>
  </section>
"""


def render_issue(item: dict) -> str:
    sev = SEV_CLASS.get(item.get("severity", "warn"), "warn")
    fix = item.get("fix")
    fix_html = ""
    if fix:
        fix_html = f"""
        <div class="issue-fix">
          <span class="issue-fix-label">建议</span>
          <span>{md_inline(fix)}</span>
        </div>"""
    return f"""
    <article class="issue {sev}">
      <div class="issue-head">
        <span class="issue-id">{md_inline(item.get('id',''))}</span>
        <span class="issue-tag">{md_inline(item.get('tag',''))}</span>
        <span class="issue-loc">
          <span class="file">{md_inline(item.get('file',''))}</span>
          <span class="line">{md_inline(item.get('line',''))}</span>
        </span>
      </div>
      <div class="issue-body">
        <p class="issue-desc">{md_inline(item.get('desc',''))}</p>{fix_html}
      </div>
    </article>"""


def render_issues(d: dict) -> str:
    iss = d.get("issues", {})
    groups = []
    total = 0
    for sev in ("crit", "warn", "opt"):
        items = iss.get(sev, [])
        total += len(items)
        if not items:
            continue
        head = f"""
      <div class="group-head {sev}">
        <span class="glyph">{SEV_GLYPH[sev]}</span>
        <span class="label">{SEV_LABEL[sev]}</span>
        <span class="en">{SEV_EN[sev]}</span>
        <span class="count">{len(items)} item{'s' if len(items)!=1 else ''}</span>
      </div>"""
        body = "\n".join(render_issue({**it, "severity": it.get("severity", sev)}) for it in items)
        groups.append(f'    <div class="issue-group {sev}">{head}\n{body}\n    </div>')

    revoked = iss.get("revoked", [])
    revoked_html = ""
    for r in revoked:
        revoked_html += f"""
    <div class="revoked">
      <span class="tag">已撤销</span>
      {md_inline(r)}
    </div>"""

    return f"""
  <section>
    <h2>
      <span class="h2-num">§02</span>
      <span class="h2-text">问题清单</span>
      <span class="h2-en">Findings</span>
      <span class="h2-count">{total} items</span>
    </h2>
{''.join(groups)}
{revoked_html}
  </section>
"""


def render_verdict(d: dict) -> str:
    v = d.get("verdict", {})
    title = md_inline(v.get("title", ""))
    title_em = md_inline(v.get("title_em", ""))
    options_html = []
    for opt in v.get("options", []):
        active = " active" if opt.get("active") else ""
        options_html.append(
            f'<li class="{active.strip()}"><span class="check"></span>{md_inline(opt.get("text",""))}</li>'
            if active else
            f'<li><span class="check"></span>{md_inline(opt.get("text",""))}</li>'
        )
    options = "\n          ".join(options_html)

    status_big = md_inline(v.get("status_big", ""))
    status_small = md_inline(v.get("status_small", ""))

    return f"""
  <section id="verdict">
    <h2>
      <span class="h2-num">§03</span>
      <span class="h2-text">结论</span>
      <span class="h2-en">Verdict</span>
    </h2>
    <div class="verdict">
      <div>
        <div class="verdict-title">{title}<em> {title_em}</em></div>
        <ul>
          {options}
        </ul>
      </div>
      <div class="verdict-status">
        <div class="big">{status_big}</div>
        <div class="small">{status_small}</div>
      </div>
    </div>
  </section>
"""


def render_footer(d: dict) -> str:
    f = d.get("footer", {})
    return f"""
  <div class="footer">
    <span><b>变更记录 ·</b> {md_inline(f.get('changelog',''))}</span>
    <span class="end">{md_inline(f.get('end','— end of report —'))}</span>
  </div>
"""


# ---------- 主流程 ----------

def build_body(data: dict) -> str:
    return (
        render_topbar(data)
        + render_header(data)
        + render_summary(data)
        + render_issues(data)
        + render_verdict(data)
        + render_footer(data)
    )


# 标记: 模板中需要被替换的 body 区域
BODY_START = "<!-- {{BODY_START}} -->"
BODY_END = "<!-- {{BODY_END}} -->"


def render(data: dict) -> str:
    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    title = data.get("page_title") or data.get("header", {}).get("title_accent", "代码 Review 报告")
    template = re.sub(
        r"<title>.*?</title>",
        f"<title>{_esc(title, quote=False)}</title>",
        template,
        count=1,
    )
    if BODY_START not in template or BODY_END not in template:
        raise RuntimeError(
            f"模板中找不到 {BODY_START} / {BODY_END} 标记,无法替换 body 区。"
        )
    pre = template.split(BODY_START)[0] + BODY_START + "\n"
    post = "\n  " + BODY_END + template.split(BODY_END)[1]
    return pre + build_body(data) + post


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return
    if len(args) < 2:
        print("用法: python generate.py <input.json> <output.html>", file=sys.stderr)
        sys.exit(2)
    in_path = Path(args[0])
    out_path = Path(args[1])
    data = yaml.safe_load(in_path.read_text(encoding="utf-8"))
    out_path.write_text(render(data), encoding="utf-8")
    print(f"OK -> {out_path} ({out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
