# Developer Guide
#####[Back to main page] (#https://github.com/divsan93/tackle-container-advisor/tree/update_docs#TCA-Pipeline)
## Environment Setup
1. [Using Vagrant and VirtualBox](#Using-Vagrant-and-VirtualBox)
2. [Using Docker](#Using-Visual-Studio-Code-and-Docker)
3. [Manual Setup](#Installing-Python-3-manually)



You will need a Python 3.8 development environment with Docker in order to use this code and bring up the environment. There are three ways to do this.

## Using Vagrant and VirtualBox

For easy setup, you need to have [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/) installed. Then all you have to do is clone this repo and invoke vagrant using these commands:

```sh
git clone https://github.com/konveyor/tackle-container-advisor.git
cd tackle-container-advisor
vagrant up
```

This will bring up the development virtual machine (VM). Next you can `ssh` into the VM and change to the `/vagrant` directory and continue with the setup from there.

```sh
vagrant ssh
cd /vagrant
```

Once you are inside the virtual machine and in the `/vagrant` folder you can continue with the instructions to [Running the TCA Backend API](../README.md#running-the-tca-backend-api).

## Using Visual Studio Code and Docker

This project uses Docker and Visual Studio Code with the Remote Containers extension to provide a consistent repeatable disposable development environment for all of the developer.

You will need the following software installed:

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Visual Studio Code](https://code.visualstudio.com)
- [Remote Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension from the Visual Studio Marketplace

All of these can be installed manually by clicking on the links above or you can use a package manager like **Homebrew** on Mac of **Chocolatey** on Windows.

You can read more about creating these environments the my article: [Creating Reproducible Development Environments](https://johnrofrano.medium.com/creating-reproducible-development-environments-fac8d6471f35)

## Bring up the development environment

To bring up the development environment you should clone this repo, change into the repo directory, and start Visual Studio Code:

```bash
$ git clone git@github.com:konveyor/tackle-container-advisor.git
$ cd tackle-container-advisor
$ code .
```

Note that there is a period `.` after the `code` command. This tells Visual Studio Code to open the editor and load the current folder of files. Visual Studio Code will prompt you to **Reopen in a Container** and you should push this button. This will take a while the first time as it builds the Docker image and creates a container from it to develop in. After teh first time, this environment should come up almost instantaneously.


Once the environment is loaded you should be placed at a `bash` prompt in the `/app` folder inside of the development container. This folder is mounted to the current working directory of your repository on your computer. This means that any file you edit while inside of the `/app` folder in the container is actually being edited on your computer. You can then commit your changes to `git` from either inside or outside of the container.

You can continue with the instructions to [Running the TCA Backend API](../README.md#running-the-tca-backend-api).

## Installing Python 3 manually

This is not recomeded because everyones development environment could potentially be a little different (especially bwteeen Windows and Mac and Linux) but if you don't ant to use the two previous options, then this is the only other choice.

### Install sqlite3

Go to [https://www.sqlite.org/download.html](https://www.sqlite.org/download.html) and download and install SQLite3.

### Installing Anaconda3

Go to [https://docs.anaconda.com/anaconda/install/](https://docs.anaconda.com/anaconda/install/) and download and install Anaconda3

### Create a Conda virtual environmment with python3.8

```bash
conda create --name <env-name> python=3.8
conda activate <env-name>
```

### Clone the TCA Repository from git as follows and enter into the parent folder

```bash
git clone https://github.com/konveyor/tackle-container-advisor.git
cd tackle-container-advisor
```

You can continue with the instructions to [Running the TCA Backend API](../README.md#running-the-tca-backend-api).
