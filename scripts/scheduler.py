"""Budget-aware scheduling logic for the usage guard — pure + unit-testable.

See ``DESIGN.md``. These functions hold the *decisions* (does pending work fit the
remaining allotment? when do we resume?) with **no I/O**: the guard supplies the usage
samples / declared estimate and acts on the returned verdict. Keeping this pure means the
land/resume behavior can be tested without touching the live account or the hook.

Decisions locked with the owner:
- Q1 fit estimate: **hybrid** — a session's *declared* remaining-work estimate if present,
  else a **burn-rate projection** (utilization-per-second from recent samples).
- Q2 binding window: the **worst** (highest-utilization) window; resume at its reset + grace.
"""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Sample:
    """One usage observation: wall-clock ``t`` (epoch seconds) + worst-window ``util`` (%)."""

    t: float
    util: float


def burn_rate(samples: list[Sample]) -> float | None:
    """Rising utilization rate in **percent per second** from oldest→newest sample.

    Returns ``None`` when it can't be projected: fewer than two samples, a non-positive
    time span, or a flat/falling trend (only a *rising* burn threatens the cap, so a
    downward trend is treated as "no projection" rather than a negative rate).
    """
    pts = [s for s in samples if isinstance(s.util, (int, float))]
    if len(pts) < 2:
        return None
    first, last = pts[0], pts[-1]
    dt = last.t - first.t
    if dt <= 0:
        return None
    rate = (last.util - first.util) / dt
    return rate if rate > 0 else None


def seconds_to_stop(util: float, rate: float | None, stop: float) -> float | None:
    """Seconds until ``util`` reaches ``stop`` at ``rate`` (%/s). ``None`` if not projectable.

    Already at/over ``stop`` returns ``0.0`` (no headroom).
    """
    if rate is None or rate <= 0:
        return None
    if util >= stop:
        return 0.0
    return (stop - util) / rate


def decide(
    headroom_s: float | None,
    work_eta_s: float | None = None,
    *,
    margin: float = 0.8,
    floor_s: float = 300.0,
) -> str:
    """Return ``"continue"`` or ``"land"`` — the core budget verdict.

    - ``headroom_s``: seconds until STOP from the burn projection (``seconds_to_stop``);
      ``None`` when utilization isn't rising / can't be projected.
    - ``work_eta_s``: the session's **declared** remaining-work seconds, or ``None``.

    Logic (the Q1 hybrid):
    - No headroom projection → **continue** (the hook's hard STOP still backstops the wall).
    - Declared work ETA present → **land** only if the work won't finish within
      ``headroom_s * margin`` (safety margin leaves slack to checkpoint).
    - No declared ETA → **land** once headroom falls below ``floor_s`` (a conservative
      floor so we checkpoint before crowding the cap), else **continue**.
    """
    if headroom_s is None:
        return "continue"
    if work_eta_s is not None:
        return "continue" if work_eta_s <= headroom_s * margin else "land"
    return "land" if headroom_s < floor_s else "continue"


def resume_epoch(resets_at_epoch: float, grace_s: float = 60.0) -> float:
    """Resume slot = the binding window's reset **+ grace** (default 60s past reset)."""
    return resets_at_epoch + grace_s


# --------------------------------------------------------------------------- #
# Adaptive STOP buffer — data-calibrate the safety margin from observed overshoot.
#
# The gap between STOP and the true 100% cap exists to absorb *overshoot*: how far util
# climbs between one read and the next (poll lag + bursty spend). Instead of a hand-picked
# 5%, learn that buffer from the observed per-read rises and set
#   effective_stop = 100 - overshoot_quantile - safety   (clamped to a hard ceiling/floor).
# It self-tunes toward the data but structurally CANNOT chase the cap (the ceiling caps it),
# so it can never trade the catastrophic hard-limit trip for a few extra minutes.
# --------------------------------------------------------------------------- #
def overshoot_deltas(samples: list[Sample]) -> list[float]:
    """Positive per-read utilization rises (%) — how far util climbed between consecutive reads."""
    pts = [s for s in samples if isinstance(s.util, (int, float))]
    out: list[float] = []
    for a, b in zip(pts, pts[1:]):
        d = b.util - a.util
        if d > 0:
            out.append(d)
    return out


def quantile(xs: list[float], q: float) -> float | None:
    """Linear-interpolated ``q``-quantile (q in [0,1]) of ``xs``; ``None`` if empty."""
    if not xs:
        return None
    s = sorted(xs)
    if len(s) == 1:
        return s[0]
    pos = q * (len(s) - 1)
    lo = int(pos)
    frac = pos - lo
    return s[lo] + (s[lo + 1] - s[lo]) * frac if lo + 1 < len(s) else s[lo]


def adaptive_stop(
    overshoot: float | None,
    *,
    ceiling: float = 98.0,
    floor: float = 90.0,
    safety: float = 1.0,
    default: float = 95.0,
) -> float:
    """Effective STOP threshold from the observed ``overshoot`` buffer.

    ``100 - overshoot - safety``, clamped to ``[floor, ceiling]``. On cold start (no overshoot
    data) returns ``default`` (the classic fixed STOP). The **ceiling is a hard cap** — the
    adaptive value can never exceed it, so the learner cannot creep toward the true limit.
    """
    if overshoot is None:
        return max(floor, min(ceiling, default))
    est = 100.0 - overshoot - safety
    return max(floor, min(ceiling, est))


# --------------------------------------------------------------------------- #
# Q3 resume mechanism — self-contained `at` job → `claude --continue` (pure builders)
# --------------------------------------------------------------------------- #
def resume_command(tmux_target: str, prompt: str = "") -> list[str]:
    """Argv that nudges a paused session's tmux window to resume the SAME conversation.

    Sends ``claude --continue`` (optionally with a steering ``prompt``) as keystrokes into
    ``tmux_target`` (``session:window`` or ``%pane``). Argv form → no shell interpolation.
    """
    line = "claude --continue" + (f" {prompt}" if prompt else "")
    return ["tmux", "send-keys", "-t", tmux_target, line, "Enter"]


def at_timestamp(epoch_s: float) -> str:
    """Local-time stamp for ``at -t`` (``CCYYMMDDhhmm.ss``) from an epoch second."""
    return time.strftime("%Y%m%d%H%M.%S", time.localtime(epoch_s))


def at_schedule_argv(epoch_s: float) -> list[str]:
    """Argv to schedule a job at ``epoch_s`` via ``at`` (the job body is fed on stdin).

    Usage: ``subprocess.run(at_schedule_argv(slot), input=script, text=True)``.
    """
    return ["at", "-t", at_timestamp(epoch_s)]


def systemd_calendar(epoch_s: float) -> str:
    """systemd ``OnCalendar`` stamp ``YYYY-MM-DD HH:MM:SS`` (local) from an epoch second."""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(epoch_s))


def systemd_run_argv(epoch_s: float, unit: str, resume_argv: list[str]) -> list[str]:
    """Argv for a transient **user** timer that runs ``resume_argv`` at ``epoch_s``.

    Uses ``systemd-run --user --on-calendar=…`` — no sudo, no ``at``/``atd`` needed.
    """
    return [
        "systemd-run", "--user", "--quiet",
        f"--on-calendar={systemd_calendar(epoch_s)}", f"--unit={unit}", "--",
        *resume_argv,
    ]


def unit_name(session: str, prefix: str = "carterm-resume-") -> str:
    """A systemd-safe unit name for a session's resume timer."""
    safe = "".join(c if (c.isalnum() or c in "_.-") else "_" for c in session)
    return prefix + (safe or "session")
