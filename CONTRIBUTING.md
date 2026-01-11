# Contributing to AstroCamSync

Thank you for your interest in contributing to AstroCamSync! This document provides guidelines for contributing to this observatory-grade astrophotography decision engine.

## Code of Conduct

This project adheres to professional engineering standards. All contributors are expected to:
- Write clear, well-documented code
- Follow established architectural patterns
- Maintain test coverage above 90%
- Respect the scientific accuracy of astronomical calculations

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- Virtual environment tool (venv or conda)

### Installation

```bash
# Clone repository
git clone https://github.com/ShreyankV34/AstroEngine.git
cd AstroEngine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write code following PEP 8 style guidelines
- Add type hints to all function signatures
- Write docstrings using Google style
- Add unit tests for new functionality

### 3. Run Quality Checks

```bash
# Format code
black astrocam_sync/

# Lint code
ruff check astrocam_sync/

# Type check
mypy astrocam_sync/

# Run tests
pytest

# Check coverage
pytest --cov=astrocam_sync --cov-report=html
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: brief description of changes"
```

**Commit Message Format:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions or modifications
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `chore:` - Maintenance tasks

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Standards

### Python Style

- Follow PEP 8
- Use Black for formatting (line length: 88)
- Use Ruff for linting
- Use MyPy for type checking

### Documentation

All public APIs must have docstrings:

```python
def calculate_airmass(altitude_deg: float) -> float:
    """
    Calculate atmospheric airmass using Rozenberg formula.

    Args:
        altitude_deg: Object altitude in degrees above horizon

    Returns:
        Airmass value (dimensionless). Returns inf for alt < 0.

    Reference:
        Rozenberg, G.V. (1966). "Twilight: A Study in Atmospheric Optics"

    Example:
        >>> calculate_airmass(30.0)
        2.0
        >>> calculate_airmass(90.0)
        1.0
    """
```

### Testing

- Maintain minimum 90% code coverage
- Write unit tests for all new functions
- Write integration tests for new features
- Use pytest fixtures for common setups

Example test:

```python
def test_utc_to_julian_date():
    """Test UTC to Julian Date conversion."""
    # J2000.0 epoch
    dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    jd = utc_to_julian_date(dt)
    assert abs(jd - 2451545.0) < 1e-6
```

## Scientific Accuracy

### Astronomical Calculations

When implementing astronomical algorithms:

1. **Cite your sources**
   - Reference standard texts (Meeus, USNO Circular 179, etc.)
   - Include equation numbers where applicable
   - Document accuracy limitations

2. **Validate against known values**
   - Use published ephemerides for validation
   - Test against USNO data
   - Compare with established software (Stellarium, PyEphem)

3. **Document precision**
   - State expected accuracy (e.g., "accurate to ±0.01°")
   - Note limitations (e.g., "valid for years 1900-2100")

### Camera Specifications

When adding camera data:

1. Use manufacturer specifications
2. Cross-reference with DXOMark when available
3. Include measurement conditions (temperature, ISO)
4. Document sources

## Architecture Guidelines

### Module Organization

```
astrocam_sync/
├── core/          # Pure astronomical calculations (no I/O)
├── targets/       # Target catalogs and ephemerides
├── cameras/       # Camera specifications and models
├── conditions/    # Environmental data (I/O allowed)
├── sync/          # Decision fusion engine
├── cli/           # User interface (I/O allowed)
└── utils/         # Shared utilities
```

### Dependency Rules

- `core/` - No external API calls, pure calculations
- `targets/` - May use ephemeris services
- `cameras/` - Database access only
- `conditions/` - May call weather APIs, read sensors
- `sync/` - Coordinates other modules
- `cli/` - User interaction only

### Error Handling

```python
from astrocam_sync.utils.validators import validate_latitude

def calculate_position(lat: float, lon: float):
    """Calculate observer position."""
    # Validate inputs
    lat = validate_latitude(lat)
    lon = validate_longitude(lon)

    try:
        # Calculation
        result = complex_calculation(lat, lon)
    except ValueError as e:
        raise ValueError(f"Invalid coordinates: {e}")

    return result
```

## Adding New Features

### New Camera

1. Add specifications to `cameras/database.py`
2. Include sensor data in `cameras/sensors.py`
3. Add noise model in `cameras/noise.py`
4. Write tests in `tests/test_cameras.py`
5. Update documentation in `docs/cameras.md`

### New Target

1. Add to appropriate catalog in `targets/`
2. Include all required metadata (RA, Dec, size, brightness)
3. Add ephemeris if moving target
4. Write tests in `tests/test_targets.py`
5. Update documentation in `docs/targets.md`

### New Sensor Type

1. Create driver in `conditions/sensors/`
2. Implement protocol in `conditions/sensors/protocol.py`
3. Add calibration routine
4. Write hardware tests (use mocks for CI)
5. Document in `docs/sensors.md`

## Pull Request Process

1. **Self-review your code**
   - Run all quality checks
   - Verify test coverage
   - Update documentation

2. **Create PR with description**
   - Summarize changes
   - Reference related issues
   - Include test results

3. **Address review feedback**
   - Respond to all comments
   - Make requested changes
   - Update PR description if scope changes

4. **Merge requirements**
   - All tests passing
   - Code coverage ≥ 90%
   - All checks passing (Black, Ruff, MyPy)
   - At least one approval
   - Up to date with main branch

## Release Process

Releases follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking API changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Create an issue with template
- **Features**: Propose in GitHub Discussions first

## Recognition

Contributors are recognized in:
- CHANGELOG.md for each release
- README.md contributors section
- Git commit history

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping build observatory-grade software!**
