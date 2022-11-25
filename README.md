# Networking package for Qass Tools

Networking package to remotely control the ANalyzer4D software.

## Install as developer

Navigate a terminal with the current working directory to the repository where the `setup.py` file is:
Note: Installation directory is a system-owned directory. Need for administrator or "root" account.

```sh
pip install --user --no-deps -e .
```

## How to import the networking package

```py
from qass.tools import networking
```

or

```py
from qass.tools.networking.analyzer_socket import AnalyzerCmd 
```
