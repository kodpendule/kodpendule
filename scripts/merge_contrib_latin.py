"""Merge Latin translations for django.contrib.auth (and other admin labels) into django.po."""
from __future__ import annotations

from pathlib import Path

import polib

ROOT = Path(__file__).resolve().parents[1]
PROJECT_PO = ROOT / "locale/sr/LC_MESSAGES/django.po"

AUTH_LATIN: dict[str, str] = {
    "group": "grupa",
    "groups": "grupe",
    "Group": "Grupa",
    "Groups": "Grupe",
    "Add group": "Dodaj grupu",
    "permission": "dozvola",
    "permissions": "dozvole",
    "Authentication and Authorization": "Autentifikacija i autorizacija",
    "Authentication and authorization": "Autentifikacija i autorizacija",
    "Personal info": "Lični podaci",
    "Important dates": "Važni datumi",
    "username": "korisničko ime",
    "password": "lozinka",
    "last login": "poslednja prijava",
    "first name": "ime",
    "last name": "prezime",
    "staff status": "status osoblja",
    "superuser status": "status superkorisnika",
    "user permissions": "korisničke dozvole",
    "Logged out": "Odjavljen",
}


def main() -> None:
    proj = polib.pofile(str(PROJECT_PO))
    by_msgid = {e.msgid: e for e in proj if not e.obsolete and e.msgid}
    merged = 0
    for msgid, latin in AUTH_LATIN.items():
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
    print(f"Merged {merged} contrib auth strings")


if __name__ == "__main__":
    main()
