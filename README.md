# PGVA


[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)



`festo-pgva` is a python package which allows for driver like capabilites and usage over Festo's PGVA-1 device.

Documentation can be found here: https://festo-se.github.io/festo-pgva/

Examples can be found here: https://github.com/Festo-se/festo-pgva/tree/main/examples

## Installation

### From codebase

Identify the relative path to the directory where the code is stored and using pip type in the following command:

```
pip install <relative path> -e
```
or using `uv`
```
uv add "festo-pgva @ <relative path>"
```

This will package the library locally and can be used as regular imports

### Release (PENDING)

The lastest released version of this package can be installed from PyPI
Install using pip:

```
pip install festo-pgva
```
or using `uv`
```
uv add festo-pgva
```


### From Git repository

The festo-pgva source code can also be installed directly from Github.
```
pip install git+https://github.com/Festo-se/festo-pgva.git
```
or using [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
```
uv add "festo-pgva @ git+https://github.com/Festo-se/festo-pgva.git"
```

Or as an editable dependency with a local copy of the source code: 

1. Clone the repository

```
git clone https://github.com/Festo-se/festo-pgva.git <destination-directory>
```

2. Navigate to the clone destination directory

```
cd <destination>
```

3. Install with pip

```
pip install . -e
```

## Running examples

Use the following to run the example code:
```
PGVA_IP="192.168.0.23" uv run examples/example_pgva_print_driver_info.py
```
```
PGVA_IP="192.168.0.23" uv run examples/example_pgva_read_sensor_data.py
```
```
PGVA_IP="192.168.0.23" uv run examples/example_pgva_run_timed_pressure.py
```
```
PGVA_IP="192.168.0.23" uv run examples/example_pgva_run_timed_vacuum.py
```
```
PGVA_IP="192.168.0.23" uv run examples/example_pgva_set_internal_chambers.py
```
```
PGVA_IP="192.168.0.23" uv run examples/example_pgva_set_output_pressure.py
```
```
PGVA_IP="192.168.0.23" uv run examples/example_pgva_set_output_vacuum.py
```
```
PGVA_IP="192.168.0.23" uv run examples/example_pgva_startup.py
```
