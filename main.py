#!/usr/bin/env python3
"""Write one original office-life joke to /output/entry.txt.

Pure stdlib. Deterministic: the same bytes on every run.
The write is atomic (temp file + rename) so a reader never sees
a half-written entry, the output is world-readable (0644), and the
program re-reads its own output to verify the exact bytes landed.
"""

import os
import stat
import tempfile

JOKE = "My boss says 'per my last email' so often, HR lists it as my emergency contact."

OUT_PATH = "/output/entry.txt"


def build_entry() -> str:
    """Return the exact entry text: one line, 1-200 characters."""
    text = JOKE.strip()
    assert 1 <= len(text) <= 200, "joke must be 1-200 characters"
    assert "\n" not in text and "\r" not in text, "joke must be a single line"
    assert text == text.strip(), "joke must not be only whitespace"
    return text


def write_entry(payload: bytes) -> None:
    """Atomically write payload to OUT_PATH with mode 0644."""
    out_dir = os.path.dirname(OUT_PATH)
    os.makedirs(out_dir, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(payload)
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, OUT_PATH)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
    os.chmod(OUT_PATH, 0o644)


def verify_output(payload: bytes) -> None:
    """Re-read the output and confirm it is exactly what we wrote."""
    with open(OUT_PATH, "rb") as f:
        actual = f.read()
    assert actual == payload, "output bytes do not match the entry"
    mode = stat.S_IMODE(os.stat(OUT_PATH).st_mode)
    assert mode == 0o644, "output file must be mode 0644, got %o" % mode


def main() -> None:
    text = build_entry()
    payload = (text + "\n").encode("utf-8")
    write_entry(payload)
    verify_output(payload)


if __name__ == "__main__":
    main()
