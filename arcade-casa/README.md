# Arcade CASA Containers

The source of ARCADE CASA containers and their build recipes are contained in this directory.

This document describes how to modify existing CASA containers and add new CASA containers to ARCADE.

Please refer to the [skaha](https://github.com/opencadc/skaha/tree/master/skaha-containers) repository for details of the requirements for running containers in the skaha ARCADE desktop environment.

## Modifying a CASA container

To modify a CASA container is to modify the Dockerfile of a given version of CASA.  To make a modification, one would follow these steps:
1. fork this github repository
1. make the desired modifications to a CASA container in your fork
1. build a new container image with the modifications
1. test the new container image (more below)
1. when satisfied, issue a pull request to this github repository

To build CASA containers in a given version set, follow these steps:

1. `cd` into the relevant folder with the build files 
1. execute `make`

## Creating a new CASA container
Creating a new version of a casa container follows the same process as modifying an existing CASA container, except that a new set of build instructions (Dockerfile, etc) are created and added to the forked canfar/arcade.git repository.

## Publishing
CASA images are published in the skaha user image registry.  Details on this registry are described in the [skaha container](https://github.com/opencadc/skaha/tree/master/skaha-containers "skaha") section in opencadc/skaha.git.

The image registry contains a number of projects, one of which is for CASA containers.  Users who wish to be involved with container maintenance and publishing can be given permission to contribute to this project.  With this permission, users may 'push' new versions of CASA to the repository that will be then made available from within ARCADE.

## Testing
Before publishing a new or modified CASA image testing should be done to ensure it works as expected.  Some testing can be done by using `docker` to run the image.  However, docker will not be able to provide a graphical display of CASA windows.  That testing must be done in ARCADE itself.

To test a CASA image in ARCADE, users can push the image to a 'testing sandbox' project in the image registry.  The images in this registry will not be displayed in the ARCADE menu, but can still be launched using the API of skaha for testing.  Users can iterate by making corrections to the image and overwritting the image in the sandbox.  Once testing is complete, the last version of the image can be published to the repository project that contains the images displayed in the ARCADE menu.

### Functional testing

The following steps can be performed in ARCADE to test that a container was built correctly.
1. Type the `id` command and ensure that user name is displayed.
2. Type the following and ensure that information on ADMIT is displayed
`source /opt/admit/admint_start.sh`
`admit`
3. Run the `casa` command and ensure that the logging window opens.
4. Within CASA, type `import admit` and ensure that there is no error.
5. Exit CASA. Run the `casaviewer` command and ensure that casaviewing windows are displayed.
6. Exit `casaviewer` and exit the xterm.

## Remaining Work
* The drop-down menu in ARCADE that shows the list of available CASA containers is currently static.  It should be changed to be the list of CASA containers (and others) that are available to the current user in the image registry.
