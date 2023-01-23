# Networking package for Qass Tools

Networking package to remotely control the Analyzer4D software.

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

For more information please see [Qass Tools Networking Documentation](http://developers.gitlab_pages.qass.net/qass_tools/qass_tools_networking)

## Functions, Methods and Variable Names

In python it's common practice to use snake case for the naming scheme. That means that functions and variables consisting of two consecutive words are linked by an underscore (`_`). Using the same notation makes code more readable. Excluded from this notation rule are functions and method that either mimic a C++ interface or implement an interface to a C++ implementation. This can also be alleviated by using aliases. Since functions are objects a class or module can have several references to this function with different names.
<br>
Example:
```py
def my_function():
   my_variable = "foo"

# This is an alias to my_function
myFunction = my_function
```
Classes use upper case letters for each consecutive word and **no** underscore. <br>
Example:
```py
class MyClass:
    def my_method():
        my_variable = "foo"

    # This is an alias to my_method
    myMethod = my_method
```

## Docstrings

In order to enable automatic generation and publishing of documentation we use the [Sphinx Standard](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html). Docstrings should not describe in detail how the function works or what the algorithm it implements does. However they should tell the user **how** to use this function and what the meaning of Inputs and Outputs are. For frequently used functions it's also a nice touch to add minimal examples in the docstrings about how to use this function.

Example Signature:
```py
"""[Short Summary]

[Extended Summary]

:param [ParamName]: [ParamDescription], defaults to [DefaultParamVal]
:type [ParamName]: [ParamType](, optional)
...
:raises [ErrorType]: [ErrorDescription]
...
:return: [ReturnDescription]
:rtype: [ReturnType]
"""
```

Example function:
```py
def foo(a, b = 1):
    """This is an example function that adds a and b together

    :raises ValueError: When a is less than zero

    :param a: a is the first participant in the sum
    :type a: int, float
    :param b: b is the second participant in the sum
    :param b: int, float, optional

    :return: The sum of the two values a and b
    :rtype: int, float
    """
    if a < 0:
        raise ValueError("a can't be less than zero")
    return a + b
```

Example class:
```py
class Foo(Bar):
    """The Foo class inherits from Bar and thus implements all it's methods

    Foo handles communication with Bar by utilizing the general Foo/Bar behaviour that Bar implements. This is done using some fancy implementations schemes that are too complicated for even me to understand. Of course this is just an example to provide an extended description so in the field this text should make a lot more sense when you write it.

    :param a: a is the first participant in the sum
    :type a: int, float
    :param b: b is the second participant in the sum
    :param b: int, float, optional

    """
    def __init__(self, a, b = 1):
        pass
```
## A new package version

### `.whl` file naming

A new `.whl` file is generally created through the pipeline. For that, it's important that the version in `setup.cfg` is incremented. Package names will be named after [Semantic Versioning Guidlines](https://semver.org/lang/de/). This means that every package contains MajorNumber.MinorNumber.Patch.Number in this order. A major update contains changes which will be not backward compatible. After a major update, MinorNumber and patch.Number will be set to zero. Minor updates are changes which add new functionailties that are compatible with previous version of same MajorNumber. Patch number will be updates by changes that fix bugs but adds no new functionailties.<br>

Example:
```
version = 0.1.1 -> version = 0.1.2 # no breaking changes, just some bug fixes

version = 0.1.1 -> version = 0.2.0 # adding new functionailties

version = 0.1.1 -> version = 1.0.0 # Major update which changes already existing functionailties
```
Whenever a new version is to be created, a Tag needs to be created in the repository. The name of the tag should be the version number and the release notes should cover the new additions to the package. The creation of the tag triggers the CI/CD to build and deploy the `.whl` file to the Package Registry in the Repository where it can be downloaded. 

### `Changelog.md` structure
Beside the normal Changelog that will be generated by parsing made changes to Git Tags notes or Git Release notes, a Changelog file has to be maintained manually. All entries should be in following format (in markdown):

Example:
```
## [MajorNumber.MinorNumber.PatchNumber] - YYYY-MM-DD

### Added

- ...

### Changed

- ...

### Removed

- ...

### Fixed

- ...

### Unreleased

Planned changes for next releases will be noted here. If you have any suggestions, please contact: developer@mail.net

- ...
```
