# Vibe Hardware

> Build hardware projects with ESP32 using AI coding agents — no experience required.

From the [Coding from Beach](https://www.codingfrombeach.com) workshop series.

---

## What is this?

This repo is your starting point for the CfB vibe hardware workshop. You describe what you want your device to do, and your coding agent (Claude Code, Codex, Cursor, etc.) handles the rest — writing the code, compiling it, and flashing it to your board.

No terminal skills needed. No hardware experience needed. Just vibes.

---

## What you need

- A laptop (charged)
- A USB-C cable
- A coding agent: Claude Code, Codex, or Cursor
- An ESP32 board - provided

---

## Getting started

Open this repo in your coding agent and say:

> "Check my bootstrap and get me set up"

The agent will take it from there — installing any tools needed and connecting to your board.

---

## The board

Workshop boards are the **DFRobot FireBeetle 2 ESP32-C6** running MicroPython. Full hardware reference is in `BOARD.md`.

If you brought your own ESP32, that works too — let your agent know what board you have.

---

## How it works

1. Agent checks your setup and installs anything missing
2. You describe what you want to build
3. Agent writes the code and uploads it to your board
4. Repeat

---

## Repo structure

```
BOARD.md              — hardware reference (pinout, GPIO, chip specs)
CLAUDE.md             — instructions for your coding agent
AGENTS.md             — same, for non-Claude agents
board.sh              — CLI for board operations (test/repl/upload/flash/monitor)
scripts/              — MicroPython Python scripts
sketches/             — Arduino C sketches
firmware/             — MicroPython firmware .bin
docs/                 — reference docs and cheatsheets
```
