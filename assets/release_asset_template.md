 
## An AppImage or BlueNotebook is available for this release on this page

```bash
# Download the BlueNotebook App as an AppImage from this page
# Make it Runnable
chmod +x BlueNotebook-4.2.5-x86_64.AppImage
# Run
./BlueNotebook-4.2.5-x86_64.AppImage
```

## A Flatpak bundle is available as a local .flatpak file

```bash
# Download bundle from this page
$ ls -al *.flatpak
BlueNotebook-V4.2.5.flatpak

# Install the local bundle
$ flatpak install --bundle --user BlueNotebook-V4.2.5.flatpak
```

## A docker image for BlueNotebook is available for this release on docker hub <https://hub.docker.com>

```bash
# get the docker image (558 MB)
docker pull jmdigne/bluenotebook:4.2.5
# Create mandatoruy directories on the host 
# By default, the Journal, Backup, and Configuration directories are located in the user directory under the name `bluenotebook_docker`. You can change the name of the `bluenotebook_docker` directory and choose the name and location you want, but make the same changes in the following lines of script.

mkdir -p ~/bluenotebook_docker/config \
         ~/bluenotebook_docker/BlueNotebookJournal \
         ~/bluenotebook_docker/BlueNotebookBackup
# Modify the ownership and access rights
chown -R $(id -u):$(id -g) ~/bluenotebook_docker
chmod -R u+rwX ~/bluenotebook_docker

# Run  the docker image
docker run -it --rm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v ~/bluenotebook_docker:/data \
    -v ~/bluenotebook_docker/config:/home/appuser/.config \
    -v ~/bluenotebook_docker/BlueNotebookJournal:/home/appuser/BlueNotebookJournal \
    -v ~/bluenotebook_docker/BlueNotebookBackup:/home/appuser/BlueNotebookBackup \
    --user=$(id -u):$(id -g) \
    jmdigne/bluenotebook:4.2.5
```


## A Github Container package for BlueNotebook is available for this release 

<https://github.com/lephotographelibre/BlueNotebook/pkgs/container/bluenotebook>

```bash
# Install from the command line

$ docker pull ghcr.io/lephotographelibre/bluenotebook:4.2.5

# Create mandatoruy directories on the host 
# By default, the Journal, Backup, and Configuration directories are located in the user directory under the name `bluenotebook_docker`. You can change the name of the `bluenotebook_docker` directory and choose the name and location you want, but make the same changes in the following lines of script.

mkdir -p ~/bluenotebook_docker/config \
         ~/bluenotebook_docker/BlueNotebookJournal \
         ~/bluenotebook_docker/BlueNotebookBackup
# Modify the ownership and access rights
chown -R $(id -u):$(id -g) ~/bluenotebook_docker
chmod -R u+rwX ~/bluenotebook_docker

# Run  the docker image
docker run -it --rm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v ~/bluenotebook_docker:/data \
    -v ~/bluenotebook_docker/config:/home/appuser/.config \
    -v ~/bluenotebook_docker/BlueNotebookJournal:/home/appuser/BlueNotebookJournal \
    -v ~/bluenotebook_docker/BlueNotebookBackup:/home/appuser/BlueNotebookBackup \
    --user=$(id -u):$(id -g) \
    ghcr.io/lephotographelibre/bluenotebook:4.2.5
```
## **Ubuntu/Debian** install from source files


`pyenv` is used to create an isolated Python environment based on Python 3.11.13.

```bash
curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
```

add these lines to `.bash_profile`

```bash
# User specific environment and startup programs
#
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"
```

add tothis line to `.bashrc`

```bash
eval "$(pyenv virtualenv-init -)"
```
Install the following librairies/packages

```bash
sudo apt-get update
sudo apt-get install git libcairo2-dev libpango-1.0-0 libgdk-pixbuf2.0-0
# for QtWebEngine
sudo apt-get install libasound2t64

# Launch Bluenotebook
git clone https://github.com/lephotographelibre/BlueNotebook.git
cd Bluenotebook
./run_bluenotebook.sh
```
You can add a launcher for this application using the `install.sh` script, which will create the `bluenotebook.desktop` file and register it correctly.


## **Windows 10/11** install from source files


`pyenv-win` is used to create an isolated Python environment based on Python 3.11.9. Therefore, install pyenv-win first: <https://github.com/pyenv-win/pyenv-win>

- Install `pyenv-win`

```powershell
PS C:\Users\xx> Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
Reopen PowerShell
PS C:\Users\xx>  pyenv --version
```

- Add the following to your PATH variable:

`C:\Users\xx\.pyenv\pyenv-win\bin` 
`C:\Users\xx\.pyenv\pyenv-win\shims`

- Add the `pyenv-virtualenv` plugin:

```powershell
git clone https://github.com/pyenv/pyenv-virtualenv.git "$(pyenv root)\plugins\pyenv-virtualenv"
```

- Install the required Cairo libraries (including `libcairo-2.dll`) by downloading and running the following installer:

  <https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases/download/2022-01-04/gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe>

- Add the bin directory containing `libcairo-2.dll` to your PATH environment variable:

  `C:\Program Files\GTK3-Runtime Win64\bin`

Open a PowerShell terminal.
```powershell
#Launch Bluenotebook
PS C:\Users\xx> git clone https://github.com/lephotographelibre/BlueNotebook.git
PS C:\Users\xx> cd Bluenotebook
PS C:\Users\xx> ./run_bluenotebook.bat
```



