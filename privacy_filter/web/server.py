"""
Lightweight Web Application Server for FinTech Privacy Filter.

Serves static UI assets and provides REST API endpoint (/api/process)
connecting the browser frontend to FinTechPrivacyPipeline backend.
"""

import http.server
import json
import socketserver
import sys
from pathlib import Path

# Add project root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from privacy_filter.detectors.pipeline import FinTechPrivacyPipeline

PORT = 8050
WEB_DIR = Path(__file__).resolve().parent

pipeline_engine = FinTechPrivacyPipeline()


class PrivacyFilterHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP Request Handler managing static web assets and REST API endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_POST(self):
        if self.path == "/api/process":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)

            try:
                payload = json.loads(post_data.decode("utf-8"))
                input_text = payload.get("text", "")

                output = pipeline_engine.process(input_text)
                response_json = json.dumps(output.to_dict()).encode("utf-8")

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(response_json)))
                self.end_headers()
                self.write_utf8(response_json)
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                err_msg = json.dumps({"error": str(e)}).encode("utf-8")
                self.write_utf8(err_msg)
        else:
            self.send_error(44, "Not Found")

    def write_utf8(self, data: bytes):
        self.wfile.write(data)


def start_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), PrivacyFilterHTTPRequestHandler) as httpd:
        print(f"==================================================")
        print(f"FINTECH PRIVACY FILTER WEB STUDIO SERVER ACTIVE")
        print(f"==================================================")
        print(f"Server URL: http://localhost:{PORT}")
        print(f"Serving UI from: {WEB_DIR}")
        print("Press Ctrl+C to stop server.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down Web Studio Server.")


if __name__ == "__main__":
    start_server()
