PyATEM
======

Library implementing the ATEM video switcher protocol and a GTK3.0 application

![Screenshot of the control application](http://brixitcdn.net/srht/openatem.png)

Installation
------------

Install the pyatem protocol module::

   sudo setup.py install

Build and install the gtk application::

   meson build
   cd build
   ninja
   sudo ninja install

Run the application::

   switcher-control

Developing
----------

Development happens on matrix on #openatem:brixit.nl