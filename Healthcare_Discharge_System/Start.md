# 🏥 How to Run the AI Healthcare Discharge System

Welcome! This guide is written for anyone to easily start and test the Healthcare AI Discharge system on their computer, even with no technical background. Just follow these steps in order.

---

## 🛠️ Phase 1: Setup the Environment (First Time Only)

These steps make sure your computer has the right packages installed to run the AI.

1. **Open your Terminal (Command Prompt or PowerShell).**
2. **Navigate to the project folder** by typing:
   ```bash
   cd Desktop\Project5-v10\Healthcare_Discharge_System
   ```
3. **Create a Python Virtual Environment** (a safe, isolated space for the project's files):
   ```bash
   python -m venv venv
   ```
4. **Activate the Environment:**
   ```bash
   .\venv\Scripts\activate
   ```
   *(You should now see `(venv)` at the start of your typing line).*
5. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```
   *Wait a minute or two for everything to download and install.*

---

## 🚀 Phase 2: Start the Project Servers

The project runs on two servers: one for the AI backend (FastAPI), and one for the frontend Dashboard.

### Step A: Start the AI Backend Server
1. Make sure you are still in your terminal with `(venv)` active.
2. Run this exact command to start all the AI servers:
   ```powershell
   $env:PYTHONIOENCODING="utf-8"; python run_servers.py
   ```
3. You will see text confirming that the EHR, Pharmacy, Billing, and REST APIs have started. **Leave this window open.**

### Step B: Start the Web Dashboard
1. Open a **second, brand new Terminal window**.
2. Navigate to the dashboard folder:
   ```bash
   cd Desktop\Project5-v10\Healthcare_Discharge_System\web_dashboard
   ```
3. Start the dashboard server by typing:
   ```bash
   python -m http.server 8080
   ```
4. **Leave this window open too.**

---

## 💻 Phase 3: Test the Dashboard!

Now that everything is running behind the scenes, you can actually use the AI!

1. Open your favorite web browser (Chrome, Edge, Safari, etc.).
2. In the top address bar, type:
   **[http://localhost:8080](http://localhost:8080)**
3. The dashboard will load! 
4. **How to test it:** 
   - Click on **Ravi Kumar (P001)** and hit "Initiate Discharge" to see the AI block him for an Allergy conflict!
   - Click on **Anita Desai (P002)** to watch the AI successfully validate her meds, generate her invoice, and clear her for discharge!

---

## 🛑 Phase 4: How to Stop the Project

When you are completely finished testing:
1. Go back to your **first** terminal window (the backend one) and press `Ctrl + C` on your keyboard. This will safely shut down the AI servers.
2. Go to your **second** terminal window (the dashboard one) and press `Ctrl + C` to stop the web dashboard.
3. You can safely close the terminal windows. 
