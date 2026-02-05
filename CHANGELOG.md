# Changelog

All relevant changes to the PGVA driver package will be documented in this file.

The format is derived from [Keep A Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/)


## [Unreleased]
### Added

Nothing

### Changed

Nothing

### Deprecated

Nothing

### Removed

Nothing

### Fixed

Nothing

### Security 

Nothing

### Performance

Nothing

### Other

Nothing

## [0.1.9] - 2026-01-19

### Added

Nothing

### Changed

- Update PGVA to use pymodbus 3.11.4 

### Deprecated

Nothing

### Removed

Nothing

### Fixed

Nothing

### Security 

Nothing

### Performance

Nothing

### Other

Nothing

## [0.1.0] - [0.1.8] - 2022-2026
### Added

- Unify existing Modbus-based PGVA support libraries into one development stream

- Generate documentation using mkdocs + gitlab pages. API documentation generated automatically usage Python docstrings.

- Separate out unified interface for PGVA commands from the implmentation details in the  communication backends (ModbusTCP vs. ModbusSerial)

- Make PGVA communication backend mode dynamically generatable based on a config passed in at runtime 

- Separate out ENUM-type register mappings from communication backend for reliable usage and modification

- Initial pass at tests -- to be developed further in concert with physical infrastructure to test on actual dev-dependencies

- Apply Gitlab CI to test, package, and deplot to Gitlab native PyPI

- Construct usage examples and make usage example configurable usage environment variables for input parameters

- Update project to src directory structure

- Implement usage of modern python tooling, using ruff for linting/formatting and uv for project management and build/deploy

- Rename library install name to "festo-pgva"

### Changed

Nothing

### Deprecated

Nothing

### Removed

Nothing

### Fixed

Nothing

### Security 

Nothing

### Performance

Nothing

### Other

Nothing
