#!/usr/bin/env python3
"""story.py 命令行入口。

实现全部在 story_core；MCP 服务（story_mcp.py）使用同一份实现。
保留 CLI 是为了测试、诊断，以及 MCP 不可用时的手工兜底。

用法：python story.py [--cwd DIR] <命令> ...，详细参数见 `<命令> --help`。
"""

import sys

from story_core import main

if __name__ == "__main__":
    sys.exit(main())
