"""Create pyTIARA shortcuts on the Desktop and in the Start menu (Windows).

Run by install.bat; can be re-run any time:   env\\python.exe scripts\\make_shortcut.py
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _ps_quote(s: str) -> str:
    return "'" + str(s).replace("'", "''") + "'"


def folder(name: str) -> Path:
    """Desktop / Programs folder as Windows resolves it (handles OneDrive-redirected desktops)."""
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          f"[Environment]::GetFolderPath('{name}')"],
                         capture_output=True, text=True, check=True).stdout.strip()
    return Path(out)


def make_shortcut(lnk: Path) -> None:
    pythonw = ROOT / "env" / "pythonw.exe"
    icon = ROOT / "pytiara" / "gui" / "logo" / "pytiara.ico"
    script = (f"$s = (New-Object -ComObject WScript.Shell).CreateShortcut({_ps_quote(lnk)}); "
              f"$s.TargetPath = {_ps_quote(pythonw)}; $s.Arguments = '-m pytiara.gui.launcher'; "
              f"$s.WorkingDirectory = {_ps_quote(ROOT)}; $s.IconLocation = {_ps_quote(str(icon) + ',0')}; "
              f"$s.Description = 'pyTIARA - cryo-ET tilt-series preparation'; $s.Save()")
    subprocess.run(["powershell", "-NoProfile", "-Command", script], check=True)


def main() -> int:
    if sys.platform != "win32":
        print("Shortcuts are only created on Windows.")
        return 0
    made = []
    for where in ("Desktop", "Programs"):
        try:
            target = folder(where) / "pyTIARA.lnk"
            make_shortcut(target)
            made.append(str(target))
            target.with_name("pyPrep.lnk").unlink(missing_ok=True)    # the shortcut from before the rename
        except (subprocess.CalledProcessError, OSError) as e:
            print(f"Could not create the {where} shortcut: {e}")
    for m in made:
        print("Shortcut:", m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
