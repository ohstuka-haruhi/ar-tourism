#!/usr/bin/env python3
"""Development server for AR Tourism Guide.
Serves static files and accepts PUT /spots.json and POST /routes.json.

Usage:
    python3 server.py          # port 8080
    python3 server.py 3000     # custom port
"""
import json
import os
import re
import secrets
import sys
import urllib.request
import urllib.error
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = int(os.environ.get('PORT', sys.argv[1] if len(sys.argv) > 1 else 8080))
SPOTS_FILE      = 'spots.json'
ROUTES_FILE     = 'routes.json'
ANALYTICS_FILE  = 'analytics.json'
QR_DIR          = 'qr'
COMPILED_DIR    = 'compiled'


class Handler(SimpleHTTPRequestHandler):

    # ── CORS headers on every response ──────────────────────
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, PUT, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    # ── GET /analytics → return analytics.json ──────────────
    def do_GET(self):
        if self.path.rstrip('/') == '/analytics':
            self._get_analytics()
        else:
            super().do_GET()

    def _get_analytics(self):
        try:
            with open(ANALYTICS_FILE, 'r', encoding='utf-8') as f:
                body = f.read().encode('utf-8')
        except FileNotFoundError:
            body = b'[]'
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(body)

    # ── PUT /spots.json  or  PUT /qr/<id>.png ───────────────
    def do_PUT(self):
        if self.path.rstrip('/') == '/' + SPOTS_FILE:
            self._put_spots()
        elif re.fullmatch(r'/qr/[a-zA-Z0-9_\-]+\.png', self.path):
            self._put_qr()
        elif re.fullmatch(r'/compiled/[a-zA-Z0-9_\-]+\.mind', self.path):
            self._put_compiled()
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"error":"not found"}')

    def _put_spots(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body   = self.rfile.read(length)
            spots  = json.loads(body)

            if not isinstance(spots, list):
                raise ValueError('Payload must be a JSON array')

            with open(SPOTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(spots, f, ensure_ascii=False, indent=2)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True, 'count': len(spots)}).encode())

        except (json.JSONDecodeError, ValueError) as e:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
        except OSError as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def _put_compiled(self):
        try:
            os.makedirs(COMPILED_DIR, exist_ok=True)
            length   = int(self.headers.get('Content-Length', 0))
            body     = self.rfile.read(length)
            filepath = os.path.normpath(self.path.lstrip('/'))
            if not filepath.startswith(COMPILED_DIR + os.sep):
                raise ValueError('Invalid path')
            with open(filepath, 'wb') as f:
                f.write(body)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True}).encode())
        except (ValueError, OSError) as e:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def _put_qr(self):
        try:
            os.makedirs(QR_DIR, exist_ok=True)
            length = int(self.headers.get('Content-Length', 0))
            body   = self.rfile.read(length)
            if body[:4] != b'\x89PNG':
                raise ValueError('Not a valid PNG file')
            filepath = self.path.lstrip('/')          # e.g. "qr/abc123.png"
            filepath = os.path.normpath(filepath)
            if not filepath.startswith(QR_DIR + os.sep):
                raise ValueError('Invalid path')
            with open(filepath, 'wb') as f:
                f.write(body)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True}).encode())
        except (ValueError, OSError) as e:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    # ── POST /routes.json or /analytics ─────────────────────
    def do_POST(self):
        path = self.path.rstrip('/')
        if path == '/analytics':
            self._post_analytics()
        elif path == '/api/analyze':
            self._post_analyze()
        elif path == '/' + ROUTES_FILE:
            self._post_route()
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"error":"not found"}')

    def _post_analyze(self):
        """POST /api/analyze — vision-based road/direction analysis via Claude."""
        DEFAULT = json.dumps({
            "direction": "straight",
            "confidence": 0.5,
            "road_detected": False,
            "description": "解析不可"
        }).encode()

        def respond(data: bytes):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(data)

        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            print('  \033[33m⚠  /api/analyze: ANTHROPIC_API_KEY not set\033[0m')
            respond(DEFAULT)
            return

        try:
            length     = int(self.headers.get('Content-Length', 0))
            body       = json.loads(self.rfile.read(length))
            image_b64  = body.get('image', '')
            if not image_b64:
                raise ValueError('image field missing')

            prompt = (
                '以下の画像（カメラ映像の1フレーム）を解析し、'
                '歩行者の進行方向を判断してください。\n'
                '回答はJSONのみ（説明不要）:\n'
                '{"direction":"straight"|"left"|"right"|"arrived",'
                '"confidence":0.0-1.0,'
                '"road_detected":true|false,'
                '"description":"10文字以内の日本語"}\n'
                'direction定義: straight=直進, left=左折推奨, '
                'right=右折推奨, arrived=目的地付近\n'
                'confidence: 判断の確信度\n'
                'description: 状況の短い説明（例: 直進可能, 左に道あり）'
            )

            payload = json.dumps({
                "model": "claude-sonnet-4-6",
                "max_tokens": 150,
                "messages": [{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_b64
                            }
                        },
                        {"type": "text", "text": prompt}
                    ]
                }]
            }).encode()

            req = urllib.request.Request(
                'https://api.anthropic.com/v1/messages',
                data=payload,
                headers={
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01',
                    'content-type': 'application/json'
                },
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=20) as resp:
                result = json.loads(resp.read())

            raw = result['content'][0]['text'].strip()

            # JSON を抽出（余分なテキストに対して堅牢に）
            m = re.search(r'\{[^{}]+\}', raw, re.DOTALL)
            parsed = json.loads(m.group() if m else raw)

            # フィールドを検証・サニタイズ
            direction = parsed.get('direction', 'straight')
            if direction not in ('straight', 'left', 'right', 'arrived'):
                direction = 'straight'
            confidence  = max(0.0, min(1.0, float(parsed.get('confidence', 0.5))))
            road_detected = bool(parsed.get('road_detected', False))
            description   = str(parsed.get('description', ''))[:10]

            out = json.dumps({
                "direction":    direction,
                "confidence":   round(confidence, 3),
                "road_detected": road_detected,
                "description":  description
            }).encode()
            respond(out)

        except Exception as e:
            print(f'  \033[31m✗  /api/analyze error: {e}\033[0m')
            respond(DEFAULT)   # エラー時は straight をデフォルト返却

    def _post_analytics(self):
        try:
            length  = int(self.headers.get('Content-Length', 0))
            payload = json.loads(self.rfile.read(length))
            sid     = payload.get('sessionId', '')

            try:
                with open(ANALYTICS_FILE, 'r', encoding='utf-8') as f:
                    sessions = json.load(f)
                if not isinstance(sessions, list):
                    sessions = []
            except (FileNotFoundError, json.JSONDecodeError):
                sessions = []

            found = next((s for s in sessions if s.get('sessionId') == sid), None)
            if found:
                found['events'] = found.get('events', []) + payload.get('events', [])
                if payload.get('endTime'):
                    found['endTime'] = payload['endTime']
                found['lang'] = payload.get('lang', found.get('lang'))
            else:
                sessions.append(payload)

            with open(ANALYTICS_FILE, 'w', encoding='utf-8') as f:
                json.dump(sessions, f, ensure_ascii=False, separators=(',', ':'))

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def _post_route(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            route  = json.loads(self.rfile.read(length))
            if not isinstance(route, dict):
                raise ValueError('Payload must be a JSON object')
            try:
                with open(ROUTES_FILE, 'r', encoding='utf-8') as f:
                    routes = json.load(f)
                if not isinstance(routes, list):
                    routes = []
            except (FileNotFoundError, json.JSONDecodeError):
                routes = []
            route['id'] = secrets.token_hex(6)
            routes.append(route)
            with open(ROUTES_FILE, 'w', encoding='utf-8') as f:
                json.dump(routes, f, ensure_ascii=False, indent=2)
            self.send_response(201)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True, 'id': route['id']}).encode())
        except (json.JSONDecodeError, ValueError) as e:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
        except OSError as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    # ── Quiet log: only show writes and errors ───────────────
    def log_message(self, fmt, *args):
        line = fmt % args
        code = args[1] if len(args) > 1 else ''
        if args and (args[0].startswith('PUT') or args[0].startswith('POST')):
            print(f'  \033[32m💾 {line}\033[0m')
        elif str(code).startswith(('4', '5')):
            print(f'  \033[31m✗  {line}\033[0m')
        else:
            super().log_message(fmt, *args)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    httpd = HTTPServer(('', PORT), Handler)
    print(f'\033[36m⛩  AR Tourism server\033[0m  →  http://localhost:{PORT}')
    print(f'   AR viewer : http://localhost:{PORT}')
    print(f'   Admin     : http://localhost:{PORT}/admin.html')
    print(f'   Routes    : http://localhost:{PORT}/routes.json')
    print(f'   AR Marker : http://localhost:{PORT}/ar-marker.html?id=SPOT_ID')
    print(f'   Analytics : http://localhost:{PORT}/analytics')
    print('   Press Ctrl+C to stop.\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nServer stopped.')
