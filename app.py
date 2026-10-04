# -*- coding: utf-8 -*-
"""
 Cloud-Based URL Health Monitoring System
 College Cloud Computing Mini-Project
 Technology Stack: Python | Gradio | Requests | Pandas
"""

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: IMPORTS & CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
import requests
import pandas as pd
import gradio as gr
import time
import os
import csv
import json
from datetime import datetime
from urllib.parse import urlparse

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: IN-MEMORY SESSION STORAGE
# ─────────────────────────────────────────────────────────────────────────────

# Global list to store all monitoring records for the current session
monitoring_history = []

# Column names used throughout the application
COLUMNS = ["URL", "Status Code", "Response Time (ms)", "Status", "Checked At"]

# Default timeout (seconds) for HTTP requests
REQUEST_TIMEOUT = 10

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: CORE URL HEALTH CHECK LOGIC
# ─────────────────────────────────────────────────────────────────────────────

def normalize_url(url: str) -> str:
    """
    Ensures the URL has a proper HTTP/HTTPS scheme.
    If no scheme is detected, 'https://' is prepended automatically.

    Args:
        url (str): Raw URL string entered by the user.

    Returns:
        str: URL with a guaranteed scheme prefix.
    """
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def validate_url(url: str) -> tuple[bool, str]:
    """
    Validates that a URL has the minimum required components (scheme + netloc).

    Args:
        url (str): URL to validate.

    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False, "❌ Invalid URL: Missing scheme or domain."
        return True, ""
    except Exception as e:
        return False, f"❌ URL Parsing Error: {str(e)}"


def check_url_health(url: str) -> dict:
    """
    Performs an HTTP GET request to the target URL and measures:
      - HTTP status code
      - Response time in milliseconds
      - Availability status (Online / Unavailable / Error)

    Args:
        url (str): The URL to probe.

    Returns:
        dict: A result dictionary with keys matching COLUMNS.
    """
    url = normalize_url(url)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    is_valid, error_msg = validate_url(url)
    if not is_valid:
        return {
            "URL": url,
            "Status Code": "N/A",
            "Response Time (ms)": "N/A",
            "Status": f"Error – {error_msg}",
            "Checked At": timestamp,
            "raw_status": "error",
        }

    try:
        start_time = time.time()
        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": "CloudURLHealthMonitor/1.0 (CollegeProject)"},
            allow_redirects=True,
        )
        end_time = time.time()

        response_time_ms = round((end_time - start_time) * 1000, 2)
        status_code = response.status_code

        # Determine human-readable status
        if 200 <= status_code < 400:
            status = "🟢 Online"
            raw_status = "online"
        elif 400 <= status_code < 500:
            status = "🟡 Client Error"
            raw_status = "error"
        elif 500 <= status_code < 600:
            status = "🔴 Server Error"
            raw_status = "unavailable"
        else:
            status = "⚪ Unknown"
            raw_status = "error"

        return {
            "URL": url,
            "Status Code": status_code,
            "Response Time (ms)": response_time_ms,
            "Status": status,
            "Checked At": timestamp,
            "raw_status": raw_status,
        }

    except requests.exceptions.ConnectionError:
        return {
            "URL": url,
            "Status Code": "N/A",
            "Response Time (ms)": "N/A",
            "Status": "🔴 Unavailable – Connection refused",
            "Checked At": timestamp,
            "raw_status": "unavailable",
        }
    except requests.exceptions.Timeout:
        return {
            "URL": url,
            "Status Code": "N/A",
            "Response Time (ms)": f">{REQUEST_TIMEOUT * 1000}",
            "Status": "⏱️ Unavailable – Timed out",
            "Checked At": timestamp,
            "raw_status": "unavailable",
        }
    except requests.exceptions.InvalidURL:
        return {
            "URL": url,
            "Status Code": "N/A",
            "Response Time (ms)": "N/A",
            "Status": "❌ Error – Invalid URL format",
            "Checked At": timestamp,
            "raw_status": "error",
        }
    except requests.exceptions.MissingSchema:
        return {
            "URL": url,
            "Status Code": "N/A",
            "Response Time (ms)": "N/A",
            "Status": "❌ Error – Missing URL schema",
            "Checked At": timestamp,
            "raw_status": "error",
        }
    except Exception as e:
        return {
            "URL": url,
            "Status Code": "N/A",
            "Response Time (ms)": "N/A",
            "Status": f"❌ Error – {str(e)[:80]}",
            "Checked At": timestamp,
            "raw_status": "error",
        }


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: STATISTICS & SUMMARY HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def compute_stats(history: list) -> dict:
    """
    Computes aggregate statistics from the monitoring history.

    Args:
        history (list): List of result dictionaries.

    Returns:
        dict: Statistics including online_count, unavailable_count, total, avg_response.
    """
    total = len(history)
    online = sum(1 for r in history if r.get("raw_status") == "online")
    unavailable = sum(1 for r in history if r.get("raw_status") == "unavailable")
    errors = total - online - unavailable

    # Compute average response time (only for numeric values)
    numeric_times = [
        float(r["Response Time (ms)"])
        for r in history
        if str(r["Response Time (ms)"]).replace(".", "", 1).isdigit()
    ]
    avg_response = round(sum(numeric_times) / len(numeric_times), 2) if numeric_times else 0

    return {
        "total": total,
        "online": online,
        "unavailable": unavailable,
        "errors": errors,
        "avg_response": avg_response,
    }


def build_status_card_html(stats: dict) -> str:
    """
    Generates an HTML snippet for the status summary cards.

    Args:
        stats (dict): Output from compute_stats().

    Returns:
        str: HTML string for the status dashboard cards.
    """
    return f"""
    <div style="display:flex; gap:16px; flex-wrap:wrap; margin:12px 0;">
        <div style="flex:1; min-width:130px; background:linear-gradient(135deg,#22c55e,#16a34a);
                    border-radius:14px; padding:18px 22px; color:#fff; text-align:center;
                    box-shadow:0 4px 15px rgba(34,197,94,0.35);">
            <div style="font-size:28px; font-weight:800; letter-spacing:-1px;">{stats['online']}</div>
            <div style="font-size:12px; font-weight:600; opacity:0.9; text-transform:uppercase; letter-spacing:1px;">🟢 Online</div>
        </div>
        <div style="flex:1; min-width:130px; background:linear-gradient(135deg,#ef4444,#dc2626);
                    border-radius:14px; padding:18px 22px; color:#fff; text-align:center;
                    box-shadow:0 4px 15px rgba(239,68,68,0.35);">
            <div style="font-size:28px; font-weight:800; letter-spacing:-1px;">{stats['unavailable']}</div>
            <div style="font-size:12px; font-weight:600; opacity:0.9; text-transform:uppercase; letter-spacing:1px;">🔴 Unavailable</div>
        </div>
        <div style="flex:1; min-width:130px; background:linear-gradient(135deg,#8b5cf6,#6d28d9);
                    border-radius:14px; padding:18px 22px; color:#fff; text-align:center;
                    box-shadow:0 4px 15px rgba(139,92,246,0.35);">
            <div style="font-size:28px; font-weight:800; letter-spacing:-1px;">{stats['total']}</div>
            <div style="font-size:12px; font-weight:600; opacity:0.9; text-transform:uppercase; letter-spacing:1px;">📊 Total Checks</div>
        </div>
        <div style="flex:1; min-width:130px; background:linear-gradient(135deg,#0ea5e9,#0284c7);
                    border-radius:14px; padding:18px 22px; color:#fff; text-align:center;
                    box-shadow:0 4px 15px rgba(14,165,233,0.35);">
            <div style="font-size:28px; font-weight:800; letter-spacing:-1px;">{stats['avg_response']}</div>
            <div style="font-size:12px; font-weight:600; opacity:0.9; text-transform:uppercase; letter-spacing:1px;">⚡ Avg ms</div>
        </div>
    </div>
    """


def build_result_card_html(result: dict) -> str:
    """
    Generates an HTML card for a single URL check result.

    Args:
        result (dict): A single check result from check_url_health().

    Returns:
        str: Styled HTML card for the latest result.
    """
    raw = result.get("raw_status", "error")
    if raw == "online":
        accent = "#22c55e"
        bg = "rgba(34,197,94,0.08)"
        icon = "✅"
    elif raw == "unavailable":
        accent = "#ef4444"
        bg = "rgba(239,68,68,0.08)"
        icon = "❌"
    else:
        accent = "#f59e0b"
        bg = "rgba(245,158,11,0.08)"
        icon = "⚠️"

    return f"""
    <div style="border:2px solid {accent}; border-radius:16px; padding:20px 24px;
                background:{bg}; margin:10px 0;">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
            <span style="font-size:26px;">{icon}</span>
            <div>
                <div style="font-size:17px; font-weight:700; color:#1e293b; word-break:break-all;">
                    {result['URL']}
                </div>
                <div style="font-size:13px; color:#64748b;">Checked at {result['Checked At']}</div>
            </div>
        </div>
        <div style="display:flex; gap:20px; flex-wrap:wrap;">
            <div style="background:#fff; border-radius:10px; padding:10px 16px;
                        border-left:4px solid {accent}; min-width:110px;">
                <div style="font-size:11px; color:#94a3b8; font-weight:600; text-transform:uppercase;">Status</div>
                <div style="font-size:15px; font-weight:700; color:#1e293b;">{result['Status']}</div>
            </div>
            <div style="background:#fff; border-radius:10px; padding:10px 16px;
                        border-left:4px solid #8b5cf6; min-width:110px;">
                <div style="font-size:11px; color:#94a3b8; font-weight:600; text-transform:uppercase;">HTTP Code</div>
                <div style="font-size:15px; font-weight:700; color:#1e293b;">{result['Status Code']}</div>
            </div>
            <div style="background:#fff; border-radius:10px; padding:10px 16px;
                        border-left:4px solid #0ea5e9; min-width:140px;">
                <div style="font-size:11px; color:#94a3b8; font-weight:600; text-transform:uppercase;">Response Time</div>
                <div style="font-size:15px; font-weight:700; color:#1e293b;">{result['Response Time (ms)']} ms</div>
            </div>
        </div>
    </div>
    """


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5: GRADIO EVENT HANDLERS
# ─────────────────────────────────────────────────────────────────────────────

def handle_check_url(url_input: str):
    """
    Gradio event handler triggered when the user clicks 'Check Website'.

    Performs the URL health check, updates monitoring_history, and returns
    all UI component updates.

    Args:
        url_input (str): Raw URL string from the Gradio Textbox.

    Returns:
        tuple: Updated values for (result_html, stats_html, history_dataframe, status_msg)
    """
    global monitoring_history

    if not url_input or url_input.strip() == "":
        return (
            "<div style='color:#ef4444;padding:12px;background:#fef2f2;border-radius:10px;'>"
            "⚠️ Please enter a URL before clicking Check Website.</div>",
            build_status_card_html(compute_stats(monitoring_history)),
            pd.DataFrame(monitoring_history)[COLUMNS] if monitoring_history else pd.DataFrame(columns=COLUMNS),
            "⚠️ No URL provided.",
        )

    # Support multiple URLs (comma or newline separated)
    raw_urls = [u.strip() for u in url_input.replace("\n", ",").split(",") if u.strip()]

    if len(raw_urls) > 10:
        return (
            "<div style='color:#ef4444;padding:12px;background:#fef2f2;border-radius:10px;'>"
            "⚠️ Maximum 10 URLs can be checked at once.</div>",
            build_status_card_html(compute_stats(monitoring_history)),
            pd.DataFrame(monitoring_history)[COLUMNS] if monitoring_history else pd.DataFrame(columns=COLUMNS),
            "⚠️ Too many URLs.",
        )

    results = []
    for url in raw_urls:
        result = check_url_health(url)
        monitoring_history.append(result)
        results.append(result)

    # Build result cards HTML (latest results shown at top)
    result_html = "".join(build_result_card_html(r) for r in results)

    # Stats overview
    stats = compute_stats(monitoring_history)
    stats_html = build_status_card_html(stats)

    # History dataframe (most recent first)
    history_df = pd.DataFrame(monitoring_history)[COLUMNS].iloc[::-1].reset_index(drop=True)

    status_msg = f"✅ Checked {len(results)} URL(s) successfully at {datetime.now().strftime('%H:%M:%S')}"
    return result_html, stats_html, history_df, status_msg


def handle_clear_history():
    """
    Gradio event handler for the 'Clear History' button.
    Resets the global monitoring_history list.

    Returns:
        tuple: Empty UI state for all output components.
    """
    global monitoring_history
    monitoring_history = []

    empty_html = "<div style='color:#64748b;padding:20px;text-align:center;'>No checks performed yet.</div>"
    return (
        empty_html,
        build_status_card_html(compute_stats([])),
        pd.DataFrame(columns=COLUMNS),
        "🗑️ History cleared.",
    )


def handle_generate_report():
    """
    Generates a CSV report file from the current monitoring history.

    Returns:
        tuple: (file_path_or_None, status_message_str)
    """
    global monitoring_history

    if not monitoring_history:
        return None, "⚠️ No data to export. Please check at least one URL first."

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"url_health_report_{timestamp}.csv"

    # Save to current directory (works in both local and Colab environments)
    df = pd.DataFrame(monitoring_history)[COLUMNS]
    df.to_csv(filename, index=False)

    return filename, f"✅ Report saved as '{filename}' — {len(df)} records exported."


def handle_save_to_drive(drive_folder: str):
    """
    Attempts to save the latest CSV report to Google Drive.
    This function works only when running in Google Colab with Drive mounted.

    Args:
        drive_folder (str): Destination folder path inside Google Drive.

    Returns:
        str: Status message about the save operation.
    """
    global monitoring_history

    if not monitoring_history:
        return "⚠️ No data to save. Please check at least one URL first."

    # Check if Google Drive is mounted (Colab environment)
    drive_root = "/content/drive/MyDrive"
    if not os.path.exists(drive_root):
        return (
            "⚠️ Google Drive not mounted. Run the Drive setup cell in your Colab notebook first.\n"
            "Use: from google.colab import drive; drive.mount('/content/drive')"
        )

    # Build destination path
    folder_name = drive_folder.strip() or "URLHealthMonitor"
    dest_dir = os.path.join(drive_root, folder_name)
    os.makedirs(dest_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"url_health_report_{timestamp}.csv"
    dest_path = os.path.join(dest_dir, filename)

    df = pd.DataFrame(monitoring_history)[COLUMNS]
    df.to_csv(dest_path, index=False)

    return f"☁️ Report saved to Google Drive at:\n{dest_path}\n({len(df)} records)"


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6: GRADIO UI LAYOUT
# ─────────────────────────────────────────────────────────────────────────────

# Custom CSS for a professional monitoring dashboard appearance
CUSTOM_CSS = """
/* ── Global Reset & Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

body, .gradio-container {
    font-family: 'Inter', sans-serif !important;
    background: #f8fafc !important;
}

/* ── Header Banner ── */
.app-header {
    background: linear-gradient(135deg, #6d28d9 0%, #4f46e5 40%, #0ea5e9 100%);
    border-radius: 20px;
    padding: 32px 40px;
    margin-bottom: 24px;
    color: #fff;
    text-align: center;
    box-shadow: 0 8px 32px rgba(109,40,217,0.25);
}

/* ── Input Section Card ── */
.input-card {
    background: #fff;
    border: 1.5px solid #e2e8f0;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin-bottom: 16px;
}

/* ── Primary Button ── */
.btn-primary {
    background: linear-gradient(135deg, #22c55e, #16a34a) !important;
    color: #fff !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    border: none !important;
    font-size: 15px !important;
    letter-spacing: 0.3px !important;
}
.btn-primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(34,197,94,0.4) !important;
}

/* ── Secondary Button ── */
.btn-secondary {
    background: linear-gradient(135deg, #8b5cf6, #6d28d9) !important;
    color: #fff !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    border: none !important;
}
.btn-danger {
    background: linear-gradient(135deg, #ef4444, #dc2626) !important;
    color: #fff !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    border: none !important;
}

/* ── Section Labels ── */
.section-label {
    font-size: 13px;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}

/* ── History Table ── */
.history-table table {
    border-collapse: collapse;
    width: 100%;
}
.history-table th {
    background: linear-gradient(135deg, #6d28d9, #4f46e5);
    color: #fff;
    padding: 10px 14px;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
.history-table td {
    padding: 9px 14px;
    font-size: 13px;
    border-bottom: 1px solid #f1f5f9;
}
.history-table tr:hover td {
    background: #f8f9ff;
}

/* ── Gradio component overrides ── */
.gr-button { transition: all 0.2s ease !important; }
.gr-textbox textarea, .gr-textbox input {
    border-radius: 10px !important;
    border: 1.5px solid #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
}
.gr-textbox textarea:focus, .gr-textbox input:focus {
    border-color: #6d28d9 !important;
    box-shadow: 0 0 0 3px rgba(109,40,217,0.12) !important;
}
"""

HEADER_HTML = """
<div class="app-header">
    <div style="font-size:42px; margin-bottom:8px;">☁️</div>
    <h1 style="margin:0; font-size:30px; font-weight:800; letter-spacing:-0.5px;">
        Cloud URL Health Monitor
    </h1>
    <p style="margin:8px 0 0; font-size:15px; opacity:0.85; font-weight:400;">
        Real-time Website Availability &amp; Response Time Monitoring
    </p>
    <div style="margin-top:14px; display:flex; justify-content:center; gap:14px; flex-wrap:wrap;">
        <span style="background:rgba(255,255,255,0.2); padding:5px 14px; border-radius:20px;
                     font-size:12px; font-weight:600;">⚡ Instant Checks</span>
        <span style="background:rgba(255,255,255,0.2); padding:5px 14px; border-radius:20px;
                     font-size:12px; font-weight:600;">📊 History Tracking</span>
        <span style="background:rgba(255,255,255,0.2); padding:5px 14px; border-radius:20px;
                     font-size:12px; font-weight:600;">📁 CSV Export</span>
        <span style="background:rgba(255,255,255,0.2); padding:5px 14px; border-radius:20px;
                     font-size:12px; font-weight:600;">☁️ Drive Storage</span>
    </div>
</div>
"""

FOOTER_HTML = """
<div style="text-align:center; padding:20px; color:#94a3b8; font-size:12px; margin-top:10px;">
    ☁️ Cloud URL Health Monitor &nbsp;|&nbsp; College Cloud Computing Mini-Project &nbsp;|&nbsp;
    Built with Python · Gradio · Requests · Pandas
</div>
"""


def build_ui() -> gr.Blocks:
    """
    Constructs and returns the complete Gradio Blocks UI for the application.

    Returns:
        gr.Blocks: The fully configured Gradio interface object.
    """
    with gr.Blocks(
        title="Cloud URL Health Monitor",
    ) as demo:

        # ── Header ───────────────────────────────────────────────────────────
        gr.HTML(HEADER_HTML)

        # ── Status Dashboard Cards ────────────────────────────────────────────
        with gr.Row():
            stats_html = gr.HTML(
                value=build_status_card_html(compute_stats([])),
                label="",
            )

        # ── URL Input Section ─────────────────────────────────────────────────
        with gr.Group():
            gr.Markdown(
                "### 🔍 Enter URL(s) to Monitor\n"
                "_Enter one URL or multiple URLs separated by commas. "
                "Maximum 10 URLs per check._"
            )
            with gr.Row():
                url_input = gr.Textbox(
                    placeholder="e.g. https://google.com, github.com, openai.com",
                    label="Website URL(s)",
                    lines=2,
                    max_lines=4,
                    scale=4,
                    elem_id="url-input-box",
                )
                with gr.Column(scale=1, min_width=160):
                    check_btn = gr.Button(
                        "🔍 Check Website",
                        variant="primary",
                        size="lg",
                        elem_classes=["btn-primary"],
                    )
                    clear_btn = gr.Button(
                        "🗑️ Clear History",
                        variant="stop",
                        size="sm",
                        elem_classes=["btn-danger"],
                    )

        # Status message row
        status_msg = gr.Textbox(
            label="Status",
            interactive=False,
            lines=1,
            value="Ready – Enter a URL above to start monitoring.",
            elem_id="status-msg",
        )

        # ── Latest Result Card ────────────────────────────────────────────────
        gr.Markdown("### 📋 Latest Check Result")
        result_html = gr.HTML(
            value="<div style='color:#94a3b8;padding:20px;text-align:center;"
                  "border:2px dashed #e2e8f0;border-radius:14px;'>"
                  "🔍 Results will appear here after you check a URL.</div>"
        )

        # ── Monitoring History Table ──────────────────────────────────────────
        gr.Markdown("### 📜 Monitoring History")
        history_table = gr.Dataframe(
            value=pd.DataFrame(columns=COLUMNS),
            headers=COLUMNS,
            datatype=["str", "str", "str", "str", "str"],
            interactive=False,
            wrap=True,
            elem_classes=["history-table"],
            label="All Checks (Most Recent First)",
        )

        # ── Report Generation Section ─────────────────────────────────────────
        with gr.Accordion("📥 Export & Cloud Storage", open=False):
            gr.Markdown(
                "**Generate a CSV report** of all monitoring results, "
                "or save directly to Google Drive (requires Colab)."
            )
            with gr.Row():
                export_btn = gr.Button(
                    "📥 Download CSV Report",
                    variant="secondary",
                    elem_classes=["btn-secondary"],
                )
                drive_folder_input = gr.Textbox(
                    label="Google Drive Folder Name",
                    placeholder="URLHealthMonitor",
                    value="URLHealthMonitor",
                    scale=2,
                )
                drive_btn = gr.Button(
                    "☁️ Save to Google Drive",
                    variant="secondary",
                    elem_classes=["btn-secondary"],
                )

            report_file = gr.File(label="📁 Download Report", visible=True)
            report_status = gr.Textbox(
                label="Export Status",
                interactive=False,
                lines=2,
                value="",
            )

        # ── How to Use Section ────────────────────────────────────────────────
        with gr.Accordion("ℹ️ How to Use This App", open=False):
            gr.Markdown("""
### 📖 Quick Start Guide

| Step | Action |
|------|--------|
| **1** | Enter one or more website URLs in the input box |
| **2** | Click **Check Website** to start monitoring |
| **3** | View the status, HTTP code, and response time |
| **4** | Repeat for as many URLs as needed |
| **5** | Use **Download CSV Report** to export all results |
| **6** | Use **Save to Google Drive** when running in Google Colab |

### 🌐 Status Indicators

| Icon | Meaning |
|------|---------|
| 🟢 **Online** | Website is reachable (HTTP 2xx/3xx) |
| 🔴 **Unavailable** | Connection refused or timed out |
| 🟡 **Client Error** | HTTP 4xx response (e.g. 404 Not Found) |
| 🔴 **Server Error** | HTTP 5xx response (e.g. 503 Service Unavailable) |
| ⏱️ **Timed Out** | No response within 10 seconds |
| ❌ **Error** | Invalid URL format or DNS failure |

### ☁️ Cloud Computing Concepts Demonstrated
- **Remote HTTP Monitoring** – Checks website health from the cloud
- **Centralized Records** – All checks stored in one session history
- **Cloud Storage** – Export reports to Google Drive
- **Scalability** – Monitor up to 10 URLs simultaneously
            """)

        # ── Footer ────────────────────────────────────────────────────────────
        gr.HTML(FOOTER_HTML)

        # ── Event Wiring ──────────────────────────────────────────────────────
        outputs = [result_html, stats_html, history_table, status_msg]

        check_btn.click(
            fn=handle_check_url,
            inputs=[url_input],
            outputs=outputs,
        )

        # Also allow pressing Enter in the URL textbox
        url_input.submit(
            fn=handle_check_url,
            inputs=[url_input],
            outputs=outputs,
        )

        clear_btn.click(
            fn=handle_clear_history,
            inputs=[],
            outputs=outputs,
        )

        export_btn.click(
            fn=handle_generate_report,
            inputs=[],
            outputs=[report_file, report_status],
        )

        drive_btn.click(
            fn=handle_save_to_drive,
            inputs=[drive_folder_input],
            outputs=[report_status],
        )

    return demo


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7: APPLICATION ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    # Ensure UTF-8 output on Windows terminals
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 60)
    print("  Cloud URL Health Monitor")
    print("  College Cloud Computing Mini-Project")
    print("=" * 60)
    print("Starting Gradio interface...")
    print("Open the URL printed below in your browser.\n")

    app = build_ui()
    app.launch(
        server_name="0.0.0.0",   # Listen on all interfaces (needed for Colab)
        server_port=None,         # Let Gradio auto-select an available port
        share=False,             # Set to True to get a public Gradio link
        show_error=True,
        quiet=False,
        css=CUSTOM_CSS,
        theme=gr.themes.Base(
            primary_hue=gr.themes.colors.purple,
            secondary_hue=gr.themes.colors.green,
            neutral_hue=gr.themes.colors.slate,
            font=gr.themes.GoogleFont("Inter"),
        ),
    )
