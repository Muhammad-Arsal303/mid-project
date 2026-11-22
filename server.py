"""
server.py - Python HTTP Server & JSON REST API for Klondike Solitaire
CSC200 Data Structures & Algorithms | Mid Term Project

Bridges the Python Game Engine with the Tekken 8 Themed Graphical User Interface.
Runs locally using Python's standard library (http.server). Zero external dependencies.
"""

import sys
import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game import KlondikeGame

# Shared game session instance
GAME_SESSION = KlondikeGame(draw_mode=1)
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')


class SolitaireRequestHandler(SimpleHTTPRequestHandler):
    """Handles static web assets and REST API endpoints for Klondike Solitaire."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def _send_json(self, data: Dict[str, Any], status: int = 200) -> None:
        """Sends JSON payload with standard CORS and cache headers."""
        payload = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self) -> None:
        """Handles CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self) -> None:
        """Routes GET requests to API or serves static files."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/state':
            self._send_json(GAME_SESSION.to_dict())
            return
        elif path == '/api/hint':
            self._send_json(GAME_SESSION.get_hint())
            return

        super().do_GET()

    def do_POST(self) -> None:
        """Routes POST API calls to KlondikeGame logic methods."""
        parsed = urlparse(self.path)
        path = parsed.path

        # Read JSON body if present
        content_len = int(self.headers.get('Content-Length', 0))
        body = {}
        if content_len > 0:
            try:
                body = json.loads(self.rfile.read(content_len).decode('utf-8'))
            except Exception:
                body = {}

        if path == '/api/new_game':
            draw_mode = int(body.get('drawMode', 1))
            seed = body.get('seed', None)
            if seed is not None:
                try:
                    seed = int(seed)
                except ValueError:
                    seed = None
            GAME_SESSION.new_game(seed=seed, draw_mode=draw_mode)
            self._send_json(GAME_SESSION.to_dict())

        elif path == '/api/draw':
            GAME_SESSION.draw()
            self._send_json(GAME_SESSION.to_dict())

        elif path == '/api/move_tableau':
            src = int(body.get('src', 0))
            dst = int(body.get('dst', 0))
            count = int(body.get('count', 1))
            GAME_SESSION.move_tableau_to_tableau(src, dst, count)
            self._send_json(GAME_SESSION.to_dict())

        elif path == '/api/foundation':
            # Can be called by cardId (double click) or source specifier
            if 'cardId' in body:
                GAME_SESSION.auto_foundation_card(int(body['cardId']))
            elif body.get('source') == 'WASTE':
                GAME_SESSION.move_waste_to_foundation()
            elif body.get('source') == 'TABLEAU':
                src_idx = int(body.get('srcIdx', 0))
                GAME_SESSION.move_tableau_to_foundation(src_idx)
            self._send_json(GAME_SESSION.to_dict())

        elif path == '/api/waste_to_tableau':
            dst = int(body.get('dst', 0))
            GAME_SESSION.move_waste_to_tableau(dst)
            self._send_json(GAME_SESSION.to_dict())

        elif path == '/api/foundation_to_tableau':
            f_idx = int(body.get('fIdx', 0))
            dst = int(body.get('dst', 0))
            GAME_SESSION.move_foundation_to_tableau(f_idx, dst)
            self._send_json(GAME_SESSION.to_dict())

        elif path == '/api/undo':
            GAME_SESSION.undo()
            self._send_json(GAME_SESSION.to_dict())

        elif path == '/api/redo':
            GAME_SESSION.redo()
            self._send_json(GAME_SESSION.to_dict())

        elif path == '/api/auto_complete':
            GAME_SESSION.auto_complete()
            self._send_json(GAME_SESSION.to_dict())

        elif path == '/api/command':
            cmd_text = body.get('command', '')
            GAME_SESSION.execute_command(cmd_text)
            self._send_json(GAME_SESSION.to_dict())

        else:
            self._send_json({'error': f"Unknown endpoint: {path}"}, status=404)


def start_server(port: int = 8080) -> None:
    """Launches local HTTP server on specified port."""
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, SolitaireRequestHandler)
    print(f"\n============================================================================")
    print(f" [TK8 HUD] Klondike Solitaire Engine Server Running at http://127.0.0.1:{port}")
    print(f" Press Ctrl+C in this console to stop the server.")
    print(f"============================================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Solitaire Server...")
        httpd.server_close()


if __name__ == '__main__':
    port = 8080
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    start_server(port)
