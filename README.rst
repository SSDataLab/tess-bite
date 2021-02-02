tess-bite
============

**Take a quick bite out of TESS Full Frame Images using HTTP range requests.**

|pypi|

.. |pypi| image:: https://img.shields.io/pypi/v/tess-bite
                :target: https://pypi.python.org/pypi/tess-bite


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

    >>> from tess_bite import bite_ffi
    >>> bite_ffi(url, col=50, row=20, shape=(20, 20))


Quickly download the header of an FFI:

.. code-block:: python

    >>> from tess_bite import bite_header
    >>> bite_header(url, ext=0)
    FitsHeader


What are HTTP range requests?
-----------------------------

Tess-bite is powered by the `HTTP range request <https://developer.mozilla.org/en-US/docs/Web/HTTP/Range_requests>`_ protocol.
This is a mechanism which allows a client to request specific bytes from a file on a web server.
For example, downloading a 3-by-3 pixel square of 4-byte pixel values from a TESS image
can be done very quickly using a HTTP request as follows:

.. code-block:: python

    >>> import httpx
    >>> url = "https://mast.stsci.edu/portal/Download/file?uri=mast:TESS/product/tess2019142115932-s0012-2-1-0144-s_ffic.fits"
    >>> resp = httpx.get(url, headers={"Range": "bytes=80000-80012,80020-80032,80040-80052"})
    >>> print(resp.text)

    --00000000000000000103
    Content-Type: application/octet-stream
    Content-Range: bytes 80000-80012/35553600

    DA@DLR½DW˜oD
    --00000000000000000103
    Content-Type: application/octet-stream
    Content-Range: bytes 80020-80032/35553600

    ³D.]DªJD
    --00000000000000000103
    Content-Type: application/octet-stream
    Content-Range: bytes 80040-80052/35553600

    D-aöD+W/DRD
    --00000000000000000103--

Of course the difficult part is to translate pixel coordinates to byte positions,
and to convert bytes to pixel values.  Tess-bite takes care of these steps for you!


Documentation
-------------

Coming soon!


Similar services
----------------

`TESScut <https://mast.stsci.edu/tesscut/>`_ is an excellent API service which allows cut outs
to be obtained for stationary objects.  Tess-bite provides an alternative implementation of this
service by leveraging the `HTTP range requests <https://developer.mozilla.org/en-US/docs/Web/HTTP/Range_requests>`_
mechanism to download pixel values directly from FFI files.

Compared to TESScut, the goal of tess-bite is provide an alternative way to obtain cut-outs which
does not require a central API service, but can instead be run on a local machine or in the cloud.
At this time tess-bite is an experiment, we recommend that you keep using TESScut for now!
