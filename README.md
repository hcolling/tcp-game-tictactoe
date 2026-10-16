# Tic-Tac-Toe TCP Game

A two-player terminal Tic-Tac-Toe game in Python using TCP sockets. It uses only the Python standard library.

## Features

- Create a match as **X** (TCP server, port `5000`); X plays first.
- Join a match as **O** using the host computer's IP address.
- Keep both boards synchronized by transmitting every move.
- Validate coordinates and reject occupied positions.
- Detect wins by row, column, or diagonal, as well as draws.
- Report when the opponent disconnects or leaves the game.
- Unit tests for game rules.

## Requirements

- Python 3.9 or newer.
- No third-party packages.

## Run locally

Open two terminals in the same computer.

**Terminal 1 — host / X**
```bash
python main.py
```
Choose `1. Criar partida`. The application waits for a connection on port `5000`.

**Terminal 2 — guest / O**
```bash
python main.py
```
Choose `2. Entrar em partida` and enter:
```text
127.0.0.1
```

On Windows, use `py main.py` if `python` is not recognized.

## Run on two computers

1. Connect both computers to a network that allows connections between them.
2. On the host computer, run `python main.py` and choose option `1`.
3. Find the host computer's local IP address (for example, with `ipconfig` on Windows or `ip addr` on Linux).
4. If necessary, allow inbound TCP traffic on port `5000` in the host firewall.
5. On the second computer, run `python main.py`, choose option `2`, and enter the host's IP address.

Both computers must be able to reach each other. Guest Wi-Fi networks, NAT, VPNs, and institutional firewalls may block direct connections. Do not expose port `5000` to the public internet just for this classroom exercise.

## How to play

Enter the row and column as two numbers from `0` to `2`, for example:
```text
1 2
```
The first number is the row; the second is the column. `0 0` is the top-left cell. A move into an occupied cell is rejected and the current player can try again. Type `sair` to leave the match.

## Application protocol

Messages are UTF-8 text terminated by a newline (`\n`). Each message is one line:

| Message | Meaning |
| --- | --- |
| `MOVE <row> <col>\n` | Play at the given row and column (each in the range 0–2) |
| `QUIT\n` | The sender is leaving the match |

Example:
```text
MOVE 0 2
```

### Why newline framing?

TCP is a byte stream and does not preserve application message boundaries: one `sendall()` may be received in multiple chunks, or several messages may arrive together. The receiver uses `makefile(...).readline()` to read until the newline delimiter. Therefore, it processes one complete application message at a time rather than assuming one `recv()` equals one message.

The receiving side validates the message format, coordinates, and whether the target cell is empty before applying a remote move. If the peer closes the connection, `readline()` returns an empty string and the program reports the disconnection.

## Design overview

- `main.py`: menu, TCP connection setup, turn-taking, protocol, and terminal interface.
- `game.py`: board state, move validation, win/draw detection, and board formatting.
- `tests/test_game.py`: unit tests for core game rules.

## Run tests

From the repository root:
```bash
python -m unittest discover -s tests -v
```
