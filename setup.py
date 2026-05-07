#!/usr/bin/env python3
"""
MediCare Clinic — Cross-Platform Setup Script
Works on: Windows 10/11, macOS 12+, Ubuntu 20.04+

Usage:
  python setup.py           # Full setup (recommended first run)
  python setup.py --db      # Only setup database
  python setup.py --run     # Only start the server
"""

import os
import sys
import subprocess
import platform
import shutil

PLATFORM = platform.system()
PYTHON = sys.executable
PIP = f"{PYTHON} -m pip"

GREEN  = '\033[92m'
YELLOW = '\033[93m'
RED    = '\033[91m'
CYAN   = '\033[96m'
RESET  = '\033[0m'
BOLD   = '\033[1m'

def p(msg, color=RESET):
    print(f"{color}{msg}{RESET}")

def run(cmd, cwd=None, shell=True):
    result = subprocess.run(cmd, cwd=cwd, shell=shell, capture_output=True, text=True)
    if result.returncode != 0 and result.stderr:
        p(f"  ⚠  {result.stderr.strip()}", YELLOW)
    return result.returncode == 0

def check_python():
    p("\n🐍 Checking Python version...", CYAN)
    major, minor = sys.version_info.major, sys.version_info.minor
    if major < 3 or (major == 3 and minor < 9):
        p(f"❌ Python 3.9+ required. You have {major}.{minor}", RED)
        p("   Download: https://www.python.org/downloads/", YELLOW)
        sys.exit(1)
    p(f"  ✅ Python {major}.{minor} — OK", GREEN)

def check_mysql():
    p("\n🗄  Checking MySQL...", CYAN)
    if shutil.which('mysql'):
        p("  ✅ MySQL found", GREEN)
        return True
    p("  ⚠  MySQL not found in PATH", YELLOW)
    p("  Install MySQL Community Server:", YELLOW)
    if PLATFORM == 'Darwin':
        p("  → brew install mysql", YELLOW)
        p("     or download: https://dev.mysql.com/downloads/mysql/", YELLOW)
    elif PLATFORM == 'Windows':
        p("  → Download: https://dev.mysql.com/downloads/installer/", YELLOW)
    else:
        p("  → sudo apt-get install mysql-server", YELLOW)
    return False

def setup_venv():
    p("\n📦 Setting up virtual environment...", CYAN)
    venv_dir = os.path.join('backend', 'venv')
    if not os.path.exists(venv_dir):
        run(f"{PYTHON} -m venv {venv_dir}")
        p("  ✅ Virtual environment created", GREEN)
    else:
        p("  ✅ Virtual environment exists", GREEN)

    # Path to pip inside venv
    if PLATFORM == 'Windows':
        venv_pip = os.path.join(venv_dir, 'Scripts', 'pip')
        venv_py  = os.path.join(venv_dir, 'Scripts', 'python')
    else:
        venv_pip = os.path.join(venv_dir, 'bin', 'pip')
        venv_py  = os.path.join(venv_dir, 'bin', 'python')
    return venv_pip, venv_py

def install_dependencies(venv_pip):
    p("\n📥 Installing Python dependencies...", CYAN)
    req_file = os.path.join('backend', 'requirements.txt')
    if not os.path.exists(req_file):
        p(f"  ❌ requirements.txt not found at {req_file}", RED)
        return False
    ok = run(f"{venv_pip} install -r {req_file}")
    if ok:
        p("  ✅ All dependencies installed", GREEN)
    else:
        p("  ⚠  Some packages may have failed. Try running manually:", YELLOW)
        p(f"     {venv_pip} install -r {req_file}", YELLOW)
    return ok

def setup_env():
    p("\n⚙️  Setting up environment file...", CYAN)
    env_src = os.path.join('backend', '.env.example')
    env_dst = os.path.join('backend', '.env')
    if not os.path.exists(env_dst):
        shutil.copy(env_src, env_dst)
        p("  ✅ .env created from .env.example", GREEN)
        p("  ⚠  Edit backend/.env with your MySQL password and email credentials!", YELLOW)
    else:
        p("  ✅ .env already exists", GREEN)

def setup_mysql():
    p("\n🗄  Setting up MySQL database...", CYAN)
    p("  Creating database 'medicare_clinic'...", CYAN)
    sql = "CREATE DATABASE IF NOT EXISTS medicare_clinic CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    
    # Try without password first
    cmd = f'mysql -u root -e "{sql}"'
    if not run(cmd):
        # Prompt for password
        p("  Enter MySQL root password (leave blank if none):", YELLOW)
        pwd = input("  MySQL Password: ").strip()
        if pwd:
            cmd = f'mysql -u root -p"{pwd}" -e "{sql}"'
        if not run(cmd):
            p("  ⚠  Could not auto-create DB. Please run manually:", YELLOW)
            p(f"     mysql -u root -p", YELLOW)
            p(f"     {sql}", YELLOW)
            return
    p("  ✅ Database 'medicare_clinic' ready", GREEN)

def run_migrations(venv_py):
    p("\n🔄 Running Django migrations...", CYAN)
    manage = os.path.join('backend', 'manage.py')
    
    ok1 = run(f"{venv_py} {manage} migrate")
    if ok1:
        p("  ✅ Migrations applied", GREEN)
    else:
        p("  ⚠  Migration failed. Check your .env DB credentials.", YELLOW)
        return False

    ok2 = run(f"{venv_py} {manage} seed_data")
    if ok2:
        p("  ✅ Demo data seeded", GREEN)
    return True

def create_superuser(venv_py):
    p("\n👤 Creating Django admin superuser...", CYAN)
    manage = os.path.join('backend', 'manage.py')
    script = (
        "from django.contrib.auth.models import User; "
        "User.objects.filter(username='admin').exists() or "
        "User.objects.create_superuser('admin','admin@medicare.com','admin123')"
    )
    run(f'{venv_py} {manage} shell -c "{script}"')
    p("  ✅ Admin user: admin / admin123", GREEN)
    p("  ⚠  Change password in production!", YELLOW)

def collect_static(venv_py):
    manage = os.path.join('backend', 'manage.py')
    run(f"{venv_py} {manage} collectstatic --noinput")

def start_server(venv_py):
    p("\n🚀 Starting Django development server...", CYAN)
    p(f"  Backend API → http://127.0.0.1:8000/api/", GREEN)
    p(f"  Admin Panel → http://127.0.0.1:8000/admin/  (admin / admin123)", GREEN)
    p(f"  Frontend    → Open frontend/index.html in your browser", GREEN)
    p("  Press Ctrl+C to stop\n", YELLOW)
    manage = os.path.join('backend', 'manage.py')
    subprocess.run(f"{venv_py} {manage} runserver 0.0.0.0:8000", shell=True)

def print_header():
    p(f"""
{CYAN}{BOLD}
╔══════════════════════════════════════════════════════╗
║          MediCare Clinic — Setup & Launcher          ║
║     Full-stack Django + MySQL Appointment System     ║
╚══════════════════════════════════════════════════════╝
{RESET}""")

def print_summary():
    p(f"""
{GREEN}{BOLD}✅ Setup Complete!{RESET}
{CYAN}
┌─────────────────────────────────────────────────────┐
│  NEXT STEPS                                         │
│                                                     │
│  1. Edit backend/.env with your credentials         │
│     • MySQL password                                │
│     • Gmail app password (for email alerts)         │
│     • Twilio credentials (for SMS alerts)           │
│                                                     │
│  2. Start the server:                               │
│     python setup.py --run                           │
│                                                     │
│  3. Open the frontend:                              │
│     frontend/index.html (double-click or Live Server│
│                                                     │
│  4. Admin panel:                                    │
│     http://127.0.0.1:8000/admin                     │
│     Login: admin / admin123                         │
│                                                     │
│  5. API endpoints:                                  │
│     http://127.0.0.1:8000/api/departments/          │
│     http://127.0.0.1:8000/api/doctors/              │
│     http://127.0.0.1:8000/api/appointments/book/    │
└─────────────────────────────────────────────────────┘
{RESET}""")

if __name__ == '__main__':
    print_header()
    args = sys.argv[1:]
    run_only = '--run' in args
    db_only = '--db' in args

    check_python()

    venv_pip, venv_py = setup_venv()

    if run_only:
        start_server(venv_py)
        sys.exit(0)

    install_dependencies(venv_pip)
    setup_env()

    if not db_only:
        check_mysql()

    setup_mysql()
    run_migrations(venv_py)
    create_superuser(venv_py)
    collect_static(venv_py)

    print_summary()

    p("\nStart the server now? (y/n): ", CYAN)
    ans = input("  > ").strip().lower()
    if ans == 'y':
        start_server(venv_py)
