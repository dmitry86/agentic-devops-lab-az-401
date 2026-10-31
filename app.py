from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from html import escape
import json
import os


class StatusService(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            status = 200
            content_type = "application/json"
            body = json.dumps({"status": "healthy"}).encode()

        elif self.path == "/ready":
            if os.environ.get("MAINTENANCE_MODE") == "true":
                status = 503
                body = json.dumps({"status": "not_ready"}).encode()
            else:
                status = 200
                body = json.dumps({"status": "ready"}).encode()
            content_type = "application/json"

        elif self.path == "/":
            status = 200
            content_type = "text/html; charset=utf-8"
            version = escape(os.environ.get("APP_VERSION", "development"), quote=True)
            body = f"""<!doctype html>
                <html lang="en">
                <head>
                  <meta charset="utf-8">
                  <meta name="viewport" content="width=device-width, initial-scale=1">
                  <title>CloudOps Status</title>
                  <style>
                    :root {{
                      color-scheme: light;
                      font-family: Inter, ui-sans-serif, system-ui, sans-serif;
                      color: #172033;
                      background: #f3f6fb;
                    }}
                    * {{ box-sizing: border-box; }}
                    body {{ margin: 0; min-height: 100vh; }}
                    main {{ width: min(920px, calc(100% - 32px)); margin: 0 auto; padding: 64px 0; }}
                    .eyebrow {{ color: #52627a; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; }}
                    h1 {{ margin: 10px 0 8px; font-size: clamp(2rem, 5vw, 3rem); }}
                    .intro {{ margin: 0; color: #52627a; }}
                    .lab-label {{ display: inline-block; margin-top: 20px; padding: 7px 11px; border-radius: 999px; background: #e8efff; color: #244b9b; font-size: 0.85rem; font-weight: 700; }}
                    .dashboard {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 16px; margin-top: 32px; }}
                    .card {{ min-height: 142px; padding: 22px; border: 1px solid #e0e6ef; border-radius: 14px; background: #fff; box-shadow: 0 4px 16px rgb(23 32 51 / 5%); }}
                    .card h2 {{ margin: 0 0 16px; color: #52627a; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }}
                    .value {{ margin: 0; font-size: 1.35rem; font-weight: 700; overflow-wrap: anywhere; }}
                    .pending {{ color: #52627a; }}
                    .ready {{ color: #16794b; }}
                    .not-ready {{ color: #a33b2f; }}
                    .maintenance {{ color: #a33b2f; }}
                    .footnote {{ margin-top: 28px; color: #52627a; font-size: 0.9rem; }}
                    a {{ color: #244b9b; }}
                  </style>
                </head>
                <body>
                  <main>
                    <p class="eyebrow">Operations dashboard</p>
                    <h1>CloudOps Status</h1>
                    <p class="intro">A simple view of application readiness and release information.</p>
                    <span class="lab-label">Learning lab</span>
                    <section class="dashboard" aria-label="Application status">
                      <article class="card">
                        <h2>Application</h2>
                        <p class="value">CloudOps Status</p>
                      </article>
                      <article class="card">
                        <h2>Readiness</h2>
                        <p id="readiness-status" class="value pending" role="status" aria-live="polite">Checking...</p>
                      </article>
                      <article class="card">
                        <h2>Maintenance</h2>
                        <p id="maintenance-status" class="value pending">Checking...</p>
                      </article>
                      <article class="card">
                        <h2>Release version</h2>
                        <p class="value">{version}</p>
                      </article>
                    </section>
                    <p class="footnote">Readiness is checked from <a href="/ready">/ready</a>. <a href="/health">Health endpoint</a>.</p>
                  </main>
                  <script>
                    async function updateReadiness() {{
                      const readinessElement = document.getElementById("readiness-status");
                      const maintenanceElement = document.getElementById("maintenance-status");
                      try {{
                        const response = await fetch("/ready", {{ cache: "no-store" }});
                        const readiness = await response.json();
                        if (readiness.status === "ready") {{
                          readinessElement.textContent = "Ready";
                          readinessElement.className = "value ready";
                          maintenanceElement.textContent = "Inactive";
                          maintenanceElement.className = "value";
                        }} else if (readiness.status === "not_ready") {{
                          readinessElement.textContent = "Not ready";
                          readinessElement.className = "value not-ready";
                          maintenanceElement.textContent = "Active";
                          maintenanceElement.className = "value maintenance";
                        }} else {{
                          readinessElement.textContent = "Unavailable";
                          readinessElement.className = "value not-ready";
                          maintenanceElement.textContent = "Unknown";
                          maintenanceElement.className = "value pending";
                        }}
                      }} catch (error) {{
                        readinessElement.textContent = "Unavailable";
                        readinessElement.className = "value not-ready";
                        maintenanceElement.textContent = "Unknown";
                        maintenanceElement.className = "value pending";
                      }}
                    }}
                    updateReadiness();
                    window.setInterval(updateReadiness, 30000);
                  </script>
                </body>
                </html>
            """.encode()

        else:
            status = 404
            content_type = "text/plain"
            body = b"Not found"

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8080), StatusService)
    print("Open http://localhost:8080")
    server.serve_forever()
