"""
FusionGuardNet – System Logs Data Source
Reads/simulates system log events and translates them into LogSignal objects
for the Fusion Layer.
"""

import re
import random
import time
import logging
from typing import List, Dict, Any

from app.ml.fusion_layer import LogSignal

logger = logging.getLogger(__name__)

# Common log patterns (simplified)
_FAILED_LOGIN_RE   = re.compile(r"(Failed password|authentication failure|Invalid user)", re.I)
_SUCCESS_LOGIN_RE  = re.compile(r"(Accepted password|session opened for user)", re.I)
_PRIV_ESC_RE       = re.compile(r"(sudo:|su\[|NOPASSWD|privilege escalation)", re.I)
_PROCESS_RE        = re.compile(r"(nmap|masscan|sqlmap|hydra|metasploit|msfconsole)", re.I)


def parse_log_line(line: str) -> Dict[str, Any]:
    """Extract structured fields from a raw log line."""
    return {
        "raw":               line,
        "is_failed_login":   bool(_FAILED_LOGIN_RE.search(line)),
        "is_success_login":  bool(_SUCCESS_LOGIN_RE.search(line)),
        "is_priv_esc":       bool(_PRIV_ESC_RE.search(line)),
        "is_unusual_process":bool(_PROCESS_RE.search(line)),
        "timestamp":         time.time(),
    }


def aggregate_to_signal(log_lines: List[str]) -> LogSignal:
    """Aggregate a list of raw log lines into a LogSignal."""
    parsed = [parse_log_line(l) for l in log_lines]
    return LogSignal(
        failed_logins         = sum(1 for p in parsed if p["is_failed_login"]),
        successful_logins     = sum(1 for p in parsed if p["is_success_login"]),
        privilege_escalations = sum(1 for p in parsed if p["is_priv_esc"]),
        unusual_process_count = sum(1 for p in parsed if p["is_unusual_process"]),
        error_rate            = sum(1 for p in parsed if p["is_failed_login"]) / max(len(parsed), 1),
    )


def simulate_logs(n: int = 20, inject_attack: bool = False) -> List[str]:
    """Generate synthetic log lines for testing."""
    rng   = random.Random()
    users = ["alice", "bob", "root", "admin", "ubuntu"]
    ips   = [f"192.168.1.{rng.randint(2, 254)}" for _ in range(5)]
    lines = []

    for _ in range(n):
        user = rng.choice(users)
        ip   = rng.choice(ips)
        ts   = time.strftime("%b %d %H:%M:%S")

        if inject_attack and rng.random() < 0.4:
            lines.append(f"{ts} sshd[1234]: Failed password for {user} from {ip} port 22 ssh2")
        else:
            lines.append(
                rng.choice([
                    f"{ts} sshd[1234]: Accepted password for {user} from {ip} port 22 ssh2",
                    f"{ts} systemd[1]: Started Session {rng.randint(1,99)} of user {user}.",
                    f"{ts} sudo:    {user} : TTY=pts/0 ; USER=root ; COMMAND=/usr/bin/ls",
                    f"{ts} kernel: Connection from {ip}:22",
                ])
            )

    return lines
