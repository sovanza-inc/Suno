# Running Claude Code Continuously for Self-Enhancing Systems

**Claude Code can run for days on a personal Mac or PC through a careful combination of process management, autonomy configurations, and safety guardrails.** The key insight from 2025-2026 real-world deployments is that successful multi-day autonomous operation requires defense-in-depth: container isolation, state checkpointing, cost monitoring, and explicit verification hooks. Below is a comprehensive analysis of options and tradeoffs.

## 1. Process Persistence Options

### Terminal Multiplexers: tmux, screen, zellij

**tmux** is the 2026 industry standard for keeping processes alive across disconnects. It uses a client-server architecture where the server holds your session while clients attach and detach freely. Sessions survive SSH disconnects, laptop lid closures, and terminal crashes. Commands: `tmux new -s claude-agent`, detach with `Ctrl+b d`, reattach with `tmux attach`. Memory footprint is negligible (~12MB) and CPU usage under 1% when idle.

**Zellij** is a modern Rust-based alternative with built-in keybinding hints and session resurrection (survives crashes and restores layouts). It's more intuitive for beginners but 8x slower rendering than tmux when handling 100+ panes. Good for local development; tmux wins for SSH/production.

**screen** is legacy—only use when tmux is unavailable.

**Tradeoff**: tmux/zellij are reliable and proven, but they only keep the process *alive*—they don't handle crashes, rate limits, or auth expiration. Complexity is medium (requires learning key bindings).

### nohup and disown

**nohup** starts a process immune to terminal hangup signals: `nohup claude -p "task" > output.log 2>&1 &`. **disown** removes an already-running background job from the shell's job table. Both are one-liners but offer no reattachment, no status checking, and no automatic restart. Output must be explicitly redirected or it fills `nohup.out`.

**Tradeoff**: Very low complexity, adequate for one-off tasks, but unsuitable for mission-critical multi-day agents. No observability or recovery mechanism.

### System Service Managers: launchd, systemd, NSSM

**macOS launchd** (user services) runs processes as system-managed daemons. Create a `.plist` file in `~/Library/LaunchAgents/` with `KeepAlive` set to true, load with `launchctl load`, and the OS will auto-restart on crash and run at boot. XML configuration is verbose but highly reliable.

**Linux systemd** (user services) is the equivalent for Linux. Place a `.service` file in `~/.config/systemd/user/`, enable with `systemctl --user enable myapp.service`, and it runs on login with configurable restart policies (`Restart=on-failure`, `RestartSec=10s`). Integrated logging via `journalctl`.

**Windows NSSM** (Non-Sucking Service Manager) wraps any executable as a Windows service: `nssm install MyService "C:\...\node.exe" "app.js"`. GUI or CLI configuration, auto-restart, runs before login, survives reboots.

**Tradeoff**: These are the gold standard for production reliability—automatic restarts, survives reboots, monitored by OS. Complexity is medium (XML/ini files, service commands). Best for true production workloads on personal machines.

### pm2 Process Manager

**pm2** is a Node.js process manager that works for *any* process type (not just Node). Commands: `pm2 start app.js`, `pm2 start "python3 script.py" --interpreter none`, `pm2 startup` (generates boot script). Features include cluster mode, log rotation (`pm2 install pm2-logrotate`), memory-limit auto-restart (`--max-memory-restart 500M`), and rich CLI (`pm2 logs`, `pm2 status`).

**Tradeoff**: Low complexity, excellent for Node.js, good for others. ~30MB memory overhead. Primarily designed for Node; systemd/launchd are better for system-level services.

### Claude Code Non-Interactive Mode for Long-Running Tasks

Claude Code's **`-p` or `--print` flag** enables headless mode: `claude -p "Find and fix the bug in auth.py"`. Pipe stdin, redirect output, compose with Unix tools. Add **`--bare`** to skip auto-discovery (no hooks, skills, MCP servers) for consistent CI/scripts. Supports `--output-format json` for structured results.

**Critical distinction**: Interactive mode keeps a REPL loop; headless mode runs task then exits. For multi-day loops, you need a *wrapper* that repeatedly calls `claude -p` or use the SDK.

**Tradeoff**: Headless mode is scriptable and composable but exits after each task. For continuous loops, prefer SDK orchestration or a master script that invokes Claude Code repeatedly.

### Claude Agent SDK for Programmatic Orchestration

The **Claude Agent SDK** (Python/TypeScript) launches Claude Code as a subprocess and provides remote control. Install: `pip install claude-agent-sdk`. Features include streaming, custom tools, hooks (PreToolUse, PostToolUse), permission control, session management (`continue`, `resume`, `fork`), and cost tracking. It's the cleanest path for a *programmatic long-running orchestration* where your Python/TS script manages the agent loop.

**Tradeoff**: Highest flexibility and control for complex self-enhancing systems. Requires coding your own orchestration layer. Best for multi-agent systems or when you need custom logic between agent turns.

---

## 2. Preventing Machine Sleep and Shutdown

### macOS caffeinate

**caffeinate** prevents Mac sleep while a process runs. Usage: `caffeinate -i claude ...` prevents idle sleep during the command, `caffeinate -t 28800` prevents sleep for 8 hours, `caffeinate -dims` prevents display+idle+disk sleep. Common pattern: `caffeinate -i python3 orchestrator.py`.

**Permanent disable** (not recommended): `sudo pmset -a disablesleep 1` but this defeats energy-saving features.

### Windows powercfg

**powercfg** controls Windows power settings. Disable standby on AC: `powercfg -change -standby-timeout-ac 0`. Configure lid-close behavior: `powercfg -setacvalueindex SCHEME_CURRENT SUB_BUTTONS LIDACTION 0` (0=nothing, 1=sleep, 2=hibernate, 3=shutdown). Or use GUI: Control Panel → Power Options.

### Linux Power Management

Varies by desktop environment. GNOME: Settings → Power → Automatic suspend. For systemd-managed systems, edit `/etc/systemd/logind.conf` with `HandleLidSwitch=ignore` then `systemctl restart systemd-logind`.

### Tradeoffs: Heat, Battery, Electricity, Wear

Running a laptop 24/7 generates **heat** (80-95°C sustained = shortened lifespan, thermal throttling degrades performance). **Battery** degrades rapidly with continuous AC + heat (60% capacity loss per year typical). **Electricity**: laptops draw 45-65W (~$3-5/month), desktops 150-300W (~$15-30/month). **Wear**: fans designed for intermittent use last 2-3 years under 24/7 operation vs 5+ with breaks.

**Recommendation**: Elevate laptop for airflow, clean vents regularly, consider external cooling pad. For true multi-day production workloads, desktops or cloud VMs are more appropriate—laptops are not designed for server duty.

---

## 3. Autonomy and Safety Modes

### Permission Modes in Claude Code

Claude Code offers **six permission modes** controlling oversight vs autonomy:

**1. default**: Reads only without prompts; all writes/commands require approval. Safest for interactive development.

**2. acceptEdits**: Auto-approves file edits, reads, and common filesystem commands (mkdir, touch, rm, rmdir, mv, cp, sed). Still prompts for protected paths (`.git`, `.env`, shell configs). Good middle ground for coding-only auto-approval.

**3. plan**: Research and propose changes without making them. Claude reads files and writes plans but doesn't edit source. Approval options when plan is ready. Useful for exploratory work before committing to changes.

**4. auto** (Research Preview): Fully autonomous with background classifier reviews. Requires Claude Sonnet 4.6/Opus 4.6 and Anthropic API. Blocks data exfiltration, sensitive operations, production deploys by default; allows local file operations, dependency installs, read-only HTTP. Classifier pauses after 3 consecutive denials or 20 total. This is **the recommended autonomous mode** with built-in safety checks.

**5. dontAsk**: Auto-denies everything except pre-approved tools in `permissions.allow` rules. Fully non-interactive for CI/scripts.

**6. bypassPermissions** (dangerously-skip-permissions / "yolo mode"): **Disables ALL permission prompts and safety checks.** Circuit breaker still blocks `rm -rf /` and `rm -rf ~`, and refuses to run as root. **Official warning: only use in isolated containers/VMs without internet access.** Offers no protection against prompt injection or unintended actions.

**Switching modes**: Use `Shift+Tab` during session or `--permission-mode <mode>` at startup. Set default in `.claude/settings.json`.

**Tradeoff matrix**:

| Mode | Autonomy | Safety | Best For |
|------|----------|--------|----------|
| default | Low | High | Interactive development |
| acceptEdits | Medium | High | Code-only auto-approval |
| auto | High | Medium | Classifier-reviewed autonomy |
| bypassPermissions | Highest | **None** | Container-only, trusted code |

**Critical guidance**: `auto` mode is best for unattended multi-day runs with safety. `bypassPermissions` should *never* run directly on your host machine—use Docker containers.

### Running in Sandboxes: Docker, DevContainer

**Docker isolation** provides hard boundaries between Claude Code and host systems. Anthropic publishes an **official DevContainer reference** with firewall rules (`init-firewall.sh`) that allowlists only trusted domains (api.anthropic.com, registry.npmjs.org, github.com, pypi.org) and blocks everything else. Security config: `security_opt: [no-new-privileges:true]`, `cap_drop: [ALL]`, run as non-root user.

**Real incident**: One developer lost 7GB of files when Claude ran `rm -rf` on host (GitHub issue #46058). Container isolation prevents this blast radius entirely.

**DevContainer pattern**: Mount workspace as read-write but keep `~/.claude` persistent across rebuilds for auth. Use `/etc/claude-code/managed-settings.json` for org-wide policy enforcement. Disable auto-updater (`DISABLE_AUTOUPDATER=1`) and pin Claude Code version in Dockerfile for reproducibility.

**Tradeoff**: Docker adds complexity (Dockerfile, docker-compose.yml, network configuration) but dramatically reduces risk. For autonomous multi-day operation with `bypassPermissions`, containers are **mandatory**—not optional.

### Hooks for Guardrails: PreToolUse, PostToolUse, Stop

**PreToolUse hooks** intercept tool calls *before* execution. Exit codes: 0=allow, 2=**block** (feeds error to Claude), other=warning. Example: block destructive patterns like `rm -rf`, `git reset --hard`, `DROP TABLE`, `git push -f`. Typical execution time <10μs for quick-reject tier, full regex only on dangerous keywords.

**PostToolUse hooks** react *after* successful execution. Cannot undo but can trigger fixes. Example: auto-format with Prettier after every Edit/Write, run linter, update learning files.

**Stop hooks** enforce verification before loop exit. Example: check test results, confirm completion promise in output. Prevents premature exits where agent *thinks* work is done but tests still fail.

**Real-world impact** (6-month study): Accidental destructive commands went from 2-3/month to 0, manual formatting runs from 5-10/session to 0, .env edits caught in review from ~1/week to 0.

**Tradeoff**: Hooks add deterministic enforcement (unlike probabilistic LLM reasoning) but require scripting (bash, Python, etc.). 60-second default timeout may need adjustment for LLM/agent hooks.

### Risks of Fully Autonomous Unattended Operation

**Data loss**: `rm -rf` on workspace, git history erasure, lock file corruption from concurrent edits. Mitigation: PreToolUse hooks, git checkpoints, container isolation.

**Data exfiltration**: Prompt injection from malicious files, "helpful" credential leaks, tool abuse (curl to attacker endpoints). Mitigation: Network firewall, never mount `~/.ssh` or cloud credentials into containers, short-lived repository-scoped tokens.

**Runaway costs**: Documented incidents include $47,000 in 11 days (LangChain retry loop), $87,000 in 1 month (35 engineers, untagged API calls), 127,000 API calls in 8 hours (automation loop). **10 concurrent agents can generate $30,000 overnight** with Opus 4 at 100K loops. Mitigation: Gateway-level budgets (MLflow AI Gateway, RelayPlane), per-session token caps, application-level turn limits, real-time Slack alerts.

**Destructive commands**: Beyond `rm -rf`, includes `git checkout -- .` (discarding uncommitted work), database operations, credential exfiltration. Mitigation: Multi-layer detection (quick reject → context classification → full pattern match), AST-based analysis for inline scripts.

---

## 4. Long-Running Task Patterns for Self-Enhancing Loops

### Continuous Loop with Master Prompt

The **recursive agent loop** is the core pattern. Architecture: normalization → inference → tool detection → execution → recursion. The loop continues until the model returns no tool calls (natural stopping point). Async generator pattern enables streaming and composability.

Key insight: Recursion creates systems with no fixed "end" state. Default behavior is "continue until resolved" rather than "respond once and stop."

### Agent-in-a-Loop: Planner → Executor → Critic

**Real-world test**: Wilson Lin built a web browser from scratch (FastRender project) with close to a week of autonomous running, producing 1 million+ lines across 1,000 files. Architecture: planners and sub-planners create tasks, workers execute, judge agent decides completion. Hierarchical task decomposition with verification at each level.

**Pattern**: Multiple agents with specialized roles. Planner defines work, executor implements, critic validates. Prevents premature exits and ensures quality.

### Thread-Based Framework (ClaudeFast)

Six thread types for scaling autonomous work:

- **Base (L-thread)**: Single feature, one file, minutes duration
- **P-threads**: 5 independent features in parallel, hours duration  
- **C-threads**: Phased migrations, hours duration
- **F-threads**: Architecture decisions with multiple agent opinions
- **B-threads**: Multi-file refactors with sub-tasks, days duration
- **Z-threads**: Zero-touch autonomous product systems, continuous

**Economics**: Running agents costs ~$10.42 USD/hour with Sonnet. Teams report 120 agent-hours/day output with 5 parallel agents at $50/hour vs human at $100/hour for 8 hours/day. Constraint isn't cost—it's "how much reliable work can you define?"

### Using Subagents for Parallelism

Claude Code spawns autonomous worker agents via the **Task tool** that run in parallel with separate context windows. Invocation: "Use subagents to simultaneously investigate these 5 frameworks in parallel." Execution modes: foreground (parent waits) or background (independent notification).

**Agent dashboard** (`claude agents` command as of v2.1.139+) shows all background sessions, dispatch new sessions by typing prompts, peek at progress, attach when needed. Sessions survive terminal closure via supervisor process. Pinned sessions (Ctrl+T) stay alive when idle.

**Best practices**: Limit to 3-5 concurrent subagents (sweet spot), define clear scope, request synthesis at end. Don't use for sequential work or trivial tasks. Costs multiply: agent teams use ~7× tokens vs single agent.

### Queue/Todo File Pattern

External progress file for recovery:

```markdown
## Progress: User Dashboard

### Completed
- [x] Set up test infrastructure
- [x] Implement metrics API endpoint

### In Progress  
- [ ] Implement activity feed

### Remaining
- [ ] Add export functionality
- [ ] Performance optimization
```

Agent updates this file as it works. If context fills and agent restarts, it reads progress file and continues. Survives compaction and crashes.

### Checkpointing and Resumption

**Session management**: `--continue` or `-c` resumes most recent session in current directory. `--resume` or `-r` resumes specific session by name/ID. Storage: `~/.claude/projects/<project>/<session-id>.jsonl`. Sessions restore full conversation history, tool results, entire cognitive state—not just chat history.

**File checkpointing** (SDK feature): Tracks modifications through Write/Edit tools (not Bash commands). Captures checkpoint UUID with each user message. Rewind files: `await client.rewind_files(checkpoint_id)`. Restores files on disk but NOT conversation history.

**Interactive checkpointing**: Press `Esc` twice or `/rewind` to open checkpoint menu. Choose to restore code only, conversation only, or both. "Git for your agent's reasoning process."

**Critical limitation**: Checkpointing is *manual* in CLI or *explicit* in SDK. No automatic state snapshots. State loss on crash is common.

### Context Window Management

**Specs**: Default 200K tokens, extended 1M for Sonnet 4.6/Opus 4.6. Manual commands: `/clear` wipes entirely, `/compact [instructions]` summarizes while preserving key state, `/context` shows token breakdown. Auto-compaction triggers at 64-75% capacity.

**Best practice**: Don't wait for auto-compact; run `/compact` proactively at ~60% capacity. Context rot symptoms appear around 30-60 minute mark: retrieval failures, contradictory decisions, lost file structure, "Lost in the Middle" syndrome where the agent forgets decisions made 30 minutes ago.

**Context engineering is the moat**: Progressive 5-level compression pipeline enables sessions that run for hours instead of minutes. Levels: tool result budgeting → history snipping → microcompact (dual-path cache-aware) → context collapse (reversible) → autocompact (last resort, irreversible).

**Subagents for context isolation**: Delegate verbose operations (tests, logs) to subagents. Output stays in subagent context, only summary returns. Typical cost reduction: 60-70% for log processing.

### The "Self-Improving" Pattern: Editing CLAUDE.md, Skills, Commands

**Breakthrough pattern**: CLAUDE.md that teaches Claude *how to write rules*, not just what rules to follow. Meta-rules for self-teaching:

```markdown
## META - MAINTAINING THIS DOCUMENT

### Writing Effective Guidelines
1. Use absolute directives - Start with "NEVER" or "ALWAYS"
2. Lead with why - Explain the problem before the solution (1-3 bullets max)
3. Be concrete - Include actual commands/code
4. Minimize examples - One clear point per code block
5. Bullets over paragraphs
```

**The magic prompt**: "Reflect on this mistake. Abstract and generalize the learning. Write it to CLAUDE.md."

Every mistake becomes permanent learning with minimal human effort. Quality compounds as document grows because meta-rules ensure self-regulation.

**Custom slash commands** in `.claude/commands/update-learnings.md`: Trigger with `/update-learnings` to automatically extract new learnings from session and append to structured file.

**Warning**: CLAUDE.md bloat is a failure mode. Models reliably follow ~150-200 distinct instructions; Claude Code's system prompt already uses ~50 slots. A 400-bullet unsorted file is worse than no file. Keep under 200 lines / 2,000 tokens. Consolidate weekly.

---

## 5. Cost and Rate-Limit Management

### Claude Code Pro vs Max Plan Limits

**Pro Plan** ($20/month, $17/month annual): ~45 prompts per 5-hour rolling window. Shared usage bucket across claude.ai and Claude Code. Weekly usage cap introduced August 28, 2025.

**Max 5x Plan** ($100/month): 5× Pro capacity, ~50-200 prompts per 5-hour window. Two-tier weekly limits: one for all models, one Sonnet-specific. Can purchase additional usage at API rates after hitting limits.

**Max 20x Plan** ($200/month): 20× Pro capacity, ~200-800 prompts per 5-hour window. Same two-tier weekly structure.

**Critical structure**: 5-hour rolling window starts with first prompt, resets after 5 hours of inactivity. Usage shared across ALL Claude surfaces (web, desktop, mobile, Claude Code)—no separate Claude Code allocation.

**Heavy user benchmark**: 10B tokens over 8 months = $15,000 API vs $800 Max plan (93% savings). Max 20x provides best value for heavy development.

### API Billing vs Subscription

**API pay-as-you-go pricing** (per million tokens):
- Claude Sonnet 4.6: $3/M input, $15/M output
- Claude Opus 4.7/4.6: $5/M input, $25/M output  
- Claude Haiku 4.5: $1/M input, $5/M output
- Cache reads: 90% savings ($0.30/M vs $3/M for Sonnet)
- Batch API: 50% discount

**Real-world costs**: Average $13/developer/active day, enterprise $150-250/developer/month, 90th percentile under $30/active day.

**Critical warning**: If `ANTHROPIC_API_KEY` environment variable is set, Claude Code ALWAYS uses API billing, even if you have a subscription. Check your shell profile before long runs.

### Rate Limits by Tier

**API rate limits** (Messages API, Tier 1 after $5 spend):
- Sonnet 4.6: 50 RPM | 500,000 ITPM | 100,000 OTPM
- Opus: 5 RPM | 20,000 ITPM | 4,000 OTPM

Higher tiers (2-4) unlock with cumulative spend ($40, $200, $400). Tier 4: Sonnet 400 RPM | 4M ITPM | 800K OTPM.

**Cache-aware ITPM** (key advantage): Only *uncached* input tokens count toward ITPM limits. `cache_read_input_tokens` do NOT count (except Haiku 3.5). With 80% cache hit rate, 2M ITPM limit = 10M effective throughput.

**Token bucket algorithm**: Capacity continuously replenished, not reset at fixed intervals. Can burst up to limit, then sustained rate limits apply.

### Rate Limit Behavior for Long Autonomous Runs

**429 errors** include `retry-after` header (seconds to wait). Best practice: Exponential backoff with jitter (2s → 4s → 8s → 16s → 32s, max 3-5 retries, add random 0-1000ms). Three-tier wait calculation: retry-after header (highest priority) → reset-header math → jittered exponential fallback.

**Proactive throttling**: Track `anthropic-ratelimit-tokens-remaining` from response headers. When remaining ≤ 10%, preemptively sleep until reset. Avoid hitting 429 entirely for smooth autonomous operation.

**Circuit breaker pattern**: After N consecutive failures (e.g., 5), suspend requests temporarily. Prevents retry storms during extended outages.

### Monitoring Spend and Usage

**Built-in**: `/usage` command shows total cost, duration, code changes (estimates only). **Authoritative**: Claude Console at platform.claude.com/usage with real-time rate limit charts, cache hit rate, hourly maximums, per-workspace tracking.

**Usage & Cost Admin API**: Track token consumption by model, workspace, tier with 1m/1h/1d buckets. Data appears within 5 minutes of request completion.

**Third-party**: LiteLLM (open-source, track by API key), Portkey (multi-cloud routing, observability), CloudZero (FinOps-grade cost tracking).

**Alert thresholds** (recommended):
- Token usage >80% of limit
- 3+ consecutive 401 errors (auth failing)  
- Rate limit utilization >90%
- Daily cost threshold exceeded
- Session runtime >4 hours (OAuth expiry risk)

---

## 6. Observability and Intervention

### Logging stdout/stderr to Files

Basic pattern: `claude -p "task" > output.log 2>&1 &` with nohup. For system services (launchd/systemd), configure `StandardOutPath` and `StandardErrorPath` in service definition.

**pm2**: Built-in log management with `pm2 logs`, `pm2 flush`. Install `pm2-logrotate` for automatic rotation: `pm2 set pm2-logrotate:max_size 10M`, `pm2 set pm2-logrotate:retain 7`.

**Compression tools**: ContextZip compresses command output by 90% before it reaches context window. Filters framework noise (node_modules stack frames, ANSI codes, spinners) while preserving signal (error messages, security warnings, test failures). Reduces 30-line stack traces to 3-line essentials.

### Watching Progress Remotely

**SSH + tmux pattern**: Start tmux session on remote server (`tmux new -s claude-code`), detach (Ctrl+B, D), reattach later from any device (`tmux attach -t claude-code`). Sessions survive SSH disconnects. Multiple engineers can attach to same session.

**Safety layer**: Run in Docker container to limit damage from skip-permissions mode.

**Agent dashboard**: `claude agents` command (v2.1.139+) shows all background sessions, dispatch new sessions, peek at progress without interrupting, attach to full conversation when needed. Accepts flags like `--permission-mode`, `--model`, `--dangerously-skip-permissions` to set defaults for dispatched sessions.

**Tailscale/ngrok**: For true remote access across networks, not just local SSH.

### Notifications: Slack, Discord, Email

**Pattern**: Use PostToolUse hooks or standalone monitoring scripts to send alerts on key events. Example: Slack webhook on test failures, cost threshold breaches, repeated 401 errors, verification failures.

**File-based signaling** with Monitor tool: Background processes signal completion via flag files (`touch .build-complete`), Claude Code monitors filesystem events (`monitor .build-complete --timeout 300`). No polling required.

**MCP integrations**: Connect Claude Code to Slack/Discord via MCP servers for two-way communication—agent can post updates and receive intervention commands.

### Knowing When to Step In vs Let It Run

**Intervention signals**:
- **Context rot** (30-60 minute mark): Retrieval failures, contradictory decisions, re-reading files  
- **Loop detection**: 3 identical actions (by hash), 95%+ semantic similarity between consecutive states
- **Cost velocity**: $15 in 10 minutes, 127K API calls in 8 hours
- **Auth failures**: Repeated 401 errors (OAuth expiring)
- **Verification failures**: Tests failing repeatedly, stop hook blocking exit

**Let it run signals**:
- Progress file updating regularly
- Token usage within limits
- Verification passing (tests green, screenshots validated)
- Cost accumulation within budget
- Context under 60% capacity

**Hands-off duration**: Plan for human checkpoints every 4 hours (under OAuth expiry window). For true multi-day unattended operation, use API keys (don't expire) instead of OAuth.

---

## 7. Failure Modes and Recovery

### Rate Limit Errors (429)

**What happens**: Claude Code hits RPM/ITPM/OTPM ceiling. Response includes `retry-after` header with seconds to wait. Token bucket refills continuously so resumption is smooth after waiting.

**Recovery**: Read `retry-after` header, sleep for specified duration plus jitter (random 0-1000ms to prevent thundering herd), resume exactly where left off. After 5 failures, check status.claude.com for system-wide outage.

### Authentication Expiration (401)

**Critical failure mode**: OAuth tokens expire mid-session (1-4 hour typical TTL). Active session cannot reload token after `/login` in same process—stuck in 401 loop, loses all context, autonomous task halts with work incomplete.

**Documented issues**: GitHub #15007, #12447, #17123, #36911 report OAuth expiration disrupting workflows multiple times per day.

**Solution**: Use **API keys** instead of OAuth for any run >4 hours. Set `export ANTHROPIC_API_KEY=sk-ant-...` and Claude Code will use API billing (does not expire unless manually revoked). Alternative: `claude setup-token` creates 1-year OAuth token (better than /login but still not as reliable as API key).

**Recovery**: If OAuth session dies, context is lost—must start fresh. If API key: verify key validity, rotate if needed.

### Server Errors (500, 503, 504)

**What happens**: Transient server errors, bad gateway, service unavailable, gateway timeout. Typically resolve in minutes.

**Recovery**: Retry with exponential backoff (2s → 4s → 8s), max 3-5 attempts. After 5 failures, circuit breaker suspends for 5 minutes then health check. Non-retriable—check status page.

### Detecting Agent Stuck in Loop

**Three root causes**: Context blindness (error logs truncated), validation hallucination (agent "verifies" fix with silently failing command), goal ambiguity (vague "done" criteria).

**Detection patterns**:
- **Action repetition hashing**: SHA-256 hash of tool_name + sorted params. Track occurrences; 3 identical = loop.
- **Semantic similarity**: Compute similarity between consecutive loop states. If >95% similar, trigger boredom detection.
- **Time-per-step tracking**: Steps significantly longer than average = stuck in sub-loop.
- **Sub-goal completion rate**: Dropping below threshold = systematic loop problem.

**Real incident**: 50% of n8n agent runs stuck repeatedly triggering tools. Fixed by debounce hook + clear SUCCESS states.

### Detecting Destructive Operations

**Multi-layer approach**:
1. **Quick reject** (<10μs): SIMD-accelerated keyword scan for `rm -rf`, `git reset --hard`, `DROP TABLE`, `git push -f`, `sudo`
2. **Context classification**: Mark command spans as Executed vs Data vs InlineCode, only run regex on executable spans
3. **Full pattern match**: Comprehensive regex with safe patterns allowlist (e.g., `rm -rf /tmp/*` is safe)
4. **Heredoc/inline script detection**: AST-based analysis catches `python -c "os.remove(...)"` and `bash -c` embedded commands

**Implementation**: PreToolUse hook with exit code 2 to block, exit code 0 to allow.

### Auto-Restart Strategies

**For systemd/launchd**: Configure `Restart=on-failure` with `RestartSec=10s`. Process automatically restarts on crash.

**For pm2**: Built-in auto-restart on crash. Add memory threshold: `--max-memory-restart 500M`.

**For custom wrappers**: Shell loop with SIGHUP handling:
```bash
while true; do
  claude "$@"
  [[ $? -eq 129 ]] && continue  # SIGHUP restart
  break
done
```

**Safety caveat**: Auto-restart without state validation can perpetuate corruption loops. Always validate state before resume.

### Crash Recovery and State Persistence

**Current limitation**: Claude Code does NOT persist full conversation state mid-session. If process crashes, context is lost. Session files in `~/.claude/projects/` contain metadata but not full history.

**Third-party solutions**:
- **tapes**: Proxy-based black box recording. Captures all Claude Code traffic in local SQLite database. Survives Claude Code crashes independently. Manual recovery: query database, feed context back.
- **claude-mem**: Multi-layer recovery with persistent message queue (claim-confirm pattern), self-healing iterators, startup session restoration from DB.
- **Autonomous loop pattern**: Persistent JSON state machine (`.claude/autonomous-loop.json`) with re-anchoring protocol at every iteration. Knows exactly where it left off after crash.

**Best practices**:
- Externalize state regularly—git commits, structured files, not just conversation memory
- Break multi-day tasks into <4-hour segments (under OAuth expiry)
- Use `/rename` before major context switches for session organization
- Manually save progress summaries to CLAUDE.md or project files

---

## 8. Hardware and Practical Concerns

### Thermal Throttling on Laptops

**Problem**: CPU/GPU reduce clock speed when temps hit 90-100°C. Performance drops significantly (can hit 0.38 GHz in extreme cases). Common in thin laptops with inadequate cooling. Continuous operation reveals design flaws.

**Mitigation**: Elevate laptop for airflow, clean vents/fans regularly (dust = 30% efficiency loss), repaste thermal compound (3-5°C improvement), use cooling pad with active fans, balanced power profile instead of "Max Performance," laptop stand + external keyboard/mouse for better ventilation.

**Reality check**: Laptops are NOT designed for 24/7 server duty. If possible, use desktop hardware for multi-day tasks or cloud VM for true production workloads.

### Memory Leaks and Node.js Process Bloat

**Problem**: Long-running Node.js processes accumulate leaked references—global variables never freed, event listeners not removed, closures holding large objects, cache objects growing unbounded.

**Detection**: Monitor heap usage programmatically: `process.memoryUsage()`. Use Chrome DevTools (`chrome://inspect`) for heap snapshots, heapdump package for programmatic snapshots, Clinic.js for performance profiling.

**Prevention**: Remove event listeners (`removeListener()`), clear intervals/timeouts, nullify large objects when done, use WeakMap/WeakSet for caches, set memory limit restarts (`pm2 start app.js --max-memory-restart 500M`).

**Expectation**: Even well-written apps show 5-10% memory growth over days. Plan restarts every 7-14 days.

### Disk Space Concerns

**Log files** are primary culprit. Set up log rotation: Linux `logrotate`, pm2 `pm2-logrotate` with max_size 10M and retain 7 days. Monitor: `df -h`, `du -sh /var/log/*`.

**Git history**: Don't run production services inside git repos, or use git clean and shallow clones.

**Artifacts**: Schedule cleanup for temp files, build outputs: `find /tmp -mtime +7 -delete`.

### Network Reliability

**Strategies**: Connection pooling (databases, HTTP clients), exponential backoff on retries, circuit breakers (prevent cascade failures), health checks (TCP keepalive, application-level pings), monitoring with alerts on sustained connection failures.

**Example**: Retry with exponential backoff in async function, max 3 retries, sleep 2^attempt × 1000ms between attempts.

---

## 9. Recommended High-Level Architectures

### Architecture 1: Production Autonomous System (Docker + API Key + Hooks)

**Best for**: Multi-day unattended operation, trusted repositories, maximum safety

**Components**:
1. **Docker container** with official DevContainer config + firewall (`init-firewall.sh` allowlisting trusted domains)
2. **API key authentication** (not OAuth) to avoid 1-4 hour expiration
3. **`auto` permission mode** with classifier-based safety (or `acceptEdits` if auto not available)
4. **Three-hook baseline**:
   - PreToolUse: Block destructive Bash patterns
   - PreToolUse: Protect sensitive files (`.env`, `.git`, credentials)
   - PostToolUse: Auto-format on every write
5. **Stop hook** enforcing test verification before loop exit
6. **External checkpoint file** (progress.md) updated regularly
7. **systemd/launchd service** for auto-restart on crash
8. **Cost monitoring** with gateway-level budgets (MLflow AI Gateway) and Slack alerts

**Reliability**: Excellent (90%+ incident prevention based on real-world data)  
**Safety**: High (container isolation + classifier + hooks)  
**Cost**: Medium ($10-50/day depending on workload)  
**Complexity**: High (Docker, firewall, hooks, service config)  
**Observability**: Good (logs, agent dashboard, remote tmux attach)

**Tradeoffs**: Setup complexity is substantial but provides defense-in-depth. Requires DevOps knowledge (Docker, networking). Best ROI for teams or high-value autonomous projects.

---

### Architecture 2: Pragmatic Loop (tmux + API Key + Checkpointing)

**Best for**: Personal projects, iterative development, moderate autonomy needs

**Components**:
1. **tmux session** for persistence across disconnects (`tmux new -s claude-loop`)
2. **API key authentication** for multi-hour runs without OAuth expiry
3. **`acceptEdits` permission mode** (middle-ground autonomy)
4. **caffeinate** (Mac) or **powercfg** (Windows) to prevent sleep
5. **Custom wrapper script** that loops `claude -p` with task queue:
   ```bash
   while read -r task; do
     claude -p "$task" >> loop.log 2>&1
     sleep 60  # Rate limit breather
   done < tasks.txt
   ```
6. **Manual checkpointing** with `/compact` every 60% context utilization
7. **Learnings file** (LEARNINGS.md) updated with `/update-learnings` slash command
8. **pm2** for auto-restart: `pm2 start orchestrator.sh --interpreter bash`

**Reliability**: Good (tmux + pm2 handles most failures, manual intervention for auth/context issues)  
**Safety**: Medium (acceptEdits blocks most dangerous ops, no container isolation)  
**Cost**: Low-Medium ($5-20/day typical)  
**Complexity**: Low-Medium (bash script, pm2 commands, tmux basics)  
**Observability**: Moderate (log files, tmux attach, pm2 status)

**Tradeoffs**: Simpler setup than Architecture 1 but less safety. Requires periodic human checkpoints (every 4-8 hours). Good for trusted codebases on personal machine. Risk of data loss without container isolation—**backup workspace before starting**.

---

### Architecture 3: SDK Orchestration (Programmatic Long-Running Agent)

**Best for**: Custom self-enhancing systems, multi-agent orchestration, research

**Components**:
1. **Python/TypeScript orchestrator** using Claude Agent SDK
2. **Programmatic loop** with phases: plan → execute → verify → consolidate → recurse
3. **API key authentication** in SDK options
4. **Custom hooks** (PreToolUse, PostToolUse) defined in code
5. **Explicit state machine** in JSON file (`.claude/state.json`) with re-anchoring
6. **Subagent spawning** for parallel work (3-5 concurrent max)
7. **Cost tracking** built into SDK with session budget cap
8. **systemd/launchd service** running Python orchestrator
9. **Slack integration** for notifications on key events (verification failure, budget threshold)

**Example skeleton**:
```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def self_enhancing_loop():
    state = load_state()
    while not state['complete']:
        async for message in query(
            prompt=f"Continue from phase: {state['phase']}",
            options=ClaudeAgentOptions(
                permission_mode="auto",
                allowed_tools=["Bash", "Read", "Write", "Edit"],
                enable_file_checkpointing=True,
            )
        ):
            if message.type == 'result':
                state = update_state(message)
                save_state(state)
                if should_consolidate(state):
                    await consolidate_learnings()
        await asyncio.sleep(60)  # Rate limit breather

asyncio.run(self_enhancing_loop())
```

**Reliability**: Excellent (explicit state management, programmatic error handling)  
**Safety**: High (custom hooks, budget caps, explicit verification)  
**Cost**: Medium-High ($20-100/day for complex multi-agent systems)  
**Complexity**: High (requires coding orchestration layer, SDK knowledge)  
**Observability**: Excellent (full programmatic control, custom logging, metrics export)

**Tradeoffs**: Maximum flexibility and control but requires software engineering. Best for teams building custom agentic systems or researchers exploring self-enhancement patterns. Steep learning curve but highest ceiling for sophistication.

---

## Key Implementation Principles Across All Architectures

**1. API Keys, Not OAuth**: OAuth expires in 1-4 hours and kills sessions. API keys don't expire. This is the **single most critical decision** for multi-day runs.

**2. Container Isolation for bypassPermissions**: If using `--dangerously-skip-permissions`, Docker containers are mandatory. Real incidents show 7GB data loss when this runs on host.

**3. External State Checkpointing**: Don't rely on conversation memory. Write progress to files, git commits, structured logs. Context compaction and crashes lose memory.

**4. Test-Driven Verification**: Objective pass/fail criteria (tests, screenshots, metrics) prevent loops and premature exits. Subjective "done" doesn't work.

**5. Proactive Context Management**: Intervene at 60% utilization, use `/compact` with instructions, delegate verbose work to subagents. Context rot is predictable—prevent it.

**6. Cost Monitoring with Hard Caps**: Gateway-level budgets (not just provider monthly caps). Real-time alerting. $3,000 in single session is documented; $30,000 overnight with 10 agents is realistic.

**7. Defense-in-Depth Safety**: Every documented destructive incident occurred when 2+ safety layers failed simultaneously. Single-layer protection is insufficient. Combine: container + classifier/hooks + external monitoring + cost caps.

**8. Meta-Rules for Self-Enhancement**: CLAUDE.md that teaches *how to write rules*, not just rules to follow. Quality compounds. Bloat degrades—consolidate weekly.

**9. Sub-Agent Parallelism**: 3-5 concurrent agents is sweet spot. Beyond that, coordination overhead exceeds gains. 7× token cost for agent teams—use judiciously.

**10. Human Checkpoints Every 4-8 Hours**: OAuth expiry, context rot, verification gaps, cost accumulation all benefit from periodic review. True zero-touch is aspirational; pragmatic systems plan human touchpoints.

---

## Conclusion

Running Claude Code continuously for days on a personal Mac or PC for self-enhancing systems is **technically feasible and increasingly common** in 2025-2026. Real-world deployments at Stripe, Ramp, Wiz, and individual practitioners running 5+ parallel agents daily demonstrate viability. The technology matured significantly with Auto mode (March 2026), native checkpointing, and SDK enhancements.

**Success requires layered reliability**: process persistence (tmux, systemd, pm2) prevents disconnects; API key auth prevents OAuth deaths; Docker isolation prevents data loss; PreToolUse hooks prevent destructive commands; stop hooks prevent premature exits; cost caps prevent runaway spend; external checkpoints enable crash recovery.

**The real constraint isn't technical capability—it's defining reliable work**. Thread-based frameworks (base → parallel → chained → fusion → big → zero-touch) show the progression from manual to fully autonomous. Enterprises are shipping 10,000-line migrations in 4 days (previously 10 engineer-weeks) and delivering features in 5 days instead of 24.

**For practitioners starting out**: Begin with Architecture 2 (pragmatic loop with tmux + API key + acceptEdits mode) for personal projects with manual checkpoints. Advance to Architecture 1 (Docker + auto mode + hooks) when ready to run unattended overnight. Reserve Architecture 3 (SDK orchestration) for custom multi-agent systems or research. All three are production-viable; choose based on safety requirements and engineering capacity.

The self-enhancing capability—where Claude Code edits its own CLAUDE.md, skills, and slash commands—transforms static tool usage into compounding knowledge systems. Every mistake becomes permanent learning. The key insight: teach the agent *how to teach itself* through meta-rules, not just what to do. That's the breakthrough enabling true autonomous improvement over multi-day runs.