"""Terminal Tic-Tac-Toe over TCP, using only the Python standard library."""

from __future__ import annotations

import socket
from typing import Optional

from game import Board, GameOver, InvalidMove, format_board, parse_position

HOST = "0.0.0.0"
PORT = 5000


def create_connection() -> socket.socket:
    """Host a game and return the connected peer socket."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(1)
        print(f"\nAguardando o adversário na porta TCP {PORT}...")
        print("Para conectar nesta partida, informe o IP deste computador.")
        connection, address = server.accept()
        print(f"Conexão estabelecida com {address[0]}:{address[1]}.")
        return connection


def join_connection() -> socket.socket:
    """Connect to a game hosted by another player."""
    while True:
        host = input("IP do computador que criou a partida: ").strip()
        if not host:
            print("Informe um endereço IP.")
            continue
        try:
            connection = socket.create_connection((host, PORT), timeout=10)
            connection.settimeout(None)
            print(f"Conectado ao servidor {host}:{PORT}.")
            return connection
        except (OSError, socket.timeout) as exc:
            print(f"Não foi possível conectar: {exc}")
            retry = input("Tentar novamente? (s/n): ").strip().lower()
            if retry != "s":
                raise SystemExit(1)


def show_menu() -> str:
    print("=== Jogo da Velha em Rede (TCP) ===")
    print("1. Criar partida (jogar como X)")
    print("2. Entrar em partida (jogar como O)")
    while True:
        choice = input("Escolha uma opção: ").strip()
        if choice in {"1", "2"}:
            return choice
        print("Opção inválida. Digite 1 ou 2.")


def read_local_move(board: Board, mark: str) -> Optional[tuple[int, int]]:
    """Read and validate a move; return None when the player chooses to quit."""
    while True:
        raw = input(f"Jogador {mark}, informe linha e coluna (0-2), ou 'sair': ").strip()
        if raw.lower() in {"sair", "quit", "q"}:
            return None
        try:
            row, col = parse_position(raw)
            board.validate_move(row, col)
            return row, col
        except InvalidMove as exc:
            print(f"Jogada inválida: {exc}")


def send_line(connection: socket.socket, message: str) -> None:
    """Send one newline-terminated protocol message."""
    connection.sendall((message + "\n").encode("utf-8"))


def receive_line(reader) -> Optional[str]:
    """Read exactly one protocol message; None means the peer closed the connection."""
    line = reader.readline()
    if line == "":
        return None
    return line.rstrip("\r\n")


def play(connection: socket.socket, mark: str) -> None:
    opponent = "O" if mark == "X" else "X"
    board = Board()
    current_turn = "X"

    # makefile.readline() handles TCP's stream nature and message delimiters:
    # each application message ends at a newline, not at a TCP packet boundary.
    with connection, connection.makefile("r", encoding="utf-8", newline="\n") as reader:
        print("\nPartida iniciada! X começa.")
        print("Digite linha e coluna de 0 a 2, por exemplo: 1 2")
        print("Digite 'sair' para encerrar a partida.\n")
        print(format_board(board.cells))

        while True:
            if current_turn == mark:
                move = read_local_move(board, mark)
                if move is None:
                    try:
                        send_line(connection, "QUIT")
                    except OSError:
                        pass
                    print("Você encerrou a partida.")
                    return

                row, col = move
                # The move was validated before being sent, then applied locally.
                board.place(row, col, mark)
                try:
                    send_line(connection, f"MOVE {row} {col}")
                except OSError:
                    print("\nA conexão com o adversário foi encerrada.")
                    return
                print(f"\nVocê jogou em ({row}, {col}).")
                print(format_board(board.cells))
            else:
                print(f"\nAguardando a jogada de {opponent}...")
                try:
                    message = receive_line(reader)
                except (OSError, UnicodeError):
                    message = None

                if message is None:
                    print("\nA conexão com o adversário foi encerrada.")
                    return
                if message == "QUIT":
                    print("\nO adversário encerrou a partida.")
                    return
                if not message.startswith("MOVE "):
                    print(f"\nMensagem inválida recebida: {message!r}")
                    print("Encerrando a partida por erro de protocolo.")
                    return

                parts = message.split()
                if len(parts) != 3:
                    print("\nMensagem de jogada malformada. Partida encerrada.")
                    return
                try:
                    row, col = int(parts[1]), int(parts[2])
                    board.place(row, col, opponent)
                except (ValueError, InvalidMove):
                    print("\nO adversário enviou uma jogada inválida. Partida encerrada.")
                    return
                print(f"\nO adversário ({opponent}) jogou em ({row}, {col}).")
                print(format_board(board.cells))

            winner = board.winner()
            if winner:
                print(f"\nFim de jogo: jogador {winner} venceu!")
                return
            if board.is_full():
                print("\nFim de jogo: empate!")
                return

            current_turn = opponent if current_turn == mark else mark


def main() -> None:
    choice = show_menu()
    try:
        connection = create_connection() if choice == "1" else join_connection()
        play(connection, "X" if choice == "1" else "O")
    except KeyboardInterrupt:
        print("\nAplicação interrompida.")
    except OSError as exc:
        print(f"\nErro de rede: {exc}")


if __name__ == "__main__":
    main()
