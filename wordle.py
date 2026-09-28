#!/usr/bin/env python3

import random
import os
import sys

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
WORD_FILE   = os.path.join(SCRIPT_DIR, "sowpods_5letter.txt")
SOWPODS_URL = ("https://raw.githubusercontent.com/jesstess/Scrabble"
               "/master/scrabble/sowpods.txt")


def load_words():
    if os.path.exists(WORD_FILE):
        with open(WORD_FILE, "r") as fh:
            words = [w.strip().upper() for w in fh
                     if w.strip().isalpha() and len(w.strip()) == 5]
        if words:
            return words
    print("Downloading SOWPODS word list...")
    try:
        import urllib.request
        with urllib.request.urlopen(SOWPODS_URL, timeout=15) as resp:
            lines = resp.read().decode("utf-8").splitlines()
        words = [w.strip().upper() for w in lines
                 if w.strip().isalpha() and len(w.strip()) == 5]
        with open(WORD_FILE, "w") as fh:
            fh.write("\n".join(words))
        return words
    except Exception as exc:
        print(f"Could not fetch word list: {exc}")
        sys.exit(1)


def get_feedback(guess, answer):
    feedback    = ["B"] * 5
    answer_pool = list(answer)
    for i in range(5):
        if guess[i] == answer[i]:
            feedback[i]    = "G"
            answer_pool[i] = None
    for i in range(5):
        if feedback[i] == "B" and guess[i] in answer_pool:
            feedback[i] = "Y"
            answer_pool[answer_pool.index(guess[i])] = None
    return "".join(feedback)


# ── TEXT MODE ─────────────────────────────────────────────────────────────────

def text_header():
    print()
    print("  ========================================")
    print("       WORDLE  -  Terminal Edition        ")
    print("         SOWPODS  .  5 letters            ")
    print("  ========================================")
    print()
    print("  G = Correct position")
    print("  Y = Wrong position")
    print("  B = Not in word")
    print()


def text_board(guesses, feedbacks):
    print()
    print("  " + "-" * 34)
    for g, fb in zip(guesses, feedbacks):
        print(f"  {' '.join(g)}    [{fb}]")
    for _ in range(6 - len(guesses)):
        print("  _  _  _  _  _    [-----]")
    print("  " + "-" * 34)
    print()


def text_keyboard(guesses, feedbacks):
    status   = {}
    priority = {"G": 3, "Y": 2, "B": 1}
    for guess, fb in zip(guesses, feedbacks):
        for ch, f in zip(guess, fb):
            if priority.get(f, 0) > priority.get(status.get(ch, ""), 0):
                status[ch] = f
    rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
    print("  -- Keyboard --")
    for row in rows:
        line = "  "
        for ch in row:
            line += f"{ch}({status.get(ch, '.')}) "
        print(line)
    print()


def play_text_game(words, word_set):
    answer    = random.choice(words)
    guesses   = []
    feedbacks = []
    text_header()
    text_board(guesses, feedbacks)
    for attempt in range(1, 7):
        while True:
            try:
                raw = input(f"  Guess {attempt}/6: ").strip().upper()
            except (EOFError, KeyboardInterrupt):
                print("\n\nGame aborted.\n")
                sys.exit(0)
            if len(raw) != 5:
                print("  Please enter exactly 5 letters.")
            elif not raw.isalpha():
                print("  Letters only - no numbers or symbols.")
            elif raw not in word_set:
                print(f"  '{raw}' is not in the SOWPODS list. Try again.")
            else:
                break
        fb = get_feedback(raw, answer)
        guesses.append(raw)
        feedbacks.append(fb)
        text_board(guesses, feedbacks)
        text_keyboard(guesses, feedbacks)
        if fb == "GGGGG":
            medals = ["(1st!)", "(2nd)", "(3rd)", "(4th)", "(5th)", "(6th - phew!)"]
            print(f"  Congratulations! You guessed '{answer}' in {attempt}/6 {medals[attempt-1]}!\n")
            return True
    print(f"  Game Over! The word was: {answer}\n")
    return False


def run_text_mode(words, word_set):
    wins, games = 0, 0
    while True:
        games += 1
        if play_text_game(words, word_set):
            wins += 1
        print(f"  Session: {wins} win(s) / {games} game(s)\n")
        again = input("  Play again? [y/n]: ").strip().lower()
        if again not in ("y", "yes"):
            break


# ── COLOUR MODE ───────────────────────────────────────────────────────────────

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    WHITE  = "\033[97m"
    CYAN   = "\033[96m"
    YELLOW = "\033[93m"
    GREEN  = "\033[92m"
    RED    = "\033[91m"
    GRAY   = "\033[90m"
    TILE_G = "\033[42m\033[97m"
    TILE_Y = "\033[43m\033[97m"
    TILE_B = "\033[100m\033[97m"

_TILE  = {"G": C.TILE_G, "Y": C.TILE_Y, "B": C.TILE_B}
_LABEL = {"G": f"{C.GREEN}G{C.RESET}", "Y": f"{C.YELLOW}Y{C.RESET}", "B": f"{C.GRAY}B{C.RESET}"}


def colour_header():
    print(f"\n{C.BOLD}{C.CYAN}"
          "╔══════════════════════════════════════╗\n"
          "║     WORDLE  -  Terminal Edition      ║\n"
          "║        SOWPODS  .  5 letters         ║\n"
          "╚══════════════════════════════════════╝"
          f"{C.RESET}\n")
    print(f"  {C.TILE_G} G {C.RESET} Correct position   "
          f"{C.TILE_Y} Y {C.RESET} Wrong position   "
          f"{C.TILE_B} B {C.RESET} Not in word\n")


def colour_board(guesses, feedbacks):
    empty = f"  {C.DIM}[ _ ] [ _ ] [ _ ] [ _ ] [ _ ]{C.RESET}"
    print()
    for g, fb in zip(guesses, feedbacks):
        tiles  = "".join(f"{_TILE[f]} {l} {C.RESET}" for l, f in zip(g, fb))
        labels = "".join(_LABEL[f] for f in fb)
        print(f"  {tiles}   [{labels}]")
    for _ in range(6 - len(guesses)):
        print(empty)
    print()


def colour_keyboard(guesses, feedbacks):
    status   = {}
    priority = {"G": 3, "Y": 2, "B": 1}
    for guess, fb in zip(guesses, feedbacks):
        for ch, f in zip(guess, fb):
            if priority.get(f, 0) > priority.get(status.get(ch, ""), 0):
                status[ch] = f
    rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
    print(f"  {C.DIM}-- Keyboard --{C.RESET}")
    for row in rows:
        line = "  "
        for ch in row:
            fb = status.get(ch)
            if   fb == "G": line += f"{C.TILE_G} {ch} {C.RESET}"
            elif fb == "Y": line += f"{C.TILE_Y} {ch} {C.RESET}"
            elif fb == "B": line += f"{C.GRAY} {ch} {C.RESET}"
            else:           line += f"{C.WHITE}{C.DIM} {ch} {C.RESET}"
        print(line)
    print()


def play_colour_game(words, word_set):
    answer    = random.choice(words)
    guesses   = []
    feedbacks = []
    colour_header()
    colour_board(guesses, feedbacks)
    for attempt in range(1, 7):
        while True:
            try:
                raw = input(f"  {C.BOLD}Guess {attempt}/6:{C.RESET}  ").strip().upper()
            except (EOFError, KeyboardInterrupt):
                print(f"\n\n{C.YELLOW}Game aborted.{C.RESET}\n")
                sys.exit(0)
            if len(raw) != 5:
                print(f"  {C.YELLOW}Please enter exactly 5 letters.{C.RESET}")
            elif not raw.isalpha():
                print(f"  {C.YELLOW}Letters only - no numbers or symbols.{C.RESET}")
            elif raw not in word_set:
                print(f"  {C.YELLOW}'{raw}' is not in the SOWPODS list. Try again.{C.RESET}")
            else:
                break
        fb = get_feedback(raw, answer)
        guesses.append(raw)
        feedbacks.append(fb)
        print("\033[2J\033[H", end="")
        colour_header()
        colour_board(guesses, feedbacks)
        colour_keyboard(guesses, feedbacks)
        if fb == "GGGGG":
            medals = ["(1st!)", "(2nd)", "(3rd)", "(4th)", "(5th)", "(6th - phew!)"]
            print(f"  {C.GREEN}{C.BOLD}Congratulations! You guessed '{answer}' "
                  f"in {attempt}/6 {medals[attempt-1]}!{C.RESET}\n")
            return True
    print(f"  {C.RED}{C.BOLD}Game Over! The word was: {C.WHITE}{answer}{C.RESET}\n")
    return False


def run_colour_mode(words, word_set):
    wins, games = 0, 0
    while True:
        games += 1
        if play_colour_game(words, word_set):
            wins += 1
        print(f"  {C.DIM}Session: {wins} win(s) / {games} game(s){C.RESET}\n")
        again = input("  Play again? [y/n]: ").strip().lower()
        if again not in ("y", "yes"):
            break
        print("\033[2J\033[H", end="")


# ── WEB MODE ──────────────────────────────────────────────────────────────────

def launch_web_mode():
    import http.server
    import threading
    import webbrowser

    web_index = os.path.join(SCRIPT_DIR, "web", "index.html")
    if not os.path.exists(web_index):
        print("  Web game files not found. Ensure web/index.html exists.")
        return

    PORT = 8765

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=SCRIPT_DIR, **kwargs)
        def log_message(self, *args):
            pass

    server = http.server.HTTPServer(("", PORT), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    url = f"http://localhost:{PORT}/web/index.html"
    print(f"\n  Wordle web app running at: {url}")
    print("  Press Enter to stop the server and return to the menu.\n")
    webbrowser.open(url)

    try:
        input()
    except (EOFError, KeyboardInterrupt):
        pass
    finally:
        server.shutdown()
        print("  Server stopped.\n")


# ── MAIN MENU ─────────────────────────────────────────────────────────────────

def main():
    words    = load_words()
    word_set = set(words)

    print()
    print("  ========================================")
    print("       WORDLE  -  Choose Your Mode        ")
    print("  ========================================")
    print()
    print("  1. Terminal  (plain text, B/Y/G strings)")
    print("  2. Terminal  (with colours)")
    print("  3. Web       (interactive browser UI)")
    print()

    while True:
        try:
            choice = input("  Enter choice [1/2/3]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Goodbye!\n")
            sys.exit(0)
        if choice == "1":
            run_text_mode(words, word_set)
            break
        elif choice == "2":
            run_colour_mode(words, word_set)
            break
        elif choice == "3":
            launch_web_mode()
            break
        else:
            print("  Please enter 1, 2, or 3.")

    print("\n  Thanks for playing - goodbye!\n")


if __name__ == "__main__":
    main()
