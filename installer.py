import os
import shutil
import glob
import urllib.request
import json
import sys
import subprocess
import time
from pathlib import Path
import filecmp

# ================================

# CONFIG

# ================================

GITHUB_USER = "ProdHallow"
GITHUB_REPO = "StereoInstaller"
GITHUB_BRANCH = "main"
SCRIPT_NAME = "installer.py"  # name of this Python script in GitHub

APPDATA = os.getenv("APPDATA")
LOCALAPPDATA = os.getenv("LOCALAPPDATA")
TEMP_DIR = os.getenv("TEMP")
SCRIPT_DIR = Path(**file**).parent

# ================================

# AUTO-UPDATE

# ================================

def auto_update():
update_url = f"[https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{SCRIPT_NAME}](https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{SCRIPT_NAME})"
temp_file = Path(TEMP_DIR) / "stereo_update.tmp"
current_file = Path(**file**)

```
print("Checking for updates...")
try:
    urllib.request.urlretrieve(update_url, temp_file)
except Exception as e:
    print(f"[UPDATE ERROR] Could not download update: {e}")
    return

if not temp_file.exists() or not filecmp.cmp(temp_file, current_file):
    print("New update found! Applying update...")
    try:
        shutil.copy2(temp_file, current_file)
        print("Update applied. Restarting script...")
        temp_file.unlink(missing_ok=True)
        os.execv(sys.executable, [sys.executable, str(current_file)])
    except Exception as e:
        print(f"[UPDATE ERROR] Could not replace script: {e}")
        sys.exit(1)
else:
    print("You are already on the latest version.")
    temp_file.unlink(missing_ok=True)
```

# ================================

# COLORS

# ================================

class Color:
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
RESET = "\033[0m"

# ================================

# HELPER FUNCTIONS

# ================================

def progress_bar(msg, length=25, delay=0.05):
bar = ""
for _ in range(length):
bar += "█"
print(f"{Color.CYAN}[{bar}]{Color.RESET} {msg}\r", end="")
time.sleep(delay)
print()

def find_latest_discord_build():
base = Path(LOCALAPPDATA) / "Discord"
for folder in sorted(base.glob("app-*"), reverse=True):
if (folder / "modules").exists():
for module in folder.glob("modules/discord_voice*"):
return folder
return None

def find_discord_voice_module(appPath):
for module in (appPath / "modules").glob("discord_voice*"):
if (module / "discord_voice").exists():
return module / "discord_voice"
return module
return None

def copy_backup_to_target(source, target):
if not source.exists():
print(f"{Color.RED}[ERROR]{Color.RESET} Backup folder not found: {source}")
return False
print(f"{Color.GREEN}[FOUND]{Color.RESET} Backup folder: {source}")
shutil.rmtree(target, ignore_errors=True)
shutil.copytree(source, target)
progress_bar("Updating module files...")
return True

def replace_ffmpeg(appPath):
ffmpeg_source = next(SCRIPT_DIR.rglob("ffmpeg.dll"), None)
if not ffmpeg_source:
print(f"{Color.RED}[ERROR]{Color.RESET} ffmpeg.dll not found.")
return False
ffmpeg_target = appPath / "ffmpeg.dll"
try:
shutil.copy2(ffmpeg_source, ffmpeg_target)
print(f"{Color.GREEN}[SUCCESS]{Color.RESET} ffmpeg.dll replaced.")
return True
except Exception as e:
print(f"{Color.RED}[ERROR]{Color.RESET} Failed to copy ffmpeg.dll: {e}")
return False

def create_startup_shortcut():
startup_folder = Path(APPDATA) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
shortcut_path = startup_folder / "DiscordVoiceFixer.lnk"
script_path = Path(**file**).resolve()

```
vbs_file = Path(TEMP_DIR) / "createShortcut.vbs"
with open(vbs_file, "w") as f:
    f.write(f"""Set WshShell = WScript.CreateObject("WScript.Shell")
```

Set Shortcut = WshShell.CreateShortcut("{shortcut_path}")
Shortcut.TargetPath = "{script_path}"
Shortcut.WorkingDirectory = "{SCRIPT_DIR}"
Shortcut.WindowStyle = 1
Shortcut.Save
""")
subprocess.run(["cscript", "//nologo", str(vbs_file)])
vbs_file.unlink(missing_ok=True)
print(f"{Color.GREEN}[SUCCESS]{Color.RESET} Startup shortcut created.")

def quit_discord():
subprocess.run(["taskkill", "/F", "/IM", "discord.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(["taskkill", "/F", "/IM", "Update.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)

def launch_discord(appPath):
subprocess.Popen([str(appPath / "Discord.exe")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"{Color.GREEN}[DONE]{Color.RESET} All tasks completed.")

# ================================

# MAIN SCRIPT

# ================================

if **name** == "**main**":
auto_update()

```
print(f"{Color.CYAN}===========================================")
print("      Discord Voice Module Auto-Fixer")
print(f"==========================================={Color.RESET}\n")

quit_discord()

appPath = find_latest_discord_build()
if not appPath:
    print(f"{Color.RED}[ERROR]{Color.RESET} No Discord app-* folder with voice module found.")
    input("Press Enter to exit...")
    sys.exit(1)
print(f"{Color.GREEN}[FOUND]{Color.RESET} Using Discord folder: {Color.CYAN}{appPath}{Color.RESET}\n")

voice_module = find_discord_voice_module(appPath)
if not voice_module:
    print(f"{Color.RED}[ERROR]{Color.RESET} No discord_voice module found.")
    input("Press Enter to exit...")
    sys.exit(1)

backup_folder = next(SCRIPT_DIR.glob("Discord*Backup"), None)
if not backup_folder:
    print(f"{Color.RED}[ERROR]{Color.RESET} Backup folder not found next to the script.")
    input("Press Enter to exit...")
    sys.exit(1)

copy_backup_to_target(backup_folder, voice_module)
replace_ffmpeg(appPath)
create_startup_shortcut()
launch_discord(appPath)

input("Press Enter to exit...")
```
