# JSON Match Finder
JSON Match Finder (jmf) is a generalized Python 3 application used to match listings against openings via authenticated JSON API access. You can run searches for listings and searches for openings, but the ultimate goal is to find listings that match openings. The idea is that there are two databases, one we are calling "listings" and one we are calling "openings." We do not have access to the entire databases, so we cannot combine them locally and run nice SQL queries over them both. Furthermore, either they are split across entirely separate JSON APIs, or they coexist within one API that does not provide any way to find matches between the two databases. This makes it difficult to find common data between each database without software like jmf. jmf must be modified in order to be used depending on your specific JSON API implementation.

Included is a service that regularly queries the listings API to monitor for all new listings to find every listing that fills any opening. Also included is an interactive shell with ten commands. These commands allow you to login, logout, run all kinds of searches, review your matches, examine logs, run any arbitrary python code with custom utilization of the jmf library, run shell commands, and more.

JSON Match Finder as a package is made for Linux systems using systemd, but as a Python module it can be used in any system that has Python 3. It is possible without much difficulty to port the entire application with all of its functionality to any system, including Windows and OS X.

## Installation
If you use Arch Linux, you should navigate to the main directory where you will find the PKGBUILD and src directory. I have structured the repository in this manner rather than placing it in the AUR because the application requires modification to be useful. Install like so:
```
$ makepkg -si
```

If you use any other system, you can simply install the python module using these commands:
```
$ python setup.py sdist
# python setup.py
```
However, this only installs the module, not the complete application. If you would like a complete application, you should examine the PKGBUILD and adapt the build() and package() functions as needed to create a suitable package for your distribution.
## Usage
#### Service
In a system using systemd, assuming the package has been fully installed, activate the service using the following commands:
```
$ systemd --user start jmf.timer
$ systemd --user enable jmf.timer
```
#### Interactive Shell
Initialize the shell using the following command:
```
$ jmf
```
Each command is documented within the user interface, simply use the help command. For example:
```
> help login
```
For more information on the available commands, please see the [Wiki](https://github.com/dnut/JSON-Match-Finder/wiki).
## File Outline
#### Package Files

<big><pre>
[PKGBUILD](PKGBUILD)             Installs package in Arch Linux.
src/[setup.py](src/setup.py)         Installs Python module.
src/[jmf.py](src/jmf.py)           Executable for interactive session.
src/[jmf-service.py](src/jmf-service.py)   Executable used by service.
src/[jmf.timer](src/jmf.timer)        Systemd timer that runs service periodically.
src/[jmf.service](src/jmf.service)      Systemd service that runs jmf-service.py.
src/jmf/[\__init__.py](src/jmf/__init__.py)  Python module information.
src/jmf/[api.py](src/jmf/api.py)       Accesses JSON API.
src/jmf/[libjmf.py](src/jmf/libjmf.py)    Provides general functions used in jmf.
src/jmf/[service.py](src/jmf/service.py)   Operates continuous automated service.
src/jmf/[ui.py](src/jmf/ui.py)        Fully interactive command-line shell.
src/jmf/[config.py](src/jmf/config.py)    Build time configuration.
src/jmf/[session.py](src/jmf/session.py)   Manages user session and match storage.
</pre></big>


#### Application Files
```
~/.config/jmf/last_change.pkl  Used to prevent erasing new matches.
~/.config/jmf/session.pkl      Stores entire session, including user and matches.
~/.config/jmf/jmf.log         Logs all activity.
~/.config/jmf/match.log        Logs discovered matches.
```
