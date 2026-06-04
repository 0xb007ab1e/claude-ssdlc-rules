#!/usr/bin/env python3
"""Locate and copy the claude.ai ``sessionKey`` cookie from a local browser.

Finds the claude.ai ``sessionKey`` in your installed browsers and writes it to
``~/.claude/.claude_session_key`` (mode 0600, git-ignored) so ``claude_usage.py``
can use it. Supports:

  * Firefox family (Firefox, ESR, LibreWolf) - cookies are plaintext SQLite.
  * Chromium family (Chrome, Chromium, Brave, Edge, Vivaldi) - cookie values are
    encrypted; this decrypts the Linux ``v10``/``v11`` AES-128-CBC scheme.
      - ``v10`` uses the fixed password ``peanuts`` (no keyring needed).
      - ``v11`` uses the "<Browser> Safe Storage" secret from the OS keyring,
        read via the ``secretstorage`` Python lib or the ``secret-tool`` CLI.

The cookie database is copied to a temp file before reading, so it works even
while the browser is running (the live DB is locked).

Decryption uses the ``cryptography`` package if importable, else falls back to
the ``openssl`` CLI - so no single dependency is mandatory.

By default the key value is **never printed**; it is written to the key file and
a redacted confirmation is shown. Use ``--stdout`` to print it (e.g. to pipe).

SECURITY: this reads an authentication secret from your own browser profile on
your own machine. Treat the output like a password. macOS/Windows Chromium
keyrings are not handled here (different crypto); use Firefox or set the key
manually there.

Exit codes: 0 = found & written, 1 = not found / error.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import os
import shutil
import sqlite3
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_OUT = Path.home() / ".claude" / ".claude_session_key"
DEFAULT_HOST = "claude.ai"
DEFAULT_COOKIE = "sessionKey"

HOME = Path.home()

# Each Chromium entry: display name, list of profile-Cookies path globs, and the
# keyring "safe storage" identifiers for the v11 path (label + secret-tool app).
CHROMIUM_BROWSERS = {
    "chrome": {
        "globs": [HOME / ".config/google-chrome/*/Cookies"],
        "label": "Chrome Safe Storage", "app": "chrome",
    },
    "chromium": {
        "globs": [HOME / ".config/chromium/*/Cookies"],
        "label": "Chromium Safe Storage", "app": "chromium",
    },
    "brave": {
        "globs": [HOME / ".config/BraveSoftware/Brave-Browser/*/Cookies"],
        "label": "Brave Safe Storage", "app": "brave",
    },
    "edge": {
        "globs": [HOME / ".config/microsoft-edge/*/Cookies"],
        "label": "Microsoft Edge Safe Storage", "app": "chromium",
    },
    "vivaldi": {
        "globs": [HOME / ".config/vivaldi/*/Cookies"],
        "label": "Vivaldi Safe Storage", "app": "vivaldi",
    },
}

FIREFOX_BROWSERS = {
    "firefox": {
        "globs": [
            HOME / ".mozilla/firefox/*/cookies.sqlite",
            HOME / ".var/app/org.mozilla.firefox/.mozilla/firefox/*/cookies.sqlite",
        ],
    },
    "librewolf": {
        "globs": [HOME / ".librewolf/*/cookies.sqlite"],
    },
}


class ExtractError(Exception):
    """A user-facing failure that should exit non-zero."""


def _copy_to_temp(path: str) -> str:
    """Copy a (possibly locked) SQLite DB to a temp file; return its path."""
    fd, tmp = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    shutil.copy2(path, tmp)
    return tmp


def _query_cookie(db: str, table: str, host_col: str, name_col: str,
                  val_col: str, host: str, cookie: str):
    """Return the cookie value column for the newest matching row, or None."""
    tmp = _copy_to_temp(db)
    try:
        con = sqlite3.connect(f"file:{tmp}?mode=ro", uri=True)
        try:
            rows = con.execute(
                f"SELECT {val_col} FROM {table} "
                f"WHERE {host_col} LIKE ? AND {name_col} = ?",
                (f"%{host}%", cookie),
            ).fetchall()
        finally:
            con.close()
        return rows[-1][0] if rows else None
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


# --------------------------------------------------------------------------- #
# Firefox (plaintext)
# --------------------------------------------------------------------------- #
def from_firefox(globs: list[Path], host: str, cookie: str) -> str | None:
    """Read a plaintext cookie value from any matching Firefox profile."""
    for pattern in globs:
        for db in sorted(glob.glob(str(pattern))):
            value = _query_cookie(db, "moz_cookies", "host", "name", "value", host, cookie)
            if value:
                return value if isinstance(value, str) else value.decode("utf-8", "strict")
    return None


# --------------------------------------------------------------------------- #
# Chromium (encrypted)
# --------------------------------------------------------------------------- #
def _aes_cbc_decrypt(key: bytes, iv: bytes, ciphertext: bytes) -> bytes:
    """AES-128-CBC decrypt via ``cryptography`` if available, else ``openssl``."""
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        dec = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
        return dec.update(ciphertext) + dec.finalize()
    except ImportError:
        pass
    if shutil.which("openssl"):
        proc = subprocess.run(
            ["openssl", "enc", "-d", "-aes-128-cbc", "-nopad",
             "-K", key.hex(), "-iv", iv.hex()],
            input=ciphertext, capture_output=True,
        )
        if proc.returncode != 0:
            raise ExtractError("openssl AES decrypt failed: " + proc.stderr.decode("utf-8", "ignore"))
        return proc.stdout
    raise ExtractError("No AES backend available (install the 'cryptography' pip package or 'openssl').")


def _keyring_password(label: str, app: str) -> bytes:
    """Fetch a Chromium 'Safe Storage' secret from the OS keyring (v11)."""
    # Preferred: the secretstorage Python lib (Secret Service / D-Bus).
    try:
        import secretstorage  # type: ignore
        conn = secretstorage.dbus_init()
        for coll in secretstorage.get_all_collections(conn):
            if coll.is_locked():
                continue
            for item in coll.get_all_items():
                if item.get_label() == label or item.get_attributes().get("application") == app:
                    return item.get_secret()
    except Exception:
        pass
    # Fallback: the secret-tool CLI.
    if shutil.which("secret-tool"):
        proc = subprocess.run(["secret-tool", "lookup", "application", app],
                              capture_output=True)
        if proc.returncode == 0 and proc.stdout:
            return proc.stdout.rstrip(b"\n")
    raise ExtractError(
        f"This cookie is keyring-encrypted (v11) and the '{label}' secret could "
        "not be read. Install the 'secretstorage' pip package or the "
        "'secret-tool' CLI, and ensure your keyring is unlocked."
    )


def _decrypt_chromium(encrypted: bytes, label: str, app: str) -> str:
    """Decrypt a Linux Chromium ``encrypted_value`` (v10/v11) into a string."""
    version = encrypted[:3]
    if version == b"v10":
        password = b"peanuts"
    elif version == b"v11":
        password = _keyring_password(label, app)
    else:
        raise ExtractError(f"Unsupported cookie encryption tag {version!r} "
                           "(macOS/Windows schemes are not handled).")
    key = hashlib.pbkdf2_hmac("sha1", password, b"saltysalt", 1, 16)
    plaintext = _aes_cbc_decrypt(key, b" " * 16, encrypted[3:])
    if plaintext:  # strip PKCS#7 padding
        plaintext = plaintext[: -plaintext[-1]]
    # Chromium >= M114 prepends a 32-byte SHA256 domain hash to the value.
    if not plaintext.startswith(b"sk-ant"):
        plaintext = plaintext[32:]
    return plaintext.decode("utf-8", "strict")


def from_chromium(globs: list[Path], label: str, app: str,
                  host: str, cookie: str) -> str | None:
    """Read and decrypt a cookie value from any matching Chromium profile."""
    for pattern in globs:
        for db in sorted(glob.glob(str(pattern))):
            encrypted = _query_cookie(db, "cookies", "host_key", "name",
                                      "encrypted_value", host, cookie)
            if encrypted:
                return _decrypt_chromium(encrypted, label, app)
    return None


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def locate(browser: str, host: str, cookie: str) -> tuple[str, str]:
    """Find the cookie. Returns ``(browser_name, value)``.

    ``browser`` is a specific name or ``"auto"`` to try all (Firefox first,
    then Chromium). Raises :class:`ExtractError` if nothing is found.
    """
    order: list[str]
    if browser == "auto":
        order = list(FIREFOX_BROWSERS) + list(CHROMIUM_BROWSERS)
    else:
        order = [browser]

    for name in order:
        if name in FIREFOX_BROWSERS:
            val = from_firefox(FIREFOX_BROWSERS[name]["globs"], host, cookie)
        elif name in CHROMIUM_BROWSERS:
            cfg = CHROMIUM_BROWSERS[name]
            val = from_chromium(cfg["globs"], cfg["label"], cfg["app"], host, cookie)
        else:
            raise ExtractError(f"Unknown browser '{name}'. Choices: auto, "
                               + ", ".join(list(FIREFOX_BROWSERS) + list(CHROMIUM_BROWSERS)))
        if val:
            return name, val
    raise ExtractError(
        f"Could not find the '{cookie}' cookie for {host} in any local browser. "
        "Make sure you are logged into claude.ai in a supported browser."
    )


def write_key(value: str, out_path: Path) -> None:
    """Write ``value`` to ``out_path`` with 0600 permissions."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(out_path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(value)
    os.chmod(str(out_path), 0o600)


def build_parser() -> argparse.ArgumentParser:
    """Construct the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Locate the claude.ai sessionKey in a local browser and copy it "
                    "to the git-ignored key file used by claude_usage.py.",
    )
    parser.add_argument("--browser", default="auto",
                        help="auto (default) or one of: "
                             + ", ".join(list(FIREFOX_BROWSERS) + list(CHROMIUM_BROWSERS)))
    parser.add_argument("--host", default=DEFAULT_HOST, help="cookie host (default claude.ai)")
    parser.add_argument("--cookie", default=DEFAULT_COOKIE, help="cookie name (default sessionKey)")
    parser.add_argument("--out", default=str(DEFAULT_OUT), type=Path,
                        help=f"destination key file (default {DEFAULT_OUT})")
    parser.add_argument("--stdout", action="store_true",
                        help="print the key value to stdout instead of writing the file "
                             "(use with care - the value is a credential)")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns a process exit code (0 found, 1 error)."""
    args = build_parser().parse_args(argv)
    try:
        browser, value = locate(args.browser, args.host, args.cookie)
    except ExtractError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.stdout:
        sys.stdout.write(value)
        if sys.stdout.isatty():
            sys.stdout.write("\n")
        return 0

    write_key(value, args.out)
    mode = oct(stat.S_IMODE(os.stat(args.out).st_mode))
    preview = value[:13] + "..." if len(value) > 13 else "(short)"
    print(f"found {args.cookie} in {browser}; wrote {args.out} (mode {mode}, "
          f"len {len(value)}, starts {preview})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
