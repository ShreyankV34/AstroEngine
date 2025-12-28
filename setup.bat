@echo off
REM AstroCamSync Project Setup Script for Windows
REM Run this in your AstroEngine directory

echo.
echo ========================================
echo   AstroCamSync Project Setup
echo ========================================
echo.

REM Create folder structure
echo [1/5] Creating folder structure...
mkdir astrocam_sync\core 2>nul
mkdir astrocam_sync\targets 2>nul
mkdir astrocam_sync\cameras 2>nul
mkdir astrocam_sync\conditions\sensors 2>nul
mkdir astrocam_sync\sync 2>nul
mkdir astrocam_sync\cli 2>nul
mkdir astrocam_sync\utils 2>nul
mkdir tests 2>nul
mkdir docs 2>nul
mkdir scripts 2>nul
mkdir .github\workflows 2>nul
echo    Done!

REM Create __init__.py files
echo [2/5] Creating Python package files...
type nul > astrocam_sync\__init__.py
type nul > astrocam_sync\core\__init__.py
type nul > astrocam_sync\targets\__init__.py
type nul > astrocam_sync\cameras\__init__.py
type nul > astrocam_sync\conditions\__init__.py
type nul > astrocam_sync\conditions\sensors\__init__.py
type nul > astrocam_sync\sync\__init__.py
type nul > astrocam_sync\cli\__init__.py
type nul > astrocam_sync\utils\__init__.py
type nul > tests\__init__.py
echo    Done!

REM Create .gitignore
echo [3/5] Creating .gitignore...
(
echo # Python
echo __pycache__/
echo *.py[cod]
echo *$py.class
echo *.so
echo .Python
echo build/
echo develop-eggs/
echo dist/
echo downloads/
echo eggs/
echo .eggs/
echo lib/
echo lib64/
echo parts/
echo sdist/
echo var/
echo wheels/
echo *.egg-info/
echo .installed.cfg
echo *.egg
echo MANIFEST
echo.
echo # Virtual environments
echo venv/
echo env/
echo ENV/
echo .venv
echo.
echo # IDE
echo .vscode/
echo .idea/
echo *.swp
echo *.swo
echo *~
echo .DS_Store
echo.
echo # Testing
echo .pytest_cache/
echo .coverage
echo htmlcov/
echo .tox/
echo.
echo # MyPy
echo .mypy_cache/
echo.
echo # Project specific
echo *.log
echo config.local.yaml
echo *.db
echo *.sqlite
) > .gitignore
echo    Done!

REM Create requirements.txt
echo [4/5] Creating requirements.txt...
(
echo # Core dependencies
echo numpy^>=1.24.0
echo scipy^>=1.10.0
echo pytz^>=2023.3
echo python-dateutil^>=2.8.2
echo click^>=8.1.0
echo pyyaml^>=6.0
echo requests^>=2.31.0
) > requirements.txt
echo    Done!

REM Create README.md
echo [5/5] Creating README.md...
(
echo # 🌌 AstroEngine ^(AstroCamSync^)
echo.
echo **Real-time, GPS-synced astrophotography decision engine**
echo.
echo [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg^)](LICENSE^)
echo [![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg^)](https://www.python.org/^)
echo.
echo ---
echo.
echo ## What Is This?
echo.
echo AstroCamSync is a **physics-driven decision engine** that computes optimal astrophotography camera settings by synchronizing:
echo.
echo 1. **Celestial mechanics** - Time, coordinates, object motion
echo 2. **Observer location** - GPS positioning, UTC→LST conversion
echo 3. **Camera sensor physics** - Noise models, ISO behavior, dynamic range
echo 4. **Real-time environment** - SQM sensors, weather APIs, light pollution
echo 5. **Decision fusion** - Judgment-producing recommendations with confidence
echo.
echo This is a **deterministic, explainable instrument** for serious astrophotography.
echo.
echo ---
echo.
echo ## 🚧 Status: Active Development
echo.
echo **Currently Implemented:**
echo - ✅ Project structure
echo - ✅ Time system ^(UTC → JD → GST → LST^)
echo - ✅ Coordinate transforms ^(RA/Dec → Alt/Az^)
echo - ✅ Celestial mechanics ^(NPF rule, star trailing^)
echo - ✅ Exposure engine ^(SNR optimization^)
echo - 🚧 Camera database ^(in progress^)
echo - 🚧 Target catalog ^(in progress^)
echo - 🚧 Environmental sensors ^(planned^)
echo - 🚧 CLI interface ^(planned^)
echo.
echo ---
echo.
echo ## Quick Start
echo.
echo ### Installation
echo.
echo ```bash
echo # Clone repository
echo git clone https://github.com/ShreyankV34/AstroEngine.git
echo cd AstroEngine
echo.
echo # Create virtual environment
echo python -m venv venv
echo venv\Scripts\activate
echo.
echo # Install package
echo pip install -e .
echo ```
echo.
echo ---
echo.
echo ## Architecture
echo.
echo ```
echo astrocam_sync/
echo ├── core/          # Astronomical calculations
echo │   ├── time.py          # UTC→LST conversions
echo │   ├── coordinates.py   # RA/Dec→Alt/Az
echo │   ├── astronomy.py     # Celestial mechanics
echo │   └── engine.py        # Exposure calculations
echo ├── targets/       # Target database
echo ├── cameras/       # Camera specifications
echo ├── conditions/    # Environmental data
echo ├── sync/          # Decision fusion
echo └── cli/           # Command-line interface
echo ```
echo.
echo ---
echo.
echo ## Development
echo.
echo ```bash
echo # Run tests
echo pytest
echo.
echo # Format code
echo black astrocam_sync/
echo.
echo # Lint
echo ruff check astrocam_sync/
echo ```
echo.
echo ---
echo.
echo ## License
echo.
echo MIT License - See [LICENSE](LICENSE^)
echo.
echo ---
echo.
echo **Repository:** https://github.com/ShreyankV34/AstroEngine  
echo **Status:** Alpha - Core systems in development  
echo **Python:** 3.9-3.12
) > README.md
echo    Done!

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Copy Python files from artifacts
echo   2. Run: git add .
echo   3. Run: git commit -m "Initial project structure"
echo   4. Run: git push origin main
echo.
echo Press any key to open file explorer...
pause >nul
explorer .