Overview
********
Welcome fellas, to the QASS TOOLS NETWORKING CONTRIBUTING GUIDE. Here you will find everything to know to start your individual path to contribute to this OpenSource Package.
QASS TOOLS NETWORKING member from the QASS GmbH OpenSource Projects, for flawless and optimized development with QASS GmbH products.
With this tool an external device control over the Analyzer4D will be possible via TCP. If you are new to QASS OpenSource products please see `QASS TOOLS DOCUMENTATION`_ for more information 



Otherwise is nice to see you here and we are enlighted for your next and probably first contribution!

I don't want to read this whole thing, I just have a question!!!
****************************************************************

.. note:: Please don't file an issue to ask a question. You'll get faster results by using the resources below.

Eitherwise contact okowollik@qass.net and submit your question or try to ask via the Mattermost Channel "QASS TOOLS", where the community can help you.


How do I Contribute?
********************

Never contributed? New to Git and Python? Don't know where to start? No problem, we got your bag. Heres a simple rundown.

#. Find a bug, suggesting enhacement or being curious for more options
    
    * Submit a GitLab report/issue for your specific point. think of using a clear and descriptive title
    * Describe the exact steps to reproduce the problem
    * If possible provide Examples: Traceback stack, Terminal Output, Results, etc 
    * Explain which beahviour you expected to see (and if not obvious why)
    * Include more specific information depending on your problem state, e.g. if problem is related to performance or memory, include CPU profil screenshot
    * Include information about your configuration and environment 

#. Create a new branch related to your issue
    
    * Clone the repository to your local machine
    * Create a new branch by "git checkout -b branch-name"
    * Use a descriptive branch name as features/issue, fix/issue, etc

#. Make your changes and extensions
#. Test your functionalities
#. Write a testing function for your changes if needed
#. Add a docstring
#. Stage your changes ("git add ." for all files to stage)
#. Commit by "git commit -m "description-of-changes" "
#. Push your ready to merge branch into the remote repository by "git push origin branch-name"
#. Create a merge Request
    
    * Link your request to the issue (e.g. ... resolved #4352)
    * Make a short description of what you Changend
    * Describe to your reviwer any issues that might happen and remaining questions you have 
    * Provide a simple example for the reviewer to test your extensions and describe the ouput or ouput behaviour for your changes

#. Now just wait for a project member to observe your changes, and check for errors. No worries if the reviewer will have annotations. Reviewer are there to help and fix problems.
#. If everything is alright the merge request will be accepted, the remote branch will be deleted and within the next release, you will have made your first contribution. Congratiulations!

Important notes for functionality
*********************************

For any contributor there are a few important points to take into consideration by contributing new functionalities. 

.. tab-set::
  .. tab-item:: AnalyzerRemote
    
    - :mod:`AnalyzerRemote._value_parser()`

    Commands for the Analyzer4D Communication will be handeled trough the :mod:`AnalyzerRemote._value_parser()` method. This method takes your input param for the analyzer command and builds a message. This message will be send and as soon as the repsonse is avaible, the response will be checked for errrors and returned.
    
    To use the :mod:`AnalyzerRemote._value_parser()` parse the kind of command protocol that will be used (mostly 'AppCmd'), the command kind as first param and the command specifications as second one.

    Example for adding a new function by using :mod:`AnalyzerRemote._value_parser()`
    
    .. code-block:: python
        :linenos:
        :emphasize-lines: 3

        def set_something(self, score_value:int=800):
            """ insert docstring in sphinx reStructedText style here"""
            self._value_parser(cmd="AppCmd", p1="setSomethingCommand", p2=f"{score_value}") 


    - `Paths`

    If you need to include Paths that should be sended, escape the double quotes within the string to support whitespaces in Paths

    .. code-block:: python
        :linenos:

        print("\"insert/your/path/as/string\"")
        "insert/your/path/as/string" 

  .. tab-item:: SSHConnector
    
    - One channel creation
    
    All commands will executed by an open channel terminal channel on connected device by paramiko. Each command gets his own channel. So mutiple terminal commands, another form of apramiko channel is needed.  


Testing
*******
Unfortunately, automatic testing pipelines are not supplied yet. But please stay curious. Testing is commming soon. 

Documentation
*************
Documentation will be generated automatically if docstrings are build after Contributional Guidlines. Please note that all added classes have to be extend in documentation manually.Beside the notes that will be generated by parsing made changelogs to Git Tags notes or Git Release notes, a Changelog rst-file has to be maintained manually for documentation. Entries are made in rst file and should contain:

- Version number
- Date
- Analyzer version
- Made Changes
- New Features
- Fixes


Functions, Methods and Variable Names
=====================================
In python it's common practice to use snake case for the naming scheme. That means that functions and variables consisting of two consecutive words are linked by an underscore (`_`). Using the same notation makes code more readable. Excluded from this notation rule are functions and method that either mimic a C++ interface or implement an interface to a C++ implementation. This can also be alleviated by using aliases. Since functions are objects a class or module can have several references to this function with different names.

Example:

.. code-block:: python
    :linenos:

    def my_function():
        my_variable = "foo"

    # This is an alias to my_function
    myFunction = my_function

Classes use upper case letters for each consecutive word and **no** underscore.
Example:

.. code-block:: python
    :linenos:

    class MyClass:
        def my_method():
            my_variable = "foo"

        # This is an alias to my_method
        myMethod = my_method

Docstrings
==========
For documentation all QASS TOOLS projects use the reStructuredText (reST) Style from Sphinx. This will provide a automatic updating documentation by release.
Please see `Sphinx Style Guide`_ and  using `reStructuredText`_. New docstring should be written in sphinx one line style for enhancend type hinting. 
Docstrings should not describe in detail how the function works or what the algorithm it implements does. However they should tell the user **how** to use this function 
and what the meaning of Inputs and Outputs are. For frequently used functions it's also a nice touch to add minimal examples in the docstrings about how to use this function.

.. tip:: Use Typehinting and IDE Extensions for enhancend performance

.. note:: Sphinx (with reST) provides a lot of directiveso include like the one you are reading ('.. note::').

General signature of docstring:

.. code-block:: python
        :linenos:

        """ [General description]
            
        [Extended description]            

        :param *param_type* *param_name*: *param_description*
        :raises *exception_kind* *description why exception is raised* 
        :return *return_type*: *return_description*
        """

Example:

.. code-block:: python
    :linenos:

    def set_something(self, score_value:int=800)    ->bool:
        """ Method to set something            

        :param int score_value: Sets the score value 
        :raises ValueError: Only score values in range from 0 to 1000 are supported.
        :return bool: Flag if method succeed
        """
        if score_value > 1000 or score_value < 0:
            raise ValueError('Desired score value is not supported to set for something')
        error_message = self._value_parser(cmd="AppCmd", p1="setSomethingCommand", p2=f"{score_value}") 
        if not error_message:
            return true


Releasing a new package version
*******************************

A new `.whl` file is generally created through the pipeline. For that, it's important that the version in `setup.cfg` is incremented. Package names will be named after `Semantic Versioning Guidlines`__. This means that every package contains: 

``MajorNumber.MinorNumber.PatchNumber`` 

in this order. A major update contains changes which will be not backward compatible. After a major update, MinorNumber and patch.Number will be set to zero. Minor updates are changes which add new functionailties that are compatible with previous version of same MajorNumber. Patch number will be updates by changes that fix bugs but adds no new functionailties.

Example:

::

    version = 0.1.1 -> version = 0.1.2 # no breaking changes, just some bug fixes
    version = 0.1.1 -> version = 0.2.0 # adding new functionailties
    version = 0.1.1 -> version = 1.0.0 # Major update which changes already existing functionailties


Whenever a new version is to be created, a Tag needs to be created in the repository first. The name of the tag should be the version number and the release notes should cover the new additions to the package. The creation of the tag triggers the CI/CD to build and deploy the `.whl` file to the Package Registry in the Repository where it can be downloaded.

.. _`Sphinx Style Guide`: https://documentation-style-guide-sphinx.readthedocs.io/en/latest/style-guide.html
.. _`reStructuredText`: https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html
.. _QASS TOOLS DOCUMENTATION: http://developers.gitlab_pages.qass.net/qass_tools/qass_tools_networking/index.html
.. _SVGuidlines: https://semver.org/lang/de/
__ SVGuidlines_