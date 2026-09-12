# Atlas workflows MCP bridge

This is a small read-only stdio server for using explicitly installed Atlas and
Spotter workflow packages through an MCP client. It takes a fixed startup
snapshot of the canonical core doctrine and skill Markdown; callers can list
skills, load one with its core doctrine, then read a package-relative reference.

Install its locked Python environment from this directory:

```sh
uv sync --frozen
```

Launch it with explicit package roots:

```sh
.venv/bin/python server.py --plugin atlas=/path/to/atlas --plugin spotter=/path/to/spotter
```

For a secure tunnel, use that command as the tunnel client's `mcp.commands`
entry. Keep credentials in the tunnel client's credential reference, never in
this server configuration or its command line.

The bridge does not read the filesystem after making its startup snapshot. It
cannot run skill scripts, activate hooks or agents, read mail/calendars, write
a tracker, create schedules, or perform external actions. An MCP connection
therefore provides workflow content and guidance, not the host-side plugin
runtime.
