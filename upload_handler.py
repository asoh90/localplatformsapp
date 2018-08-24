import re
import sys
import os
import json
from http.server import SimpleHTTPRequestHandler, HTTPServer

class FileUploadHTTPRequestHandler(SimpleHTTPRequestHandler):
    # A HTTP Server that accepts POST requests and savest hem as files in the same folder as this script

    protocol_version = "HTTP/1.1"

    def do_POST(self):
        # Handle a POST request
        wasSuccess, file_uploaded = self.handle_file_uploads()

        # Compose a response to the client
        response_obj = {
            "wasSuccess": wasSuccess,
            "files_uploaded": files_uploaded,
            "client_address": self.client_address
        }

        response_str = json.dumps(response_obj)

        self.log_message(response_str)

        # Send our response code, header, and data
        self.send_response(200)
        self.send_header("Content-type", "Application/json")
        self.send_header("Content-Length", len(response_str))
        self.end_headers()
        self.wfile.write(response_str.encode('utf-8'))

    def read_line(self):
        line_str = self.rfile.readline(.decode('utf-8'))