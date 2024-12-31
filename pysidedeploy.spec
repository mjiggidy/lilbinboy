[app]

# title of your application
title = Lil' Bin Boy

# source file path
input_file = main.py

# directory where exec is stored
exec_directory = ./dist


[qt]

# comma separated path to qml files required
# normally all the qml files required by the project are added automatically
qml_files = 

# excluded qml plugin binaries
excluded_qml_plugins = 

# qt modules used. comma separated
modules = Widgets,Core,Gui

# qt plugins used by the application
plugins = egldeviceintegrations,platforminputcontexts,generic,xcbglintegrations,styles,iconengines,platforms,platforms/darwin,platformthemes,accessiblebridge,imageformats

[nuitka]

# mode of using nuitka. accepts standalone or onefile. default is onefile.
mode = standalone

# (str) specify any extra nuitka arguments
extra_args = --quiet --noinclude-qt-translations --disable-console

