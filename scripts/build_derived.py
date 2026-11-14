#!/usr/bin/env python3
"""Regenerate the rendered results page and the claim-to-evidence index.

Inputs (all inside the pack):
  - claims.json                 (claim list, single source of truth)
  - results/run_log.txt         (unedited harness output; last 40 lines
                                  are embedded verbatim in the page)
  - results/digest_check_output.txt (embedded verbatim in the page)
  - results/env.txt             (environment details)
  - PINNED_COMMIT               (pinned postfiatd commit)

Outputs:
  - docs/index.html             (rendered results page)
  - claim-evidence-index.md     (claim-to-evidence index, same data)

Deterministic: no timestamps, no random data. Re-running this script on
unchanged inputs produces byte-identical outputs, so a fresh-copy run
leaves the working tree clean.
"""
import html
import json
import os
import re
import sys

PACK = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(PACK, "claims.json")) as f:
    claims_data = json.load(f)
claims = claims_data["claims"]

with open(os.path.join(PACK, "PINNED_COMMIT")) as f:
    pinned_commit = f.read().strip()

with open(os.path.join(PACK, "results", "run_log.txt")) as f:
    run_log_lines = f.read().splitlines()
log_tail = run_log_lines[-40:]

with open(os.path.join(PACK, "results", "digest_check_output.txt")) as f:
    digest_output = f.read()

with open(os.path.join(PACK, "results", "env.txt")) as f:
    env_text = f.read()

# Parse per-check summary lines from the run log.
summaries = {}
total_pass = total_fail = 0
for line in run_log_lines:
    m = re.match(r"^([A-Z-]+): (\d+) passed, (\d+) failed$", line)
    if m:
        summaries[m.group(1)] = (int(m.group(2)), int(m.group(3)))
        total_pass += int(m.group(2))
        total_fail += int(m.group(3))

digest_ok = all(line.rstrip().endswith(": OK") for line in
                digest_output.splitlines() if line.strip())
digest_files = sum(1 for line in digest_output.splitlines() if line.strip())

measured = [c for c in claims if c["type"] == "MEASURED"]
derived = [c for c in claims if c["type"] == "SOURCE-DERIVED"]


def esc(s):
    return html.escape(s)


def rows_html(cs):
    out = []
    for c in cs:
        out.append("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            esc(c["id"]), esc(c["claim"]), esc(c["evidence"])))
    return "\n".join(out)


summary_rows = "".join(
    "<tr><td>%s</td><td>%d</td><td>%d</td></tr>" % (esc(k), v[0], v[1])
    for k, v in sorted(summaries.items()))

page = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>PFTL Governance Audit Framework — Results</title>
<style>
body { font-family: system-ui, sans-serif; max-width: 960px; margin: 2em auto; padding: 0 1em; color: #1a1a1a; }
h1, h2 { color: #0b3d66; }
table { border-collapse: collapse; width: 100%%; margin: 1em 0; }
th, td { border: 1px solid #bbb; padding: 6px 8px; text-align: left; vertical-align: top; }
th { background: #e8f0f7; }
pre { background: #f4f4f4; padding: 1em; overflow-x: auto; font-size: 0.85em; }
.pass { color: #0a7a0a; font-weight: bold; }
.fail { color: #b00000; font-weight: bold; }
code { background: #f0f0f0; padding: 0 3px; }
</style>
</head>
<body>
<h1>PFTL Governance Audit Framework — Results</h1>
<p>Read-only audit harness for PFTL governance rules, run against synthetic
local fixtures. The harness never touches the network and never mutates the
pinned postfiatd tree. Vote replay and reordered validations are out of
scope for this pack.</p>
<h2>Pinned sources</h2>
<ul>
<li>Pinned postfiatd commit: <code>%s</code></li>
<li>Upstream comparison: rippled 2.5.0, commit <code>%s</code></li>
</ul>
<h2>Summary</h2>
<p>Total checks: <strong>%d passed, %d failed</strong> —
<span class="%s">%s</span></p>
<table>
<tr><th>Check group</th><th>Passed</th><th>Failed</th></tr>
%s
</table>
<p>Digest verification: <strong>%s</strong> (%d files checked, see below).</p>
<h2>Environment</h2>
<pre>%s</pre>
<h2>Measured claims (backed by a runnable check and raw output)</h2>
<table>
<tr><th>ID</th><th>Claim</th><th>Evidence</th></tr>
%s
</table>
<h2>Source-derived claims (backed by an exact file:line citation)</h2>
<table>
<tr><th>ID</th><th>Claim</th><th>Evidence</th></tr>
%s
</table>
<h2>Run log (last 40 lines, unedited)</h2>
<pre>%s</pre>
<p>Full unedited log: <code>results/run_log.txt</code></p>
<h2>Digest verification output (unedited)</h2>
<pre>%s</pre>
<h2>Reproduction</h2>
<p>From a fresh copy of this pack, run <code>bash run_all.sh</code>. The exact
commands, exit status, and any limitations are recorded in
<code>results/reproduction_log.txt</code>.</p>
<h2>Limitations</h2>
<ul>
<li>Fixtures are synthetic JSON built from the real schema shapes; the
harness checks the rules as transcribed from the cited source lines, it
does not compile or execute postfiatd (a full build is not feasible on
this machine).</li>
<li>Publisher-list signatures in the fixtures are synthetic
sha256 stand-ins that exercise the verify-then-apply rule, not real
ed25519 signatures.</li>
<li>Upstream comparison covers AmendmentTable.cpp, ValidatorList.cpp, and
SystemParameters.h. The upstream sparse checkout used here does not
contain src/xrpld/app/tx or the xrpl include tree, so no upstream diff is
claimed for the fee/sequence code.</li>
</ul>
</body>
</html>
""" % (
    esc(pinned_commit),
    esc(claims_data["upstream_commit"]),
    total_pass, total_fail,
    "pass" if total_fail == 0 else "fail",
    "ALL CHECKS PASSED" if total_fail == 0 else "FAILURES PRESENT",
    summary_rows,
    "PASS" if digest_ok else "FAIL",
    digest_files,
    esc(env_text.rstrip("\n")),
    rows_html(measured),
    rows_html(derived),
    esc("\n".join(log_tail)),
    esc(digest_output.rstrip("\n")),
)

with open(os.path.join(PACK, "docs", "index.html"), "w") as f:
    f.write(page)

# --- claim-evidence-index.md (same data, markdown form) ---
lines = []
lines.append("# Claim-to-evidence index")
lines.append("")
lines.append("Pinned postfiatd commit: `%s`" % pinned_commit)
lines.append("")
lines.append("Upstream comparison: rippled 2.5.0, commit "
             "`%s`." % claims_data["upstream_commit"])
lines.append("")
lines.append("MEASURED claims are backed by a runnable check and raw output "
             "in `results/run_log.txt`. SOURCE-DERIVED claims are backed by "
             "an exact file:line citation in the pinned tree (or the "
             "upstream tree where stated).")
lines.append("")
lines.append("## Measured claims")
lines.append("")
lines.append("| ID | Claim | Evidence |")
lines.append("|----|-------|----------|")
for c in measured:
    lines.append("| %s | %s | %s |" % (c["id"], c["claim"], c["evidence"]))
lines.append("")
lines.append("## Source-derived claims")
lines.append("")
lines.append("| ID | Claim | Evidence |")
lines.append("|----|-------|----------|")
for c in derived:
    lines.append("| %s | %s | %s |" % (c["id"], c["claim"], c["evidence"]))
lines.append("")

with open(os.path.join(PACK, "claim-evidence-index.md"), "w") as f:
    f.write("\n".join(lines))

print("build_derived: wrote docs/index.html and claim-evidence-index.md "
      "(%d measured, %d source-derived claims; %d passed, %d failed)" % (
          len(measured), len(derived), total_pass, total_fail))
