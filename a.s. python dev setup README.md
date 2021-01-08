# Notes

## Installation

- Dev Computer: Follow these two documents:

  - [Python 3](https://opensource.com/article/19/5/python-3-default-mac)

Okay, great! The Homebrew maintainers have updated the default Python bottle to point to the latest release. Since the Homebrew maintainers are more dependable at updating the release than most of us, we can use Homebrew's version of Python 3 with the following command:

```sh
$ brew update && brew upgrade python
# a.s. installed:
$ pyenv install 3.9.0
$ pyenv global 3.9.0

# a.s. if something is missing, check between those two articles...
# Be sure to keep the $() syntax in this command so it can evaluate
$ $(pyenv which python3) -m pip install virtualenvwrapper
```

Now we want to point our alias (from above) to the copy of Python that Homebrew manages:

# If you added the previous alias, use a text editor to update the line to the following

```sh
alias python=/usr/local/bin/python3
```

- [Python Virtual Env](https://opensource.com/article/19/6/python-virtual-environments-mac)

- $ mkvirtualenv test1

```sh
  # Using base prefix '/Users/moshe/.pyenv/versions/3.7.3'
  # New python executable in /Users/moshe/.virtualenvs/test1/bin/python3
  # Also creating executable in /Users/moshe/.virtualenvs/test1/bin/python
  # Installing setuptools, pip, wheel...
  # done.
```

- (test1)$ mkvirtualenv test2
- (test1)$ ls $WORKON_HOME

The deactivate command exits you from the current environment.

### Recommended practices

You may already set up your long-term projects in a directory like ~/src. When you start working on a new project, go into this directory, add a subdirectory for the project, then use the power of Bash interpretation to name the virtual environment based on your directory name. For example, for a project named "pyfun":

```sh
$ mkdir -p ~/src/pyfun && cd ~/src/pyfun
$ mkvirtualenv $(basename $(pwd))
# we will see the environment initialize
(pyfun)$ workon
pyfun
test1
test2
(pyfun)$ deactivate
$
```

Whenever you want to work on this project, go back to that directory and reconnect to the virtual environment by entering:

```sh
$ cd ~/src/pyfun
(pyfun)$ workon .
```

Since initializing a virtual environment means taking a point-in-time copy of your Python version and the modules that are loaded, you will occasionally want to refresh the project's virtual environment, as dependencies can change dramatically. You can do this safely by deleting the virtual environment because the source code will remain unscathed:

```sh
$ cd ~/src/pyfun
$ rmvirtualenv $(basename $(pwd))
$ mkvirtualenv $(basename $(pwd))
```

This method of managing virtual environments with pyenv and virtualwrapper will save you from uncertainty about which version of Python you are running as you develop code locally. This is the simplest way to avoid confusion—especially when you're working with a larger team.
