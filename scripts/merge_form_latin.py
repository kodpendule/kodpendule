"""Ensure Django form validation strings use Serbian Latin in django.po."""

from __future__ import annotations

from pathlib import Path

import polib

ROOT = Path(__file__).resolve().parents[1]
PROJECT_PO = ROOT / "locale/sr/LC_MESSAGES/django.po"

# Overrides Django's built-in sr (Cyrillic) fallbacks when project .mo lacks an entry.
FORM_LATIN: dict[str, str] = {
    "This field is required.": "Ovo polje je obavezno.",
    "Enter a valid email address.": "Unesite ispravnu email adresu.",
    "Enter a valid URL.": "Unesite ispravan URL.",
    "Enter a whole number.": "Unesite ceo broj.",
    "Enter a valid date.": "Unesite ispravan datum.",
    "Enter a valid time.": "Unesite ispravno vreme.",
    "Enter a valid date/time.": "Unesite ispravan datum i vreme.",
    "Enter a valid UUID.": "Unesite ispravan UUID.",
    "Enter a valid JSON.": "Unesite ispravan JSON.",
    "Enter a valid integer.": "Unesite ispravan ceo broj.",
    "Enter a valid decimal number.": "Unesite ispravan decimalni broj.",
    "Enter a valid value.": "Unesite ispravnu vrednost.",
}


def main() -> None:
    proj = polib.pofile(str(PROJECT_PO))
    by_msgid = {e.msgid: e for e in proj if not e.obsolete and e.msgid}
    merged = 0
    for msgid, latin in FORM_LATIN.items():
        if msgid in by_msgid:
            entry = by_msgid[msgid]
        else:
            entry = polib.POEntry(msgid=msgid, msgstr=latin)
            proj.append(entry)
            by_msgid[msgid] = entry
        entry.msgstr = latin
        if "fuzzy" in entry.flags:
            entry.flags.remove("fuzzy")
        merged += 1
    proj.save(str(PROJECT_PO))
    proj.save_as_mofile(str(PROJECT_PO.with_suffix(".mo")))
    print(f"Merged {merged} form validation strings into {PROJECT_PO}")


if __name__ == "__main__":
    main()
