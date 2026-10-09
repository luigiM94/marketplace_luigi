#!/usr/bin/env python3
"""Gestisce il marketplace di skills.

Uso:
    python3 scripts/add-skill.py <cartella-skill> [--version X.Y.Z] [--note "..."] [--force]
    python3 scripts/add-skill.py --sync-docs

Ogni caricamento aggiorna SEMPRE la documentazione:
  - plugins/<name>/CHANGELOG.md  (nuova voce con versione e data)
  - plugins/<name>/README.md     (descrizione, versione, installazione)
  - README.md                    (tabella delle skill, tra i marker PLUGINS)

--sync-docs rigenera la documentazione senza caricare nulla.
"""

import argparse
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
README = ROOT / "README.md"
PLUGINS = ROOT / "plugins"
AUTHOR = {"name": "Luigi Mazzarella", "email": "luigi.mazzarella@bitrock.it"}
START, END = "<!-- PLUGINS:START -->", "<!-- PLUGINS:END -->"


def read_frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        sys.exit(f"Errore: {skill_md} non ha un frontmatter YAML (--- ... ---)")
    fields = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def load_catalog() -> dict:
    return json.loads(MARKETPLACE.read_text(encoding="utf-8"))


def save_catalog(catalog: dict) -> None:
    MARKETPLACE.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def record_changelog(name: str, version: str, note: str) -> None:
    """Aggiunge in cima al CHANGELOG del plugin una nuova voce datata."""
    path = PLUGINS / name / "CHANGELOG.md"
    if path.exists():
        text = path.read_text(encoding="utf-8")
    else:
        text = f"# Changelog — {name}\n"
    head, sep, rest = text.partition("\n## ")
    old_sections = ("## " + rest) if sep else ""
    entry = f"## {version} — {date.today().isoformat()}\n\n- {note}\n"
    path.write_text(f"{head.rstrip()}\n\n{entry}\n{old_sections}".rstrip() + "\n", encoding="utf-8")


def write_plugin_readme(entry: dict, marketplace: str) -> None:
    name = entry["name"]
    text = f"""# {name}

{entry["description"]}

**Versione:** {entry["version"]}
**Installazione:** `/plugin install {name}@{marketplace}`

## Uso

La skill si attiva automaticamente quando la richiesta corrisponde alla sua descrizione.
Il contenuto completo è in [`skills/{name}/SKILL.md`](skills/{name}/SKILL.md).

## Changelog

Vedi [CHANGELOG.md](CHANGELOG.md).
"""
    (PLUGINS / name / "README.md").write_text(text, encoding="utf-8")


def write_root_readme(catalog: dict) -> None:
    rows = ["| Skill | Versione | Descrizione | Documentazione |", "|---|---|---|---|"]
    for e in catalog["plugins"]:
        rows.append(
            f"| `{e['name']}` | {e['version']} | {e['description']} | [README](plugins/{e['name']}/README.md) |"
        )
    table = "\n".join(rows) if catalog["plugins"] else "_Nessuna skill caricata._"
    block = f"{START}\n{table}\n{END}"
    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        sys.exit(f"Errore: marker {START} / {END} mancanti in README.md")
    new = re.sub(re.escape(START) + ".*?" + re.escape(END), lambda _: block, text, flags=re.DOTALL)
    README.write_text(new, encoding="utf-8")


def sync_docs(catalog: dict) -> None:
    """Rigenera tutta la documentazione dal catalogo."""
    for entry in catalog["plugins"]:
        name = entry["name"]
        if not (PLUGINS / name / "skills" / name / "SKILL.md").is_file():
            sys.exit(f"Errore: '{name}' è nel catalogo ma plugins/{name}/skills/{name}/SKILL.md non esiste. Rimuovi la voce da marketplace.json.")
        if not (PLUGINS / name / "CHANGELOG.md").exists():
            record_changelog(name, entry["version"], "Prima versione nel marketplace.")
        write_plugin_readme(entry, catalog["name"])
    write_root_readme(catalog)


def main() -> None:
    parser = argparse.ArgumentParser(description="Gestisce il marketplace di skills")
    parser.add_argument("skill_dir", type=Path, nargs="?", help="Cartella della skill (con SKILL.md)")
    parser.add_argument("--version", default="1.0.0", help="Versione del plugin (default 1.0.0)")
    parser.add_argument("--note", help="Descrizione della modifica per il changelog")
    parser.add_argument("--force", action="store_true", help="Sovrascrive una skill già presente")
    parser.add_argument("--sync-docs", action="store_true", help="Rigenera solo la documentazione")
    args = parser.parse_args()

    if args.sync_docs:
        sync_docs(load_catalog())
        print("Documentazione rigenerata.")
        return

    if args.skill_dir is None:
        parser.error("indica la cartella della skill, oppure usa --sync-docs")

    src = args.skill_dir.resolve()
    skill_md = src / "SKILL.md"
    if not skill_md.is_file():
        sys.exit(f"Errore: SKILL.md non trovato in {src}")

    meta = read_frontmatter(skill_md)
    name = meta.get("name")
    description = meta.get("description")
    if not name or not description:
        sys.exit("Errore: il frontmatter deve contenere 'name' e 'description'")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
        sys.exit(f"Errore: il nome '{name}' deve essere kebab-case (es. my-skill)")

    plugin_dir = PLUGINS / name
    target_skill = plugin_dir / "skills" / name
    if plugin_dir.exists() and not args.force:
        sys.exit(f"Errore: '{name}' esiste già. Usa --force per sovrascrivere.")
    if src == target_skill.resolve():
        sys.exit("Errore: la sorgente è già la copia nel marketplace; modifica la skill in una cartella esterna.")

    # 1. copia la skill
    if target_skill.exists():
        shutil.rmtree(target_skill)
    shutil.copytree(src, target_skill)

    # 2. plugin.json
    manifest_dir = plugin_dir / ".claude-plugin"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    plugin_json = {
        "name": name,
        "description": description,
        "version": args.version,
        "author": AUTHOR,
    }
    (manifest_dir / "plugin.json").write_text(
        json.dumps(plugin_json, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # 3. catalogo
    catalog = load_catalog()
    entry = {
        "name": name,
        "source": f"./plugins/{name}",
        "description": description,
        "version": args.version,
    }
    plugins = catalog.setdefault("plugins", [])
    for i, existing in enumerate(plugins):
        if existing["name"] == name:
            plugins[i] = entry
            break
    else:
        plugins.append(entry)
    save_catalog(catalog)

    # 4. documentazione (sempre)
    note = args.note or f"Versione {args.version}: aggiornamento della skill."
    record_changelog(name, args.version, note)
    sync_docs(catalog)

    print(f"Skill '{name}' v{args.version} caricata in plugins/{name}")
    print("Documentazione aggiornata: CHANGELOG.md, README del plugin, README.md principale.")
    print("Ricorda: git add, commit e push per renderla disponibile agli altri.")


if __name__ == "__main__":
    main()
