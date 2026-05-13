# AggerPilot

> Auto-pilot for **AGGER GESTOR** — turns a folder of proposal PDFs on a VPS into fully-filled prospection records, hands-free.

AggerPilot is a Python automation that bridges three systems most sales teams still glue together by hand:

1. **A VPS** that receives proposal files (PDFs and images).
2. **A PostgreSQL database** that holds customer/seller records.
3. **AGGER GESTOR** — a Windows desktop ERP whose only public interface is its own UI.

The bot pulls the files, matches each one to a customer row, drives the AGGER window through `pywinauto`, fills in every field (item, status, seller, owner, notes, attachments), saves the record, and stamps `data_prospectada` back in the database. It logs every outcome and cleans up after itself.

---

## What it does, step by step

```
   VPS (SFTP)                  Local machine                       PostgreSQL
   ──────────                  ─────────────                       ──────────
   propostas/*.pdf  ─────►  download new files
                            │
                            ▼
                            parse filename → "<id> <CUSTOMER NAME>.pdf"
                            │
                            ▼
                            buscar_cliente(name)  ◄──────────────  registros_vendedor
                            │
                            ▼
                            rename copies for uniqueness in AGGER
                            │
                            ▼
                            pywinauto → AGGER GESTOR
                              • open "Criar Prospecção"
                              • fill name, item, status, situação,
                                seller, owner, phone, notes, due date
                              • attach renamed files
                              • save
                            │
                            ▼
                            on success:
                              • atualizar_data_prospectada(id) ──►  UPDATE registros_vendedor
                              • move originals to processados/
                              • delete originals from VPS
                              • delete temp renamed copies
                            │
                            ▼
                            append result to automacao_log.txt
```

---

## Project layout

```
aggerpilot/
├── main.py                # orchestrator: sync → group by client → drive AGGER
├── agger.py               # connects to AGGER GESTOR window, opens "Criar Prospecção"
├── banco.py               # PostgreSQL: lookup client + write back data_prospectada
├── config.py              # loads .env (SSH, DB, paths)
├── copiar_propostas.py    # SFTP sync of VPS → local proposals folder
├── gerenciador_sftp.py    # thin SFTP context manager around paramiko
├── responsavel.py         # selects the "Responsável" combobox in AGGER
├── consultar.py           # ad-hoc DB query helper
├── preencher/             # per-field UI fillers
│   ├── preencher.py         # entry point — runs all fillers in order
│   ├── nome.py              # customer name
│   ├── item.py              # product / item
│   ├── status.py            # status combobox
│   ├── vendedor.py          # seller combobox
│   ├── responsavel.py       # responsible person combobox
│   ├── telefone.py          # phone field
│   ├── vencimento.py        # due date
│   ├── observacoes.py       # observations / notes
│   ├── anexar.py            # attaches PDFs and images
│   ├── salvar.py            # final save
│   ├── criar_tarefa.py      # creates follow-up task
│   └── sair_em_renovacoes.py
├── requirements.txt
└── automacao_log.txt      # generated — per-client run log
```

---

## Requirements

- **Windows** with **AGGER GESTOR** installed and reachable on screen (the bot drives its UI through `pywinauto` + UIA).
- **Python 3.10+**.
- **PostgreSQL** instance with `registros_vendedor` and `anexos` tables.
- **SSH/SFTP** access to the VPS that hosts incoming proposals.
- Dependencies:
  ```
  python-dotenv
  paramiko
  pywinauto[uia]
  pyautogui
  opencv-python
  pillow
  numpy
  psycopg2-binary
  ```

---

## Installation

```bash
git clone https://github.com/mfzera/aggerpilot.git
cd aggerpilot
python -m venv .venv
.venv\Scripts\activate          # PowerShell:  .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Then create a `.env` (see below) — **never commit it.**

---

## Configuration

All credentials and paths come from a `.env` at the project root:

```dotenv
# SSH / SFTP — VPS that holds incoming proposals
SSH_HOST=vps.example.com
SSH_USER=deploy
SSH_PASS=change-me
REMOTO_PDFS=/var/www/propostas

# PostgreSQL
DB_HOST=db.example.com
DB_NAME=agger
DB_USER=agger
DB_PASS=change-me
DB_PORT=5432

# Local working folder for downloaded proposals
LOCAL_PROPOSTAS=C:\AggerPilot\propostas
```

---

## Usage

1. Open **AGGER GESTOR** and leave the main menu visible and focused.
2. Run:
   ```bash
   python main.py
   ```
3. The bot will:
   - Sync new files from the VPS to `LOCAL_PROPOSTAS`.
   - Wait 5 seconds (so you can finish moving the mouse out of the way).
   - Process each customer group, one at a time.
   - Pause 3s between customers to let AGGER settle.

**While it runs, don't touch the keyboard or mouse** — `pywinauto` drives real OS-level focus and clicks.

### Filename convention

Files in `REMOTO_PDFS` must be named:

```
<CLIENT_ID> <CUSTOMER NAME>[ optional suffix].<ext>
```

Examples:
- `712 MIGUEL FERREIRA.pdf`
- `712 MIGUEL FERREIRA_2.jpg`
- `1083 ACME COMERCIO LTDA 3.png`

Files sharing the same `<ID> <NAME>` prefix are grouped and attached to a single AGGER record. Supported extensions: `.pdf .jpg .jpeg .png .bmp .gif`.

### What happens on success vs. failure

| Outcome | Files | Database | Log line |
|---|---|---|---|
| Success | originals → `processados/`, deleted from VPS, renamed temps removed | `data_prospectada = NOW()` | `<key> - SUCESSO - (ts) - (seller)` |
| Customer missing in DB | left in place | untouched | `CLIENTE NÃO ENCONTRADO NO BANCO` |
| Fill failed in AGGER | left in place | untouched | `FALHA NO PREENCHIMENTO` |
| Unexpected error | left in place | untouched | `ERRO INESPERADO (<exc>)` |

Logs are appended to `automacao_log.txt`.

---

## Database expectations

`banco.py` expects two tables:

**`registros_vendedor`**
| column | use |
|---|---|
| `id` | primary key, used to link attachments and to update `data_prospectada` |
| `cliente` | matched case- and trim-insensitive against the filename's customer name |
| `produto`, `observacao`, `situacao`, `status`, `vendedor`, `pct_atual`, `salvo_por` | fed into the AGGER form |
| `data_atualizacao` | used to pick the **latest** row when a customer has multiple |
| `data_prospectada` | stamped with `NOW()` after a successful AGGER save |

**`anexos`**
| column | use |
|---|---|
| `registro_id` | FK to `registros_vendedor.id` |
| `file_path` | path of any extra attachments pre-registered in the system |

---

## Security notes

- The `.env` file is **secrets** — keep it out of git. The repo should contain a `.env.example` instead.
- VPS credentials, DB credentials, and proposal files often contain personal data; treat the local `propostas/` folder as sensitive.
- The bot uses `AutoAddPolicy` for SSH host keys — fine for first-run, but consider pinning the host key in production.

---

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `O aplicativo 'AGGER GESTOR' não foi encontrado` | AGGER isn't open, or its window title changed |
| `Cliente '...' não encontrado no banco` | Filename's customer name doesn't match `registros_vendedor.cliente` (check spaces / accents) |
| ComboBox click misses | UI element index drifted — adjust `found_index` in `preencher/*.py` |
| SFTP timeout | Verify `SSH_HOST` / firewall; the bot uses port 22 |

---

## Roadmap ideas

- Headless dry-run mode (parse + DB lookup, skip the UI).
- Replace positional combobox indexes with stable AutomationId lookups.
- Structured (JSON) log alongside `automacao_log.txt`.
- Retry with backoff on transient AGGER focus errors.

---

## License

No license declared yet — add one (MIT / Apache-2.0 are common for tools like this) before sharing publicly.
