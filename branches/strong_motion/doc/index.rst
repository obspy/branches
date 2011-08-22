.. strong motion analyser documentation master file, created by
   sphinx-quickstart on Thu Aug 04 14:24:28 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Welcome to the Strong Motion Analyser documentation!
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

Here are a few lines of documentation on the Strong Motion Analyser GUI, 
a thin wrapper around one of the Fortran programs used to analyse strong motion 
records at GNS Science, New Zealand. 

.. image:: start_window.JPG
   :scale: 50 %

Installation
------------
To install the package under Windows go to ``I:\SEISMO\yannikb\strong_motion_analyser`` and start the ``setup.exe`` installer. 
This will install Python 2.6 and all the dependencies necessary to run the program. The installer will call several other installers 
and if you don't have special preferences, you can always accept the installers' suggestions for directories etc.
   
.. For Linux, make sure that Python 2.6 and the  ``distribute`` package are installed and then install the file 
.. ``sm_analyser-0.x.x-py2.6.egg`` (located in the directory mentioned above) on the command line:
.. >>>easy_install sm_analyser-0.x.x-py2.6.egg  

After installing the ``sm_analyser`` package you will have a script called ``sm_gui.py`` in the ``Scripts`` directory of 
your local Python installation.

You finally have to make sure that you have the Fortran program ``esvol2m_special.exe`` (written and maintained by Jim Cousins) together
with the input file ``filt_special.dat``. The required format for each line of the input file in Fortran syntax
is ``(a,4f6.0,2i6,2i2,1x,3i2,f5.2,i12,i12,f12.0,f12.0)`` and the entries are:
``filename; cutoff frequency high pass filter; corner frequency high pass filter; cutoff frequency low pass filter; 
corner frequency low pass filter; ?? ; event date; event time; magnitude??; number of points; starting index??; latitude of accelerometer; 
longitude of accelerometer``
You can find an example of the input file under ``I:\SEISMO\yannikb\strong_motion_analyser``.

The Fortran program further needs to have the network drive ``nickel.geonet.org.nz\smdata`` mounted as a local drive under ``S:\`` to 
access the raw data. You can find a copy of the Fortran routines under ``I:\SEISMO\yannikb\strong_motion_analyser\Fortran_programs``. 
To compile them first copy the directory and then make sure that you have a Fortran compiler installed. If you have gfortran from the MinGW
project (http://www.mingw.org/) together with GNU's make for windows (http://gnuwin32.sourceforge.net/packages/make.htm) installed you can
open a command prompt, ``cd`` to the directory where you copied the Fortran routines to and then type ``make``. To check whether your 
installation is working you can type ``esvol2m_special.exe`` on the command prompt. This will read in the file `filt_special.dat` and 
process the files listed therein. If the Fortran program worked correctly you will find a couple of ``*.V2A`` files in the directory after
the Fortran program finished. There is no point trying the ``sm_gui.py`` program until the Fortran program is working correctly. 
  
Running the program
-------------------

Once you have installed ``sm_gui.py`` and compiled the Fortran program you can start the GUI by typing ``sm_gui.py`` on the command prompt. 
Let's say the Fortran program is installed under ``I:\some\path`` than you could pass this information to the GUI on the command line

>>> sm_gui.py --fdir I:\some\path

If you don't provide this directory on the command line the program will ask you for it at start up.

The functionality of the program is fairly self explanatory. You can choose the filter range for the high pass filter by either typing 
directly in the entry box or by using the arrow buttons (increments of 0.01). Once you press the ``Filter`` button, the Fortran program 
will be called with the new filter parameters and create a Volume 2 data file in the same directory as the Fortran program and the input 
file. The spectra and time series plots get updated and you can either go to the next entry in your input file by pressing the ``Next`` 
button or keep playing with the filter range. The input to trim the data works the same. 
 
There are two drop-down lists which let you choose the spectra and time series to plot. ``Acceleration (filtered)`` and 
``Displacement (filtered)`` are the records from the Volume 2 file produced by the Fortran program. ``Acceleration (unfiltered)`` is
the record of the corresponding Volume 1 file. The orientation of the sensor for each trace is shown in the top right corner 
and the filename is shown in the title of the time series plot.

When pressing the ``Save`` button, you can choose a file to save the modified input list to. This file is identical to the original 
input file apart from the filter range and length of the records that you changed.

With the check buttons on the right you can switch the plotting of extra information on and off, such as the maxima of the time series. 
If you hover with your mouse over the button you will get a short help message.

The navigation buttons below each canvas can be used for things like zooming into the plots or saving them as pixel images. 

.. _Python: http://www.python.org


Troubleshooting
---------------

In case the installer doesn't find your Python 2.6.x installation you can check in the registry for the correct entry of 
``SOFTWARE\Python\PythonCore\2.6\InstallPath\`` under the ``HKEY_LOCAL_MACHINE`` category. It should point to the Python 
installation on your computer.

 

.. toctree::
   :maxdepth: 2

Modules
-------

sm_gui.py
=========
.. automodule:: sm_gui
   :members:
   
read_gns_sm_data.py
===================
.. automodule:: read_gns_sm_data
   :members:
   
fortran_interface.py
====================
.. automodule:: fortran_interface
   :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

