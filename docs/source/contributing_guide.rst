Overview
********
Welcome fellas, to the QASS TOOLS NETWORKING CONTRIBUTING GUIDE. Here you will find everything to know to start your individual path to contribute to this OpenSource Package.
QASS TOOLS NETWORKING member from the QASS GmbH OpenSource Projects, for flawless and optimized development with QASS GmbH products.
With this tool an external device control over the Analyzer4D will be possible via TCP. If you are new to QASS OpenSource products please see `QASS TOOLS DOCUMENTATION`_ for moer information 



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
    
    - Commands for the Analyzer4D Communication will be handeled trough the :mod:`AnalyzerRemote._value_parser()` method. This method takes your input param for the analyzer command and builds a message. This message will be sended and as soon as the repsonse is avaible, the response will be checked for errrors and returned.
    
    To use the :mod:`AnalyzerRemote._value_parser()` parse the kind of command protocol that will be used (mostly 'AppCmd'), the command kind as first param and the command specifications as second one.

    Example for adding a new function by using :mod:`AnalyzerRemote._value_parser()`
    
    .. code-block:: python
        :linenos:
        :emphasize-lines: 3

        def set_something(self, score_value:int=800):
            """ insert docstring in sphinx reStructedText style here"""
            self._value_parser(cmd="AppCmd", p1="setSomethingCommand", p2=f"{score_value}") 


    - If you need to include Paths that should be sended, escape the double quotes within the string to support whitespaces in Paths

    .. code-block:: python
        :linenos:

        print("\"insert/your/path/as/string\"")
        "insert/your/path/as/string" 

  .. tab-item:: SSHConnector
    
    - All commands will executed by an open channel terminal channel on connected device by paramiko. Each command gets his own channel. So mutiple terminal commands, another form of apramiko channel is needed.  


Testing
*******
Unfortunately, automatic testing pipelines are not supplied yet. But please stay curious. Testing is commming soon. 

Docstrings
**********
For documentation all QASS TOOLS projects use the reStructuredText (reST) Style from Sphinx. This will provide a automatic updating documentation by release.
Please see `Sphinx Style Guide`_ and  using `reStructuredText`_. New docstring should be written in sphinx one line style for enhancend type hinting 

.. tip:: Use Typehinting and IDE Extensions for enhancend performance

.. note:: Sphinx (with reST) provides a lot of directiveso include like the one you are reading ('.. note::').

General form of docstring:

.. code-block:: python
        :linenos:

        """ [General description]
            
        [Extended description]            

        :param *param_type* *param_name*: *param_description*
        :raises *exception_kind* *description why exception is raised* 
        """

Example:

.. code-block:: python
    :linenos:

    def set_something(self, score_value:int=800):
        """ Method to set something            

        :param int score_value: Sets the score value 
        :raises ValueError: Only score values in range from 0 to 1000 are supported.
        """
        if score_value > 1000 or score_value < 0:
            raise ValueError('Desired score value is not supported to set for something')
        self._value_parser(cmd="AppCmd", p1="setSomethingCommand", p2=f"{score_value}") 


.. _`Sphinx Style Guide`: https://documentation-style-guide-sphinx.readthedocs.io/en/latest/style-guide.html
.. _`reStructuredText`: https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html
.. _QASS TOOLS DOCUMENTATION: http://developers.gitlab_pages.qass.net/qass_tools/qass_tools_networking/index.html