# ☁️ Cloud URL Health Monitor

> **College Cloud Computing Mini-Project**  
> A professional, cloud-native website availability and response-time monitoring system built with Python, Gradio, Requests, and Pandas.

---

## 📌 Project Overview

The **Cloud URL Health Monitor** is a real-time web application that enables users to check the availability and performance of any website. It demonstrates core **Cloud Computing concepts** such as remote service monitoring, centralized data collection, and cloud-based report storage via Google Drive.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 URL Health Check | Sends HTTP GET requests to check website availability |
| ⚡ Response Time | Measures and displays response time in milliseconds |
| 📊 Status Codes | Shows HTTP status codes (200, 404, 503, etc.) |
| 🟢 Visual Indicators | Color-coded Online / Unavailable / Error status |
| 📜 Monitoring History | Maintains a full session history in a table |
| 🔗 Multi-URL Support | Check up to 10 URLs simultaneously |
| 📥 CSV Export | Download a complete monitoring report as CSV |
| ☁️ Google Drive Storage | Save reports directly to Google Drive (Colab) |
| 🗑️ Clear History | Reset the session with one click |
| 📱 Responsive Design | Works on desktop and mobile browsers |

---

## 🛠️ Technology Stack

| Technology | Role |
|-----------|------|
| **Python 3.9+** | Core programming language |
| **Gradio** | Interactive web UI framework |
| **Requests** | HTTP client for URL health checking |
| **Pandas** | Data handling and CSV report generation |
| **Google Colab** | Cloud-based development and execution |
| **Google Drive** | Cloud storage for monitoring reports |

---

## ☁️ Cloud Computing Concepts Demonstrated

1. **Remote HTTP Monitoring** – Checks website health from the cloud without local network bias  
2. **Centralized Records** – All checks aggregated in a single monitoring dashboard  
3. **Cloud-based Storage** – Reports persisted to Google Drive  
4. **Scalability** – Supports concurrent multi-URL monitoring  
5. **Availability Metrics** – Uptime tracking with response-time measurement  

---

## 📁 Project Structure

```
url-health-monitor/
├── app.py                          # Main application (Gradio UI + logic)
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation (this file)
└── Cloud_URL_Health_Monitor.ipynb  # Google Colab notebook
```

---

## 🚀 Setup & Installation

### Option A – Run Locally (Recommended for Testing)

#### Prerequisites
- Python 3.9 or higher
- pip package manager

#### Steps

```bash
# 1. Clone or download the project
cd url-health-monitor

# 2. (Optional) Create a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

5. Open your browser at: **http://localhost:7860**

---

### Option B – Run on Google Colab (Cloud Execution)

1. Open [Google Colab](https://colab.research.google.com/)
2. Upload `Cloud_URL_Health_Monitor.ipynb`
3. Run each cell in order:
   - **Cell 1**: Install dependencies
   - **Cell 2**: Import libraries
   - **Cell 3**: Load application code
   - **Cell 4**: Mount Google Drive (optional)
   - **Cell 5**: Launch the Gradio interface
4. Click the **public Gradio link** that appears after Cell 5

> **Tip:** Set `share=True` in the `demo.launch()` call to get a public URL accessible from any device.

---

## 📖 How to Use the Application

| Step | Action |
|------|--------|
| **1** | Enter a website URL (e.g., `https://google.com`) |
| **2** | Click **🔍 Check Website** |
| **3** | View the result card with Status, HTTP Code, and Response Time |
| **4** | Check multiple URLs by separating with commas |
| **5** | Scroll down to view full monitoring history |
| **6** | Click **📥 Download CSV Report** to export results |
| **7** | Click **☁️ Save to Google Drive** to store in the cloud |

---

## 🌐 Status Indicators

| Icon | Status | Meaning |
|------|--------|---------|
| 🟢 | **Online** | HTTP 200–399 – Website is healthy |
| 🟡 | **Client Error** | HTTP 400–499 – Page not found / forbidden |
| 🔴 | **Server Error** | HTTP 500–599 – Server-side issue |
| ⏱️ | **Timed Out** | No response within 10 seconds |
| ❌ | **Error** | Invalid URL or DNS failure |

---

## 📊 Sample CSV Report

```csv
URL,Status Code,Response Time (ms),Status,Checked At
https://google.com,200,142.5,🟢 Online,2024-01-15 10:30:45
https://github.com,200,231.8,🟢 Online,2024-01-15 10:30:47
https://example-broken.com,N/A,N/A,🔴 Unavailable,2024-01-15 10:30:49
```

---

## ⚙️ Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `REQUEST_TIMEOUT` | `10` sec | HTTP request timeout |
| Max URLs per check | `10` | Maximum simultaneous URL checks |
| Drive folder | `URLHealthMonitor` | Default Google Drive save folder |
| Server port | `7860` | Gradio server port |

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Port 7860 in use | Change `server_port` in `app.py` |
| Google Drive not mounting | Run the Drive cell in Colab first |
| URL shows "Error – Connection" | Check internet connection or firewall |
| Gradio public URL not working | Set `share=True` in `app.launch()` |

---

## 👨‍💻 Development Notes

- The application uses **session-based in-memory storage** — history resets when the server restarts.
- All HTTP requests include a custom `User-Agent` header to identify the monitoring tool.
- The `normalize_url()` function automatically prepends `https://` if no scheme is present.
- Error handling covers: connection errors, DNS failures, timeouts, invalid URLs, and HTTP errors.

---

## 📄 License

This project is created for educational purposes as part of a **College Cloud Computing Mini-Project**.  
Free to use, modify, and distribute for academic use.

---

*Built with ❤️ using Python · Gradio · Requests · Pandas*
