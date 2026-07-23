# Cambria Bot

Automated bot for the [Cambria](https://lobby.cambria.gg) gaming platform. Handles account setup and loot drop claiming across multiple wallets concurrently.

## Features

- **Multi-account automation** — processes accounts in parallel (default concurrency: 2)
- **Privy SIWE authentication** — signs in with Ethereum via EVM private keys
- **Solana wallet linking** — optional Solana wallet association per account
- **Proxy rotation** — HTTP proxy support for request distribution
- **Random profile generation** — Faker-based nicknames and character avatars
- **Loot drop claiming** — automatically checks and claims Common, Epic, and Legendary chests
- **SQLite persistence** — tracks account state and chest counts locally

## Project Structure

```
cambria/
├── main.py              # Entry point — CLI menu and asyncio runner
├── cambria.py           # Core bot logic (auth, sessions, claiming)
├── db/
│   ├── db.py            # SQLAlchemy engine/session (SQLite)
│   ├── models.py        # User ORM model
│   └── user_api.py      # CRUD operations
├── utils/
│   └── create_files.py  # File init + user creation from text files
└── files/
    ├── private_evm.txt  # EVM private keys (one per line)
    ├── private_sol.txt  # Solana private keys (one per line)
    ├── proxy.txt        # HTTP proxies (one per line)
    └── accounts.db      # SQLite database (auto-created)
```

## Requirements

- Python 3.11+
- Dependencies: `aiohttp`, `eth-account`, `solders`, `base58`, `faker`, `sqlalchemy`

## Setup

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install aiohttp eth-account solders base58 faker sqlalchemy
```

3. Add your wallet keys and proxies to the `files/` directory:

```
files/private_evm.txt   — one EVM private key per line
files/private_sol.txt   — one Solana private key per line (optional, same order as EVM)
files/proxy.txt         — one HTTP proxy per line (optional, same order as EVM)
```

## Usage

```bash
python main.py
```

The CLI presents two options:

1. **Init DB** — reads the text files and creates User records in `files/accounts.db`
2. **Start Actions** — runs the full automation workflow for all accounts:
   - Proxy validation/rotation
   - Privy SIWE authentication
   - Session acquisition
   - Account creation (random nickname, avatar, invite code `thedescent`)
   - Solana wallet linking (if key provided)
   - Loot drop chest claiming

## How It Works

1. Each account authenticates via [Privy](https://privy.io) using SIWE (Sign-In With Ethereum)
2. After authentication, a Cambria session token is obtained
3. If the account is new, it goes through setup: random nickname, character selection, and invite code validation
4. Optionally links a Solana wallet via signed message verification
5. Checks eligibility for loot drop chests and claims available rewards
6. Chest counts are tracked in the local SQLite database to avoid duplicate claims
