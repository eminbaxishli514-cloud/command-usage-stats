# Command Usage Stats

Tracks your shell commands over time, showing frequency, last use, and patterns.

## Features

- **Command Tracking**: Automatically track shell commands
- **Usage Statistics**: View command frequency and patterns
- **Most Used Commands**: See your most frequently used commands
- **Last Used**: Track when commands were last used
- **Pattern Analysis**: Identify command usage patterns
- **Export Data**: Export statistics for analysis

## Installation

```bash
pip install -r requirements.txt
```

## Setup

Add to your shell configuration file (`.bashrc`, `.zshrc`, etc.):

```bash
# For bash
export PROMPT_COMMAND='python /path/to/command_tracker.py log "$(history 1)"'

# For zsh
precmd() { python /path/to/command_tracker.py log "$(history -1)" }
```

## Usage

```bash
python command_tracker.py [COMMAND] [OPTIONS]
```

### Commands

- `log COMMAND`: Log a command (usually called automatically)
- `stats`: Show command usage statistics
- `top N`: Show top N most used commands
- `search QUERY`: Search for commands
- `export`: Export statistics

### Options

- `--days N`: Show stats for last N days
- `--format FORMAT`: Output format (text, json, csv)

### Examples

```bash
# Show statistics
python command_tracker.py stats

# Show top 10 commands
python command_tracker.py top 10

# Show stats for last 7 days
python command_tracker.py stats --days 7

# Search for git commands
python command_tracker.py search git

# Export statistics
python command_tracker.py export --format json
```

## Data Storage

Command history is stored in:
- `~/.command_stats/commands.json` - Command data

