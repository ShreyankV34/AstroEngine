# 🌌 AstroEngine (AstroCamSync)

**Real-time, GPS-synced astrophotography decision engine**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)

---

## What Is This?

AstroCamSync is a **physics-driven decision engine** that computes optimal astrophotography camera settings by synchronizing:

1. **Celestial mechanics** - Time, coordinates, object motion
2. **Observer location** - GPS positioning, UTC→LST conversion
3. **Camera sensor physics** - Noise models, ISO behavior, dynamic range
4. **Real-time environment** - SQM sensors, weather APIs, light pollution
5. **Decision fusion** - Judgment-producing recommendations with confidence

This is a **deterministic, explainable instrument** for serious astrophotography.

---

## ✅ Status: Production-Ready Core Systems

**7,500+ lines of observatory-grade code implemented!**

**Core Systems (Complete):**
- ✅ **Time system** (552 lines) - Full Meeus algorithms for UTC→JD→GST→LST
- ✅ **Coordinate transforms** (665 lines) - Equatorial↔Horizontal, airmass, refraction
- ✅ **Celestial mechanics** (507 lines) - NPF rule, twilight, moon phase, extinction
- ✅ **Exposure engine** (566 lines) - SNR optimization, stacking, diffraction limits

**Databases (Complete):**
- ✅ **Camera database** (1,928 lines) - 30+ cameras (Sony, Canon, Nikon, Fuji)
- ✅ **Smartphone database** (336 lines) - 6 flagship phones (iPhone, Samsung, Pixel)
- ✅ **Target catalog** (1,844 lines) - 50+ targets (Milky Way, galaxies, nebulae, planets)

**Environmental Conditions (Complete):**
- ✅ **Light pollution** (405 lines) - Complete Bortle scale, sky quality assessment
- ✅ **Moon impact** (436 lines) - Phase calculations, Krisciunas-Schaefer model

**Next Phase:**
- 🔄 Decision fusion engine
- 🔄 Multi-target session planner
- 🔄 CLI interface
- 🔄 Real-time SQM sensor integration
- 🔄 Comprehensive test suite (95% coverage target)

---

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/ShreyankV34/AstroEngine.git
cd AstroEngine

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install package
pip install -e .
```

---

## Architecture

```
astrocam_sync/
├── core/          # Astronomical calculations
│   ├── time.py          # UTC→LST conversions
│   ├── coordinates.py   # RA/Dec→Alt/Az
│   ├── astronomy.py     # Celestial mechanics
│   └── engine.py        # Exposure calculations
├── targets/       # Target database
├── cameras/       # Camera specifications
├── conditions/    # Environmental data
├── sync/          # Decision fusion
└── cli/           # Command-line interface
```

---

## Development

```bash
# Run tests
pytest

# Format code
black astrocam_sync/

# Lint
ruff check astrocam_sync/
```

---

## License

MIT License - See [LICENSE](LICENSE)

---

**Repository:** https://github.com/ShreyankV34/AstroEngine  
**Status:** Alpha - Core systems in development  
**Python:** 3.9-3.12
