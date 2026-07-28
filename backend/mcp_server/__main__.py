"""MCP server entrypoint. Claude Desktop launches this as a subprocess with an
arbitrary working directory, but backend.config.Settings() (.env path) and
backend.db (sqlite file path) both resolve relative to CWD *at import time*.
So we chdir to the repo root before any backend.* submodule other than this
package's own empty __init__.py is imported. This is why the imports below
are split around the chdir instead of grouped at the top of the file.
"""

import os
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
os.chdir(_REPO_ROOT)

from backend.db import create_db_and_tables  # noqa: E402
from backend.mcp_server.server import mcp  # noqa: E402


def main() -> None:
    create_db_and_tables()
    mcp.run()


if __name__ == "__main__":
    main()
