# Networking package for Qass Tools

Networking package to remotely control the Analyzer4D software.

[Qass Tools Networking Documentation](http://developers.gitlab_pages.qass.net/qass_tools/qass_tools_networking)

## Install as developer
Either download the newest .whil file from [Qass Tools Networking Gitlab Packages](https://git.qass.net/developers/qass_tools/qass_tools_networking/-/packages) and install the downloaded package with your local pip manager:

```sh
pip install <path-to-.whl-file>
```

or

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
from qass.tools.networking.analyzer_socket import AnalyzerRemote, ExactSamplerates16Bit
```
or address analyzer_ssh as:

```py
from qass.tools.networking.analyzer_ssh import SSHConnector 
```

For more information please see [Qass Tools Networking Documentation](http://developers.gitlab_pages.qass.net/qass_tools/qass_tools_networking)

## Contribution
You want to contributing to your new favorit open source project? We want that too! So for a flawless start, go checkout our [Contributing Guidlines](http://developers.gitlab_pages.qass.net/qass_tools/qass_tools_networking/contributing_guide.html)
