"""
Server launcher script.
Starts all three FastMCP servers as background processes.
"""
import subprocess
import sys
import os
import time
import signal

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable


def start_servers():
    """Start all three FastMCP servers."""
    servers = [
        {
            "name": "EHR MCP Server",
            "module": "backend.ehr_server.ehr_mcp_server",
            "port": 8001,
        },
        {
            "name": "Pharmacy MCP Server",
            "module": "backend.pharmacy_server.pharmacy_mcp_server",
            "port": 8002,
        },
        {
            "name": "Billing MCP Server",
            "module": "backend.billing_server.billing_mcp_server",
            "port": 8003,
        },
    ]

    processes = []
    print("🏥 Starting AI Healthcare Discharge Coordination System")
    print("=" * 60)

    for server in servers:
        print(f"▶️  Starting {server['name']} on port {server['port']}...")
        proc = subprocess.Popen(
            [PYTHON, "-m", server["module"]],
            cwd=BASE_DIR,
        )
        processes.append(proc)
        time.sleep(1)
        print(f"✅ {server['name']} started (PID: {proc.pid})")

    print("=" * 60)
    print(f"\n🚀 Starting FastAPI REST API on port 8000...")
    api_proc = subprocess.Popen(
        [PYTHON, "-m", "uvicorn", "backend.api.main:app",
         "--host", "127.0.0.1", "--port", "8000", "--reload"],
        cwd=BASE_DIR,
    )
    processes.append(api_proc)
    print(f"✅ FastAPI API started (PID: {api_proc.pid})")

    print("\n" + "=" * 60)
    print("📊 All servers are running!")
    print("  EHR MCP:      http://127.0.0.1:8001/mcp")
    print("  Pharmacy MCP: http://127.0.0.1:8002/mcp")
    print("  Billing MCP:  http://127.0.0.1:8003/mcp")
    print("  REST API:     http://127.0.0.1:8000")
    print("  API Docs:     http://127.0.0.1:8000/docs")
    print("=" * 60)
    print("\nPress Ctrl+C to stop all servers.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⛔ Stopping all servers...")
        for proc in processes:
            proc.terminate()
        print("✅ All servers stopped.")


if __name__ == "__main__":
    start_servers()
