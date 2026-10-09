# Regole per questo repo

## Documentazione delle skill

Ogni modifica a un plugin in `plugins/` deve aggiornare anche la sua documentazione, nello stesso passaggio:

- Carica le modifiche con `python3 scripts/add-skill.py <cartella> --version X.Y.Z --note "..." --force`. Lo script aggiorna `plugins/<name>/CHANGELOG.md`, `plugins/<name>/README.md` e la tabella in `README.md`.
- Alza la versione a ogni modifica di una skill, e scrivi una nota che descriva cosa è cambiato.
- Non modificare a mano `CHANGELOG.md`, `README.md` del plugin o la tabella tra i marker `PLUGINS` del `README.md` principale: vengono rigenerati dallo script.
- Se modifichi solo lo script o la documentazione generale (`README.md` fuori dalla tabella, questo file), non serve un nuovo changelog di plugin, ma va comunque aggiornato il `README.md` principale se cambia il modo di usare il marketplace.
- Se cambi `scripts/add-skill.py`, esegui `python3 scripts/add-skill.py --sync-docs` e verifica che la documentazione sia coerente.

## Modifica di una skill

La sorgente va tenuta fuori da `plugins/`: lo script rifiuta di caricare una skill dalla sua stessa copia nel marketplace. Modifica la cartella di lavoro della skill, poi ricaricala.
