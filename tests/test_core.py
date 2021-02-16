from astropy.io import fits
import numpy as np

from tess_bite import RemoteTessImage


def test_remotetessimage_basics():
    """Test basic features of RemoteTessImage."""
    url = "https://mast.stsci.edu/portal/Download/file?uri=mast:TESS/product/tess2019142115932-s0012-2-1-0144-s_ffic.fits"
    img = RemoteTessImage(url=url)
    # Can we retrieve the first FITS header keyword? (SIMPLE)
    assert img._download_range(0, 5).decode("ascii") == "SIMPLE"
    assert img._download_range_multiple([(0, 5), (8, 8)]) == [b"SIMPLE", b"="]
    # Can we find the correct start position of the data for extenions 0 and 1?
    assert img._find_data_offset(ext=0) == 2880
    assert img._find_data_offset(ext=1) == 23040
    assert img._find_pixel_offset(col=0, row=0) == 23040
    assert img._find_pixel_range(col=0, row=0, shape=(1, 1)) == [(23040, 23043)]
    # Corner pixel
    assert img.download_cutout_array(col=0, row=0, shape=(1, 1)).round(7) == 0.0941298
    # First three pixels of the first row
    assert (
        img.download_cutout_array(col=1, row=0, shape=(3, 1)).round(7)
        == np.array([0.0941298, -0.0605419, 0.0106343])
    ).all()
    # First three pixels of the first column
    assert (
        img.download_cutout_array(col=1, row=1, shape=(1, 3)).round(7)
        == np.array([[-0.0605419], [0.0327947], [-0.0278026]])
    ).all()
