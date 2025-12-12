#!/usr/bin/env python3
"""
Command Usage Stats - Tracks shell commands over time.
"""

import os
import sys
import json
import csv
import argparse
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import Counter


class CommandTracker:
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            data_dir = Path.home() / '.command_stats'
        else:
            data_dir = Path(data_dir)
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.commands_file = self.data_dir / 'commands.json'
        self.load_commands()
    
    def load_commands(self):
        """Load command history."""
        if self.commands_file.exists():
            with open(self.commands_file, 'r') as f:
                self.commands = json.load(f)
        else:
            self.commands = []
    
    def save_commands(self):
        """Save command history."""
        with open(self.commands_file, 'w') as f:
            json.dump(self.commands, f, indent=2)
    
    def log_command(self, command_line: str):
        """Log a command."""
        # Extract command from history line
        # Format: " 123  command" or "command"
        command_line = command_line.strip()
        
        # Remove history number if present
        command = re.sub(r'^\s*\d+\s+', '', command_line)
        command = command.strip()
        
        if not command:
            return
        
        # Extract base command (first word)
        base_command = command.split()[0] if command.split() else command
        
        entry = {
            'command': command,
            'base_command': base_command,
            'timestamp': datetime.now().isoformat(),
            'full_command': command_line
        }
        
        self.commands.append(entry)
        
        # Keep only last 10000 commands
        if len(self.commands) > 10000:
            self.commands = self.commands[-10000:]
        
        self.save_commands()
    
    def get_stats(self, days: Optional[int] = None) -> Dict:
        """Get command usage statistics."""
        commands_to_analyze = self.commands
        
        # Filter by days
        if days:
            cutoff = datetime.now() - timedelta(days=days)
            commands_to_analyze = [
                c for c in self.commands
                if datetime.fromisoformat(c['timestamp']) >= cutoff
            ]
        
        # Count commands
        base_command_counts = Counter(c['base_command'] for c in commands_to_analyze)
        full_command_counts = Counter(c['command'] for c in commands_to_analyze)
        
        # Get last used times
        last_used = {}
        for cmd in commands_to_analyze:
            base = cmd['base_command']
            timestamp = datetime.fromisoformat(cmd['timestamp'])
            if base not in last_used or timestamp > last_used[base]:
                last_used[base] = timestamp
        
        return {
            'total_commands': len(commands_to_analyze),
            'unique_base_commands': len(base_command_counts),
            'base_command_counts': dict(base_command_counts),
            'full_command_counts': dict(full_command_counts),
            'last_used': {k: v.isoformat() for k, v in last_used.items()},
            'period_days': days
        }
    
    def show_stats(self, days: Optional[int] = None):
        """Display statistics."""
        stats = self.get_stats(days)
        
        print("\n" + "=" * 70)
        print("COMMAND USAGE STATISTICS")
        print("=" * 70)
        
        if stats['period_days']:
            print(f"Period: Last {stats['period_days']} days")
        else:
            print("Period: All time")
        
        print(f"Total Commands: {stats['total_commands']:,}")
        print(f"Unique Commands: {stats['unique_base_commands']}")
        print()
        
        # Top commands
        print("Most Used Commands:")
        print("-" * 70)
        sorted_commands = sorted(
            stats['base_command_counts'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]
        
        for i, (cmd, count) in enumerate(sorted_commands, 1):
            percentage = (count / stats['total_commands'] * 100) if stats['total_commands'] > 0 else 0
            last = stats['last_used'].get(cmd, '')
            if last:
                last_dt = datetime.fromisoformat(last)
                last_str = last_dt.strftime('%Y-%m-%d %H:%M')
            else:
                last_str = 'Never'
            
            print(f"{i:2d}. {cmd:<20} {count:>6} times ({percentage:5.1f}%)  Last: {last_str}")
    
    def show_top(self, n: int = 10, days: Optional[int] = None):
        """Show top N commands."""
        stats = self.get_stats(days)
        
        sorted_commands = sorted(
            stats['base_command_counts'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:n]
        
        print(f"\nTop {n} Commands:")
        print("=" * 70)
        
        for i, (cmd, count) in enumerate(sorted_commands, 1):
            percentage = (count / stats['total_commands'] * 100) if stats['total_commands'] > 0 else 0
            print(f"{i:2d}. {cmd:<30} {count:>6} times ({percentage:5.1f}%)")
    
    def search_commands(self, query: str):
        """Search for commands."""
        matching = [
            c for c in self.commands
            if query.lower() in c['command'].lower() or query.lower() in c['base_command'].lower()
        ]
        
        if not matching:
            print(f"No commands found matching '{query}'")
            return
        
        # Group by base command
        grouped = {}
        for cmd in matching:
            base = cmd['base_command']
            if base not in grouped:
                grouped[base] = []
            grouped[base].append(cmd)
        
        print(f"\nCommands matching '{query}':")
        print("=" * 70)
        
        for base, cmds in sorted(grouped.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"\n{base} ({len(cmds)} occurrences):")
            # Show unique full commands
            unique_commands = set(c['command'] for c in cmds)
            for full_cmd in sorted(unique_commands)[:5]:
                print(f"  {full_cmd}")
            if len(unique_commands) > 5:
                print(f"  ... and {len(unique_commands) - 5} more")
    
    def export_stats(self, format_type: str = 'json', output_file: Optional[str] = None):
        """Export statistics."""
        stats = self.get_stats()
        
        if format_type == 'json':
            data = {
                'statistics': stats,
                'export_date': datetime.now().isoformat()
            }
            output = json.dumps(data, indent=2)
        elif format_type == 'csv':
            # Export top commands as CSV
            sorted_commands = sorted(
                stats['base_command_counts'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            lines = ['Command,Count,Percentage,Last Used']
            for cmd, count in sorted_commands:
                percentage = (count / stats['total_commands'] * 100) if stats['total_commands'] > 0 else 0
                last = stats['last_used'].get(cmd, '')
                lines.append(f"{cmd},{count},{percentage:.2f},{last}")
            
            output = '\n'.join(lines)
        else:
            output = str(stats)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(output)
            print(f"Statistics exported to: {output_file}")
        else:
            print(output)


def main():
    parser = argparse.ArgumentParser(description='Command Usage Stats')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Log command
    log_parser = subparsers.add_parser('log', help='Log a command')
    log_parser.add_argument('command_line', type=str, help='Command line to log')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.add_argument('--days', type=int, help='Show stats for last N days')
    
    # Top command
    top_parser = subparsers.add_parser('top', help='Show top commands')
    top_parser.add_argument('n', type=int, nargs='?', default=10, help='Number of commands to show')
    top_parser.add_argument('--days', type=int, help='Show stats for last N days')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search commands')
    search_parser.add_argument('query', type=str, help='Search query')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export statistics')
    export_parser.add_argument('--format', choices=['json', 'csv', 'text'],
                               default='json', help='Export format')
    export_parser.add_argument('--output', type=str, help='Output file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    tracker = CommandTracker()
    
    if args.command == 'log':
        tracker.log_command(args.command_line)
    elif args.command == 'stats':
        tracker.show_stats(getattr(args, 'days', None))
    elif args.command == 'top':
        tracker.show_top(getattr(args, 'n', 10), getattr(args, 'days', None))
    elif args.command == 'search':
        tracker.search_commands(args.query)
    elif args.command == 'export':
        tracker.export_stats(
            getattr(args, 'format', 'json'),
            getattr(args, 'output', None)
        )


if __name__ == '__main__':
    main()

