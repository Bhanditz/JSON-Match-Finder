# What
What is a generalized Python 3 application used to match listings against openings via authenticated JSON API access. You can run searches for listings and searches for openings, but the ultimate goal is to find listings that match openings. The idea is that there are two databases, one we are calling "listings" and one we are calling "openings." We do not have access to the entire databases, so we cannot combine them locally and run nice SQL queries over them both. Furthermore, either they are split across entirely separate JSON APIs, or they coexist within one API that does not provide any way to find matches between the two databases. This makes it difficult to find common data between each database without software like What. What must be modified in order to be used depending on your specific JSON API implementation. What is what you make it.

Included is a service that regularly queries the listings API to monitor for all new listings to find every listing that fills any opening. Also included is an interactive shell with ten commands. These commands allow you to login, logout, run all kinds of searches, review your matches, examine logs, run any arbitrary python code with custom utilization of the What library, run shell commands, and more.

What as a package is made for Linux systems using systemd, but as a Python module it can be used in any system that has Python 3. It is possible without much difficulty to port the entire application with all of its functionality to any system, including Windows and OS X.

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
$ systemd --user start what.timer
$ systemd --user enable what.timer
```
#### Interactive Shell
Initialize the shell using the following command:
```
$ what
```
Each command is documented within the user interface, simply use the help command. For example:
```
> help login
```
For more information on the available commands, please see the [Wiki](https://github.com/dnut/what/wiki).
## File Outline
#### Package Files

<big><pre>
[PKGBUILD](PKGBUILD)              Installs package in Arch Linux.
src/[setup.py](src/setup.py)          Installs Python module.
src/[what.py](src/what.py)           Executable for interactive session.
src/[what-service.py](src/what-service.py)   Executable used by service.
src/[what.timer](src/what.timer)        Systemd timer that runs service periodically.
src/[what.service](src/what.service)      Systemd service that runs what-service.py.
src/what/[\__init__.py](src/what/__init__.py)  Python module information.
src/what/[api.py](src/what/api.py)       Accesses JSON API.
src/what/[libwhat.py](src/what/libwhat.py)   Provides general functions used in What.
src/what/[service.py](src/what/service.py)   Operates continuous automated service.
src/what/[ui.py](src/what/ui.py)        Fully interactive command-line shell.
src/what/[config.py](src/what/config.py)    Build time configuration.
src/what/[session.py](src/what/session.py)   Manages user session and match storage.
</pre></big>


#### Application Files
```
~/.config/what/last_change.pkl  Used to prevent erasing new matches.
~/.config/what/session.pkl      Stores entire session, including user and matches.
~/.config/what/what.log         Logs all activity.
~/.config/what/match.log        Logs discovered matches.
```
