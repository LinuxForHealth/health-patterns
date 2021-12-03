The setup.py in this directory is used to build the wheel during the gradle build.

The wheel is installed into the build venv and used to run testcases. The wheel is not
published and not used to in the docker image. 

The docker build does call setup.py to install the source (just doesn't use the wheel)

setup.py requires a few other build artifacts, and so it can't run from the source directory.
It is not at the root directory because some IDEs (pycharm) might think that they can invoke it
to setup the venv used by the IDE. This does not work because the build manages the 
property and dependency files.

For our purposes, it feels like we should remove setup.py and not bother building a wheel.
I believe we could avoid the need for setup.py when creating the docker image as well.
That would make the distribution process simpler.

However that change is more than I can take on, and so I just moved it out of the root to
avoid confusion. We have a build that works reasonably well, even if there might be some
ways to simplify the process.

