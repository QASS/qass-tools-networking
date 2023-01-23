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

or to directly address analyzer_socket:

```py
from qass.tools.networking.analyzer_socket import AnalyzerRemote 
```

For more information please see <http://developers.gitlab_pages.qass.net/qass_tools/qass_tools_networking>
