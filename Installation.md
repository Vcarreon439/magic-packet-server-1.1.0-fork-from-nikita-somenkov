# Quick Start: Building the Installers

This guide covers the process for generating installers for **Windows** and **Linux**. Note: I do not have a macOS environment. **If you are a Mac user, contributions to the Mac Installation guide are welcome!**

## Windows Build Process

### Prerequisites:

- Python installed.
- pyinstaller library installed.
- **_Inno Setup_** Compiler installed.

#### Steps:

1. Generate Binaries: Navigate to installer/windows and run:

```
build-exe.bat
```

This will generate two executables in **dist/windows**: **_mpserver.exe_** and **_mpworker.exe_**.

2. Compile Installer: Open windows/mpservices.iss with Inno Setup Compiler and run the compilation script.

3. Distribution: The final setup file will be generated, which can be used to install the services on any Windows machine.

---

## Linux Build Process

### Prerequisites:

- Python and pyinstaller installed.

#### Steps:

1. Install Dependencies:

```
pip install -r requirements.txt
```

2. Generate Binaries: Use the shared build script for Linux:

```
bash installer/shared/build-exe.sh linux
```

3. Package the Installer:

```
bash installer/linux/build-installer.sh
```

**Installation on Target Machine**: Copy the generated package to your target device, then run the following as root:

```
tar -xvf mpserver.tar.gz
cd mpserver
sudo ./installer.sh install
```
