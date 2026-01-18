# Discord Vanity Role Bot

## Overview
A Discord bot that automatically assigns roles to users who have a specific vanity URL or text in their Discord status.

## Project Structure
- `main.py` - Main bot code with Discord event handlers
- `Settings.json` - Bot configuration (prefix, status, role settings)

## Configuration
The bot reads configuration from `Settings.json`:
- `Prefix` - Command prefix (e.g., `!`)
- `botStatus` - Bot's activity type (playing, streaming, watching, listening)
- `vanityURL` - The text users need in their status to get the role
- `Status` - Bot's custom status message
- `modeStatus` - Bot's online status (online, dnd, idle, offline)
- `channelLogs` - Channel ID for logging role changes
- `roleName` - Name of the role to assign

## Secrets Required
- `DISCORD_BOT_TOKEN` - Your Discord bot token from the Discord Developer Portal

## Running the Bot
The bot runs via `python main.py` and requires the `DISCORD_BOT_TOKEN` secret to be set.

## Dependencies
- discord.py
- colorama
