tess-bite
============

**Take a bite out of TESS Full Frame Images using HTTP range requests.**

|pypi| |pytest| |black| |flake8| |mypy|

.. |pypi| image:: https://img.shields.io/pypi/v/tess-bite
                :target: https://pypi.python.org/pypi/tess-bite
.. |pytest| image:: https://github.com/SSDataLab/tess-bite/workflows/pytest/badge.svg
.. |black| image:: https://github.com/SSDataLab/tess-bite/workflows/black/badge.svg
.. |flake8| image:: https://github.com/SSDataLab/tess-bite/workflows/flake8/badge.svg
.. |mypy| image:: https://github.com/SSDataLab/tess-bite/workflows/mypy/badge.svg


`tess-bite` is a user-friendly package which provides fast access to sections of TESS Full-Frame Image (FFI) data.
It uses the HTTP range request mechanism to download only those parts of an FFI that are required
to obtain a cut-out image.

Installation
------------

.. code-block:: bash

    python -m pip install tess-bite

Example use
-----------

Obtain a Target Pixel File for a stationary object:

.. code-block:: python

    >>> from tess_bite import bite
    >>> bite("Alpha Cen", shape=(10, 10))
    TargetPixelFile("Alpha Cen")


Obtain a Target Pixel File centered on a moving asteroid:

.. code-block:: python

    >>> from tess_bite import bite_asteroid
    >>> bite_asteroid("Vesta", start="2019-04-28", stop="2019-06-28)
    TargetPixelFile("Vesta")


Obtain a cut-out image from a single FFI:

.. code-block:: python



Documentation
-------------

Coming soon!


Similar services
----------------

`TESScut <https://mast.stsci.edu/tesscut/>`_ is an excellent API service which allows cut outs
to be obtained for stationary objects.  `tess-bite` provides an alternative implementation of this
service by leveraging the `HTTP range requests <https://developer.mozilla.org/en-US/docs/Web/HTTP/Range_requests>`_
mechanism to download pixel values directly from FFI files.
Compared to TESScut, the goal of tess-bite is provide an alternative way to obtain cut-outs which
does not require a central API service, but can instead be run on a local machine or in the cloud.
At this time it is unclear whether or not this is a good idea, so we recommend to keep using TESScut for now!
