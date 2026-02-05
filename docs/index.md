# PGVA

`festo-pgva` is a python package which allows for driver like capabilites and usage over Festo's PGVA-1 device.  

![](./img/PGVA_Large_Picture.png)

## Installation

### From Codebase

Using a terminal interface, navigate to the directory where the code is stored and enter the following command:

```
pip install . -e
```

This will make the library locally available as an editable dependency and can be used in Python scripts with `import pgva`

### Official Packaged Releases

The latest released version of this package can be found on the package registry of this project
Install using pip:

```
pip install festo-pgva --index-url <private index location with auth key>
```

### From Git Repository

The festo-pgva source code can also be installed directly from Github. Access the repository here: [pgva Github](https://github.com/Festo-se/festo-pgva)

1. Clone the repository

```
git clone https://github.com/Festo-se/festo-pgva.git
```

2. Navigate to the clone destination directory

```
cd <destination>
```

3. Install with pip

```
pip install . 
```

### Installation Within Virtual Environment

To install within a virtual environment, either create one by using the following command

```
python -m venv <virtual environment name> 
```

Or if one already exists, activate using:

```
<virtual environment name>\Scripts\activate.bat
```

Once activated, use the instructions from the [Release](#release) section to install the package

### Installation With uv By Astral

If your software environment utilizes uv or if you wish to begin using uv for everything python follow the instructions below.  
If uv is not already installed on the host PC or device, it can be installed following the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/), or by using pip or pipx.  
For pip:

```
pip install uv
```

For pipx:

```
pipx install uv
```

Once uv is installed or if uv is already installed on the host PC or device, use the following command to install the PGVA package into an existing virtual environment.

```
uv pip install festo-pgva
```

To add the festo-pgva library to an existing project

```
uv add festo-pgva
```

## Pymodbus Dependency
The `festo-pgva` library uses the `pymodbus` library as its core communication dependency for both TCP/IP and Serial connections. To gain a better understanding of the fundamentals of PyModbus, please visit [PyModbus Homepage](https://www.pymodbus.org/), or for a more in-depth reading, please visit [PyModbus readthedocs](https://pymodbus.readthedocs.io/en/latest/). PyPI package information for PyModbus can also be found [here](https://pypi.org/project/pymodbus/).