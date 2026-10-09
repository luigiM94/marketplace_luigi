# bitrock-skills — marketplace di skills per Claude Code

Marketplace per condividere skill di Claude Code. Ogni skill è un plugin autonomo.

## Skill disponibili

<!-- PLUGINS:START -->
| Skill | Versione | Descrizione | Documentazione |
|---|---|---|---|
| `example-skill` | 1.0.0 | Skill di esempio: mostra come è strutturata una skill nel marketplace | [README](plugins/example-skill/README.md) |
<!-- PLUGINS:END -->

## Struttura

```
.claude-plugin/marketplace.json   # catalogo dei plugin
plugins/<skill>/
  .claude-plugin/plugin.json      # manifest del plugin
  skills/<skill>/SKILL.md         # la skill (+ eventuali file di supporto)
  README.md                       # documentazione del plugin (generata)
  CHANGELOG.md                    # storico versioni (generato)
scripts/add-skill.py              # strumento di caricamento e documentazione
CLAUDE.md                         # regole per chi modifica il repo
```

## Caricare una skill

1. Prepara una cartella con un `SKILL.md` valido:

   ```markdown
   ---
   name: my-skill
   description: Cosa fa la skill e quando usarla.
   ---

   Istruzioni per Claude...
   ```

   `name` deve essere kebab-case; `description` è ciò che Claude legge per decidere quando attivarla.

2. Caricala nel marketplace, con la versione e una nota per il changelog:

   ```bash
   python3 scripts/add-skill.py /percorso/my-skill --version 1.0.0 --note "Prima versione"
   ```

   Per aggiornare una skill esistente usa `--force`, alza la versione e descrivi la modifica con `--note`.

3. Lo script aggiorna in automatico la documentazione: `CHANGELOG.md` del plugin, il suo `README.md` e la tabella sopra. Non modificarle a mano.

4. Pubblica:

   ```bash
   git add . && git commit -m "Add skill my-skill" && git push
   ```

Per rigenerare solo la documentazione: `python3 scripts/add-skill.py --sync-docs`.

## Installare le skill da questo marketplace

Dentro Claude Code:

```
/plugin marketplace add luigiM94/marketplace_luigi
/plugin install example-skill@bitrock-skills
```

## Test in locale

```
/plugin marketplace add /Users/luigimazzarella/Formazione/corso_claude/marketplace_luigi
/plugin install example-skill@bitrock-skills
```
