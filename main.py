"""
main.py - Klondike Solitaire Main Entry Point
CSC200 Data Structures & Algorithms | Mid Term Project

Usage:
  python main.py          (Interactive launcher menu)
  python main.py --cli    (Run text console interface)
  python main.py --gui    (Launch Tekken 8 Themed Graphical Interface)
  python main.py --test   (Run complete 22-test automated validation suite)
"""

import sys
import os
import webbrowser
import threading
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ui import ConsoleUI
from server import start_server


def run_tests() -> None:
    """Executes the complete test suite covering all 22 test cases."""
    print("\n" + "=" * 76)
    print(" EXECUTING CSC200 KLONDIKE SOLITAIRE TEST SUITE (TC-01 TO TC-22)")
    print("=" * 76 + "\n")

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=os.path.dirname(os.path.abspath(__file__)), pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 76)
    print(f" TESTS RUN: {result.testsRun} | SUCCESSFUL: {result.wasSuccessful()} | FAILURES: {len(result.failures)} | ERRORS: {len(result.errors)}")
    print("=" * 76 + "\n")
    if not result.wasSuccessful():
        sys.exit(1)


def launch_gui(port: int = 8080) -> None:
    """Starts local server and opens browser to the GUI."""
    url = f"http://127.0.0.1:{port}"
    print(f"Launching Tekken 8 Style Klondike Solitaire HUD at: {url} ...")

    def open_browser():
        import time
        time.sleep(0.8)
        webbrowser.open(url)

    t = threading.Thread(target=open_browser, daemon=True)
    t.start()

    start_server(port=port)


def launch_cli() -> None:
    """Starts interactive console UI."""
    ui = ConsoleUI()
    ui.start_loop()


def show_menu() -> None:
    """Displays interactive launcher menu when invoked without arguments."""
    while True:
        print("\n" + "=" * 64)
        print("    KLONDIKE SOLITAIRE // TEKKEN 8 THEMED HUD - CSC200 DSA")
        print("=" * 64)
        print("  [1] Launch 'Tekken 8 Themed' Graphical Interface (GUI)")
        print("  [2] Launch Text-Based Console Interface (CLI)")
        print("  [3] Run Automated Validation Test Suite (TC-01 to TC-22)")
        print("  [4] Exit")
        print("=" * 64)

        try:
            choice = input("Select an option (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting. Goodbye!")
            break

        if choice == '1':
            launch_gui()
            break
        elif choice == '2':
            launch_cli()
            break
        elif choice == '3':
            run_tests()
            input("Press Enter to return to menu...")
        elif choice == '4':
            print("\nExiting. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please enter 1, 2, 3, or 4.")


def main():
    args = sys.argv[1:]
    if not args:
        show_menu()
    elif '--cli' in args or '-c' in args:
        launch_cli()
    elif '--gui' in args or '-g' in args:
        port = 8080
        for i, a in enumerate(args):
            if a in ('--port', '-p') and i + 1 < len(args) and args[i + 1].isdigit():
                port = int(args[i + 1])
        launch_gui(port=port)
    elif '--test' in args or '-t' in args:
        run_tests()
    else:
        print(f"Unknown argument: {' '.join(args)}")
        print("Usage: python main.py [--cli | --gui | --test]")
        sys.exit(1)


if __name__ == '__main__':
    main()
