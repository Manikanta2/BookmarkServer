from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, unquote
import requests
import os

form = '''<!DOCTYPE html>
<title>Bookmark Server</title>
<form method="POST">
    <label>Long URI:
        <input name="longuri">
    </label>
    <br>
    <label>Short name:
        <input name="shortname">
    </label>
    <br>
    <button type="submit">Save it!</button>
</form>
<p>URIs I know about:
<pre>
{}
</pre>
'''

memory = {}


def Check_URI(uri, timeout=5):
    try:
        r = requests.get(uri, timeout=timeout)
        return r.status_code
    except requests.RequestException:
        return False


class MessageHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        name = unquote(self.path[1:])

        if name:
            if name in memory:
                self.send_response(303)
                self.send_header('Location', memory[name])
                self.end_headers()
            else:
                self.send_response(404)
                self.send_header('content-type', 'text/plain; charset-utf-8')
                self.end_headers()
                self.wfile.write("There is no URI with name {}".format(name).encode())
        else:
            self.send_response(200)
            self.send_header('content-type', 'text/html; charset-utf-8')
            self.end_headers()
            known = "\n".join('{} : {}'.format(key, memory[key])
                            for key in sorted(memory.keys()))
            print(known)
            self.wfile.write(form.format(known).encode())
    def do_POST(self):

        length = int(self.headers.get('content-length', 0))
        body = self.rfile.read(length).decode()
        params = parse_qs(body)


        if "longuri" not in params or "shortname" not in params:
            self.send_response(400)
            self.send_header('content-type', 'text/plain; charset-utf-8')
            self.end_headers()
            self.wfile.write("Missing form fields".encode())

        longuri = params["longuri"][0]
        shortname = params["shortname"][0]

        if Check_URI(longuri):

            memory[shortname] = longuri
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
        else:
            # Didn't successfully fetch the long URI.
            self.send_response(404)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(
                "Couldn't fetch URI '{}'. Sorry!".format(longuri).encode())



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    server_address = ('', port)
    httpd = HTTPServer(server_address, MessageHandler)
    httpd.serve_forever()


