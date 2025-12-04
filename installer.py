import os
import shutil
import glob
import urllib.request
import json
import sys
import subprocess
import time
import filecmp
from pathlib import Path

GITHUB_USER = "ProdHallow"
GITHUB_REPO = "StereoInstaller"
GITHUB_BRANCH = "main"
SCRIPT_NAME = "installer.py"

APPDATA = os.getenv("APPDATA")
LOCALAPPDATA = os.getenv("LOCALAPPDATA")
TEMP_DIR = os.getenv("TEMP")

# Adjust SCRIPT_DIR for PyInstaller
if getattr(sys, "frozen", False):
    SCRIPT_DIR = Path(sys._MEIPASS)  # PyInstaller temporary folder
else:
    SCRIPT_DIR = Path(__file__).parent

class Color:
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    RESET = "\033[0m"

def print_success(message):
    print(f"{Color.GREEN}[SUCCESS]{Color.RESET} {message}")

def print_error(message):
    print(f"{Color.RED}[ERROR]{Color.RESET} {message}")

def print_info(message):
    print(f"{Color.CYAN}[INFO]{Color.RESET} {message}")

def print_warning(message):
    print(f"{Color.YELLOW}[WARNING]{Color.RESET} {message}")

def print_progress(current, total, message=''):
    percent = int((current / total) * 100)
    bar_length = 30
    filled_length = int(bar_length * percent // 100)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    print(f"\r{Color.CYAN}[{bar}] {percent}% {Color.RESET} {message}", end='', flush=True)

def download_with_progress(url, dest):
    with urllib.request.urlopen(url) as response:
        total_size = int(response.getheader("Content-Length").strip())
        block_size = 8192
        downloaded = 0
        with open(dest, "wb") as f:
            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break
                f.write(buffer)
                downloaded += len(buffer)
                print_progress(downloaded, total_size, "Downloading update...")
    print()
    print_success("Download complete.")

def auto_update():
    update_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/refs/heads/{GITHUB_BRANCH}/{SCRIPT_NAME}"
    temp_file = Path(TEMP_DIR) / "stereo_update.tmp"
    current_file = Path(sys.executable if getattr(sys, "frozen", False) else __file__)
    print_info("Checking for updates...")
    try:
        download_with_progress(update_url, temp_file)
    except Exception as e:
        print_error(f"Could not download update: {e}")
        return
    if not temp_file.exists() or not filecmp.cmp(str(temp_file), str(current_file)):
        print_info("New update found! Applying update...")
        if getattr(sys, "frozen", False):
            batch_path = Path(TEMP_DIR) / "update.bat"
            with open(batch_path, "w") as f:
                f.write(f"""@echo off
timeout /t 1 /nobreak >nul
copy /y "{temp_file}" "{current_file}"
start "" "{current_file}"
del "%~f0"
""")
            subprocess.Popen([str(batch_path)])
            print_info("Update scheduled. Exiting...")
            sys.exit(0)
        else:
            shutil.copy2(str(temp_file), str(current_file))
            print_info("Update applied. Restarting script...")
            temp_file.unlink(missing_ok=True)
            os.execv(sys.executable, [sys.executable, str(current_file)])
    else:
        print_info("You are already on the latest version.")
        temp_file.unlink(missing_ok=True)

def find_latest_discord_build():
    base = Path(LOCALAPPDATA) / "Discord"
    for folder in sorted(base.glob("app-*"), reverse=True):
        if (folder / "modules").exists():
            for module in (folder / "modules").glob("discord_voice*"):
                return folder
    return None

def find_discord_voice_module(appPath):
    for module in (appPath / "modules").glob("discord_voice*"):
        if (module / "discord_voice").exists():
            return module / "discord_voice"
    return None

def copy_backup_to_target(source, target):
    if not source.exists():
        print_error(f"Backup folder not found: {source}")
        return False
    print_success(f"Backup folder found: {source}")
    shutil.rmtree(target, ignore_errors=True)
    shutil.copytree(source, target)
    for i in range(0, 101, 10):
        print_progress(i, 100, "Updating module files...")
        time.sleep(0.05)
    print()
    return True

def replace_ffmpeg(appPath):
    ffmpeg_source = next(SCRIPT_DIR.rglob("ffmpeg.dll"), None)
    if not ffmpeg_source:
        print_error("ffmpeg.dll not found.")
        return False
    ffmpeg_target = appPath / "ffmpeg.dll"
    try:
        shutil.copy2(ffmpeg_source, ffmpeg_target)
        print_success("ffmpeg.dll replaced.")
        return True
    except Exception as e:
        print_error(f"Failed to copy ffmpeg.dll: {e}")
        return False

def create_startup_shortcut():
    startup_folder = Path(APPDATA) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    shortcut_path = startup_folder / "DiscordVoiceFixer.lnk"
    target_path = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve()
    vbs_path = Path(TEMP_DIR) / "createShortcut.vbs"
    with open(vbs_path, "w") as f:
        f.write(f"""Set WshShell = WScript.CreateObject("WScript.Shell")
Set Shortcut = WshShell.CreateShortcut("{shortcut_path}")
Shortcut.TargetPath = "{target_path}"
Shortcut.WorkingDirectory = "{SCRIPT_DIR}"
Shortcut.WindowStyle = 1
Shortcut.Save
""")
    subprocess.run(["cscript", "//nologo", str(vbs_path)])
    try:
        vbs_path.unlink()
    except FileNotFoundError:
        pass
    print_success("Startup shortcut created.")

def quit_discord():
    subprocess.run(["taskkill", "/F", "/IM", "discord.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["taskkill", "/F", "/IM", "Update.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

def launch_discord(appPath):
    subprocess.Popen([str(appPath / "Discord.exe")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print_success("Discord relaunched.")
    print("All tasks completed.")

if __name__ == "__main__":
    auto_update()
    print(f"{Color.CYAN}===========================================")
    print("      Discord Voice Module Auto-Fixer")
    print(f"==========================================={Color.RESET}\n")
    quit_discord()
    appPath = find_latest_discord_build()
    if not appPath:
        print_error("No Discord app-* folder with voice module found.")
        input("Press Enter to exit...")
        sys.exit(1)
    print_success(f"Using Discord folder: {appPath}")
    voice_module = find_discord_voice_module(appPath)
    if not voice_module:
        print_error("No discord_voice module found.")
        input("Press Enter to exit...")
        sys.exit(1)
    backup_folder = next(SCRIPT_DIR.glob("Discord*Backup"), None)
    if not backup_folder:
        print_error("Backup folder not found next to the script.")
        input("Press Enter to exit...")
        sys.exit(1)
    copy_backup_to_target(backup_folder, voice_module)
    replace_ffmpeg(appPath)
    create_startup_shortcut()
    launch_discord(appPath)
    input("Press Enter to exit...")
