# Git-based CTF v2.0

**A fully distributed, serverless attack-and-defense CTF framework.**

All data lives on GitHub. No dedicated server required.  
Based on the paper: [Git-based CTF (ASE 2018, KAIST SoftSec Lab)](ase18-paper_wi.pdf)

## Core Principle

> "Instructors in Git-based CTF **do not have to prepare a separate server** to run a CTF."
> "Git-based CTF is a **fully distributed** CTF framework, which **does not have a dedicated web server**."

- **GitHub = single source of truth**: repos, issues, notifications, score.csv
- **Docker = local only**: each participant builds/runs services and exploits on their own machine
- **CLI scripts**: instructors and participants interact via command-line tools
- **GPG encryption**: exploits are encrypted before submission as GitHub Issues

## Architecture

```
┌─────────────────────────────────────────────────┐
│                    GitHub                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Team1    │  │ Team2    │  │ Scoreboard   │  │
│  │ Repo     │  │ Repo     │  │ Repo         │  │
│  │ (code,   │  │ (code,   │  │ (score.csv)  │  │
│  │  issues) │  │  issues) │  │              │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
└──────────────────────┬──────────────────────────┘
                       │ GitHub API
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
  ┌──────────┐  ┌──────────┐  ┌──────────────┐
  │ Student  │  │ Student  │  │ Instructor   │
  │ Machine  │  │ Machine  │  │ Machine      │
  │          │  │          │  │              │
  │ gitctf   │  │ gitctf   │  │ gitctf eval  │
  │ Docker   │  │ Docker   │  │ gitctf score │
  │ GPG      │  │ GPG      │  │ Docker, GPG  │
  └──────────┘  └──────────┘  └──────────────┘
```

## Prerequisites

- Python 3.11+
- Docker
- Git
- GPG
- GitHub account + Personal Access Token (`repo`, `notifications` scopes)

## Quick Start

```bash
# 1. Clone
git clone https://github.com/YOUR_ORG/GitCTF.git
cd GitCTF

# 2. Install dependencies
pip install -r requirements.txt

# 3. Edit config.json with your settings
#    - Set player, player_team, repo_owner, teams, etc.

# 4. Set your GitHub token
export GITHUB_TOKEN=ghp_your_token_here
```

## Competition Workflow

### Phase 1: Preparation
Each team prepares a network service with a Dockerfile.

```bash
# Verify your service builds and runs
python gitctf.py verify-service --team team1 --branch master --conf config.json
```

### Phase 2: Injection
Each team injects N vulnerabilities into separate branches (bug1, bug2, ...).

```bash
# Verify injected vulnerabilities
python gitctf.py verify-injection --team team1 --conf config.json

# Verify your own exploit against your vulnerability
python gitctf.py verify-exploit \
  --exploit ./my-exploit/ \
  --service-dir ./team1-service/ \
  --branch bug1 \
  --timeout 60 \
  --encrypt \
  --conf config.json
```

### Phase 3: Exercise (Attack & Defense)

**Attack:**
```bash
# 1. Verify exploit works locally
python gitctf.py verify-exploit \
  --exploit ./exploit/ \
  --service-dir ./target-service/ \
  --branch bug1 \
  --timeout 60 \
  --conf config.json

# 2. Submit as encrypted GitHub Issue
python gitctf.py submit \
  --exploit ./exploit/ \
  --service-dir ./target-service/ \
  --branch bug1 \
  --target team2 \
  --conf config.json
```

**Defense:**
Fix unintended vulnerabilities, push patches to master branch.

**View Scoreboard:**
```bash
python gitctf.py score --conf config.json
# Generates score.html with time-series graph
```

## Instructor Commands

```bash
# Setup CTF environment (create repos on GitHub)
python gitctf.py setup --admin-conf .config.json --token ghp_xxx

# Auto-grade: poll GitHub for new submissions and verify
python gitctf.py eval --conf config.json --token ghp_xxx

# Get commit hashes for all teams
python gitctf.py hash --conf config.json --token ghp_xxx
```

## Project Structure

```
GitCTF/
├── gitctf.py              # Main CLI entry point
├── config.json            # Competition configuration
├── requirements.txt       # Python dependencies
├── lib/                   # Core modules
│   ├── github_api.py      # GitHub API client (httpx)
│   ├── git.py             # Local git operations
│   ├── crypto.py          # GPG encrypt/decrypt
│   ├── issue.py           # GitHub Issue operations
│   ├── execute.py         # Docker service/exploit execution
│   ├── verify_exploit.py  # Exploit verification engine
│   ├── verify_service.py  # Service health check
│   ├── verify_injection.py# Injection phase verification
│   ├── verify_issue.py    # Issue-based exploit verification
│   ├── submit.py          # Exploit submission via Issue
│   ├── fetch.py           # Fetch & decrypt exploit from Issue
│   ├── show_score.py      # Scoreboard (fetch from GitHub)
│   ├── evaluate.py        # Auto-grading loop
│   ├── get_hash.py        # Branch hash collector
│   ├── setup_env.py       # CTF environment setup
│   └── utils.py           # Shared utilities
├── templates/
│   └── skeletons/         # Starter code for services/exploits
├── rulebook/              # Competition guides (instructor/student)
└── _legacy/               # Original Python 2 implementation
```

## How Scoring Works

1. Instructor runs `gitctf eval` which polls GitHub Notifications
2. When a new Issue (exploit submission) is detected:
   - Clone target repo locally
   - Decrypt the exploit
   - Build service in Docker, inject random flag
   - Run exploit in Docker, check if it returns the flag
   - Write result to `score.csv` in the scoreboard repo
   - Push to GitHub
3. Anyone can run `gitctf score` to fetch `score.csv` and see standings

## Key Differences from v1.0

- **Python 3.11+** (was Python 2.7)
- **httpx** instead of raw requests (modern async-ready HTTP)
- **Type hints** throughout
- **Proper error handling** and cleanup
- **`flag{...}` format** support (configurable)
- **Structured CLI** with argparse subcommands
- **Templates** for services and exploits

## License

Apache License 2.0

## Citation

```bibtex
@inproceedings{gitctf2018,
  title={Git-based CTF: A Simple and Effective Approach to Organizing
         In-Course Attack-and-Defense Security Competition},
  author={Wi, SeongIl and Choi, Jaeseung and Cha, Sang Kil},
  booktitle={Proceedings of the 33rd IEEE/ACM International Conference
             on Automated Software Engineering (ASE)},
  year={2018}
}
```
