# Installation

pyTIARA runs on **Windows 10 or 11 (64-bit)**. It installs into its own Python
environment inside the pyTIARA folder, so it does not touch any other Python on
the computer.

## Requirements

| | Minimum | Recommended / tested |
|---|---|---|
| Operating system | Windows 10 64-bit | Windows 10 / 11 |
| GPU | NVIDIA with CUDA support; optional (CPU mode is 10-50x slower) | 8 GB NVIDIA GPU (tested: Quadro M4000, driver 471.41) |
| NVIDIA driver | 452.39 or newer (CUDA 11.8 build) | the newest driver for your card |
| RAM | 16 GB | 32-64 GB |
| Disk | ~6 GB for the software | fast local disk for outputs (see below) |
| Python | installed automatically (Miniconda needed) | — |
| IMOD for Windows | only for reconstruction | IMOD 4.11 or newer |

Output size for one K3 tilt series (5760 x 4092, ~46 tilts): full-resolution
float32 stack ~4.3 GB (int16 halves it), bin-4 stack ~0.27 GB, bin-4 IMOD
project ~3 GB.

## 1. Install Miniconda

Download and install **Miniconda for Windows** from
<https://docs.conda.io/en/latest/miniconda.html> (the default "just me" install
is fine). pyTIARA only uses conda to create its private Python 3.11; you do not
need to use conda yourself afterwards.

## 2. Get pyTIARA

Either clone with git:

```bat
git clone https://github.com/pyRIME/pyTIARA.git
```

or download the ZIP from the GitHub page (**Code > Download ZIP**) and extract
it. Put it on a drive with a few GB free (the environment is ~5 GB).

## 3. Run the installer

Double-click **`install.bat`** in the pyTIARA folder, or run it from a command
prompt:

```bat
cd path\to\pyTIARA
install.bat
```

It will:

1. find Miniconda/Anaconda,
2. create a Python 3.11 environment in `pyTIARA\env`,
3. install PyTorch with CUDA (about 2.5 GB download),
4. install pyTIARA and its other dependencies (NumPy, SciPy, PySide6, pyqtgraph,
   tifffile, imagecodecs, pytest),
5. create **pyTIARA shortcuts** on the Desktop and in the Start menu,
6. print the GPU it found.

The last line should read something like:

```
pyTIARA 0.1.0 | PyTorch 2.7.1+cu118 | GPU: Quadro M4000
```

If it says `GPU: NOT AVAILABLE`, see [Troubleshooting](troubleshooting.md#gpu-not-detected).

### Choosing the PyTorch/CUDA build

The default build (CUDA 11.8) works with NVIDIA drivers from 452.39 on and with
GPUs from Maxwell (GTX 900 / Quadro M-series) to Ada (RTX 40-series). Pass a
different build to the installer if needed:

| Your GPU / driver | Command |
|---|---|
| Most GPUs, older drivers (default) | `install.bat` |
| Newer driver (2023+), want CUDA 12 | `install.bat cu126` |
| RTX 50-series (Blackwell) | `install.bat cu128` (driver 570 or newer) |
| No NVIDIA GPU | `install.bat cpu` |

Re-running `install.bat` on an existing installation just updates the packages.

## 4. Install IMOD (for reconstruction)

Frame alignment and stack building need nothing else. To let pyTIARA run
**batchruntomo** and produce tomograms, install **IMOD for Windows** from
<https://bio3d.colorado.edu/imod/> following its instructions, including the
Python that IMOD's scripts need. Check it works by opening a command prompt and
running `etomo`.

pyTIARA finds IMOD through the `IMOD_DIR` environment variable (set by the IMOD
installer) or at `C:\Program Files\IMOD`. It runs IMOD's scripts with the same
`python` that etomo uses, never with pyTIARA's own environment. The
**Reconstruction** page shows whether IMOD was found and which Python it will use.

### Optional: redeposition removal

Redeposition removal needs the [ASTRA Toolbox](https://astra-toolbox.com) and a
CUDA GPU. Install it into pyTIARA's environment:

```bat
env\python.exe -m pip install astra-toolbox
```

or run `set PYTIARA_REDEP=1` before `install.bat`, which installs pyTIARA with its
`redep` extra. ASTRA brings its own CUDA runtime from pip. Restart pyTIARA; the
**Reconstruction** page then enables *Also write a tomogram with the redeposition
removed* and shows the ASTRA version under it. ASTRA is licensed under the GPLv3
and is not part of pyTIARA.

## 5. Start pyTIARA

Use the **pyTIARA** shortcut on the Desktop or in the Start menu (or
double-click `pyTIARA.bat`). A splash screen appears within a couple of
seconds while the libraries load (the first start after installing or rebooting
can take ~30 s on a hard disk).

To recreate the shortcuts (e.g. after moving the folder):
`env\python.exe scripts\make_shortcut.py`. To skip them during installation,
run `set PYTIARA_NO_SHORTCUT=1` before `install.bat`.

## Checking the installation (optional)

```bat
env\python.exe -m pytest
```

All tests should pass (they use synthetic data and take well under a minute).

## Updating

```bat
git pull
install.bat
```

(or download the new ZIP, copy your `env` folder into it, and run `install.bat`).

## Coming from pyPrep

pyTIARA is the same program as pyPrep, renamed in November 2026. To move an
existing installation over:

```bat
git remote set-url origin https://github.com/pyRIME/pyTIARA.git
git pull
install.bat
```

`install.bat` installs the `pytiara` package into the existing `env` folder and
replaces the pyPrep shortcuts. Then remove the old package with
`env\python.exe -m pip uninstall pyprep`. You can rename the folder itself; run
`install.bat` again afterwards.

What changed:

| | pyPrep | pyTIARA |
|---|---|---|
| Start the app | `pyPrep.bat` | `pyTIARA.bat` |
| Command line | `python -m pyprep ...` | `python -m pytiara ...` |
| Python package | `import pyprep` | `import pytiara` |
| Series record and log | `<series>_pyprep.json`, `_pyprep.log` | `<series>_pytiara.json`, `_pytiara.log` |
| Reconstruction record | `imod_bin<N>\pyprep_recon.json` | `imod_bin<N>\pytiara_recon.json` |
| Other files | `pyprep_*`, `tilt.com.pyprep_orig` | `pytiara_*`, `tilt.com.pytiara_orig` |
| Default output folder | `<session>\pyPrep` | `<session>\pyTIARA` |
| Installer switches | `PYPREP_NO_SHORTCUT`, `PYPREP_NOPAUSE`, `PYPREP_REDEP` | `PYTIARA_...` |

Nothing has to be reprocessed. pyTIARA reads output written by pyPrep under its
old file names and shows it in the Results page and the Gallery. It renames a
series folder's old files to the new names the next time it writes to that
folder (for example when you redo a reconstruction). Your settings, window
layout and presets are copied over the first time pyTIARA starts.

## Uninstalling

Delete the pyTIARA folder and the two **pyTIARA** shortcuts (Desktop, Start menu).
pyTIARA also stores window layout and last-used settings in the Windows registry
(`HKEY_CURRENT_USER\Software\pyTIARA`), saved presets in `%APPDATA%\pyTIARA`,
and its startup error and crash logs in `%LOCALAPPDATA%\pyTIARA`.

## Manual installation

If you prefer to set things up yourself (any conda or venv works, Python 3.11+):

```bat
conda create -y --prefix env python=3.11
env\python.exe -m pip install torch==2.7.1 --index-url https://download.pytorch.org/whl/cu118
env\python.exe -m pip install -e ".[test]"
```

Install PyTorch **before** pyTIARA: `pip install` of a package that lists `torch`
as a dependency would otherwise fetch the CPU-only PyTorch from PyPI.
