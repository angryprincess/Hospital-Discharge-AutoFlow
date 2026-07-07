# 🏥 How to Run the AI Healthcare Discharge System

Welcome! This guide is written to help you start and test the Healthcare AI Discharge Coordination system on your computer. Just follow these steps in order.

---

## 🛠️ Phase 1: Setup the Environment (First Time Only)

These steps ensure your computer has the correct packages and dependencies installed to run the AI system.

1. **Open your Terminal** (Command Prompt or PowerShell on Windows, Terminal on macOS/Linux).
2. **Navigate to the `Healthcare_Discharge_System` folder** by typing:
   ```bash
   cd path/to/Project5-v11/Healthcare_Discharge_System
   ```
   *(Replace `path/to` with the actual folder path where you extracted the project).*
3. **Create a Python Virtual Environment** (a safe, isolated space for the project's files):
   ```bash
   python -m venv venv
   ```
4. **Activate the Environment:**
   * **On Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
     *(If you get a script execution policy error, you can run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` first in your PowerShell, or use the Command Prompt instructions).*
   * **On Windows (Command Prompt):**
     ```cmd
     .\venv\Scripts\activate.bat
     ```
   * **On macOS / Linux:**
     ```bash
     source venv/bin/activate
     ```
   *(You should now see `(venv)` at the beginning of your terminal command prompt line).*
5. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```
   *Wait for the download and installation to complete.*

---

## 🚀 Phase 2: Start the Project Servers

The project runs on two servers: one for the AI backend (FastAPI + FastMCP servers), and one for the frontend Dashboard.

### Step A: Start the AI Backend Server
1. Make sure you are still in your first terminal window with the virtual environment `(venv)` active and inside the `Healthcare_Discharge_System` directory.
2. Run the server launcher script:
   * **On Windows (PowerShell - recommended for correct emoji display):**
     ```powershell
     $env:PYTHONIOENCODING="utf-8"; python run_servers.py
     ```
   * **On Windows (Command Prompt) / macOS / Linux:**
     ```bash
     python run_servers.py
     ```
3. You will see terminal output confirming that the EHR, Pharmacy, Billing, and FastAPI REST API servers have successfully started. **Leave this terminal window open.**

### Step B: Start the Web Dashboard
1. Open a **second, brand new Terminal window**.
2. **Navigate specifically to the `web_dashboard` subdirectory**:
   ```bash
   cd path/to/Project5-v11/Healthcare_Discharge_System/web_dashboard
   ```
   > [!IMPORTANT]
   > You **must** run the dashboard web server from inside the `web_dashboard` folder itself. If you run it from the root `Healthcare_Discharge_System` directory, the browser will display a listing of project files instead of loading the dashboard interface.
   
3. Start the dashboard web server:
   ```bash
   python -m http.server 8080
   ```
4. **Leave this terminal window open as well.**

---

## 💻 Phase 3: Test the Dashboard!

Now that both servers are running behind the scenes, you can interact with the AI discharge coordinator!

1. Open your favorite web browser (Chrome, Edge, Firefox, Safari, etc.).
2. Go to: **[http://localhost:8080](http://localhost:8080)**
3. The AI Healthcare Discharge Coordination Dashboard will load!
4. **How to test:** 
   - Click on **Ravi Kumar (P001)** and hit "Initiate Discharge". You will see the AI coordinate with the EHR, resolve drug brands, check inventory (noting that Metformin is out of stock), automatically suggest a safe alternative medication (Glipizide), run allergy checks, generate a validated invoice, and output a complete discharge packet!
   - Click on **Anita Desai (P002)** and hit "Initiate Discharge" to watch the AI validate her post-op recovery prescriptions, generate her invoice, and successfully clear her for discharge.
   - Click on **Sunita Patel (P004)** to witness a successful discharge with a low-stock warning detected for her supplement medicine.

---

## 🧪 Phase 4: Run the Automated Test Suite (Optional)

If you want to run the complete test suite verifying the 13 required scenarios (including role-based access control, allergy block rules, and invoice validation):

1. Open a terminal with your virtual environment `(venv)` active and navigate to the root `Healthcare_Discharge_System` directory.
2. Run the test suite:
   ```bash
   python -m pytest -v
   ```
3. All 17 unit tests should compile and pass successfully.

---

## 🛑 Phase 5: How to Stop the Project

When you are finished testing:
1. Go back to your **first** terminal window (the backend server) and press `Ctrl + C`. This will terminate the FastAPI REST API and all three FastMCP background processes.
2. Go to your **second** terminal window (the dashboard web server) and press `Ctrl + C` to stop the web server.
3. You can now close both terminal windows.
