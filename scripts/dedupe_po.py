"""Remove duplicate msgid entries from locale/sr/LC_MESSAGES/django.po.

Windows gettext tooling (msgmerge/msgfmt) fails hard when duplicates exist.
We keep the first occurrence of each (msgctxt, msgid, msgid_plural) key and
drop later duplicates.
"""

from __future__ import annotations

from pathlib import Path

import polib

ROOT = Path(__file__).resolve().parents[1]
PO_PATH = ROOT / "locale" / "sr" / "LC_MESSAGES" / "django.po"


def main() -> None:
    po = polib.pofile(str(PO_PATH))
    # Obsolete entries often carry old duplicates and can break msgmerge on Windows.
    po[:] = [e for e in po if not e.obsolete]
    seen: set[tuple[str, str, str]] = set()
    kept: list[polib.POEntry] = []
    dropped = 0

    for entry in po:
        ctx = entry.msgctxt or ""
        msgid = entry.msgid or ""
        plural = entry.msgid_plural or ""
        key = (ctx, msgid, plural)
        if not msgid:
            kept.append(entry)
            continue
        if key in seen:
            dropped += 1
            continue
        seen.add(key)
        kept.append(entry)

    po[:] = kept
    po.save(str(PO_PATH))
    print(f"Deduped {PO_PATH}: dropped {dropped} duplicates, kept {len(kept)} entries")


if __name__ == "__main__":
    main()

