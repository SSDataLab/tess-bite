from astropy.io import fits

from tess_bite import RemoteTessImage


def test_basics():
    with open("example.fits", "rb") as fp:
        img = RemoteTessImage(url=fp)
        fts = fits.open("example.fits")
        assert img._download_range(0, 5).decode("ascii") == "SIMPLE"
        assert img._download_range_multiple([(0, 5), (8, 8)]) == [b"SIMPLE", b"="]
        assert img._find_data_offset(ext=0) == 2880
        assert img._find_data_offset(ext=1) == 23040
        assert img._find_pixel_offset(col=0, row=0) == 23040
        assert img._find_pixel_range(col=0, row=0, shape=(1, 1)) == [(23040, 23043)]
        assert (
            img.download_cutout(col=0, row=0, shape=(1, 1))[0][0] == fts[1].data[0, 0]
        )
        assert (
            img.download_cutout(col=1, row=0, shape=(3, 1)) == fts[1].data[0, (0, 1, 2)]
        ).all()
        # shape mismatch: assert (img.download_cutout(col=1, row=1, dcol=1, drow=3) == fts[1].data[(1, 2, 3), 1]).all()


def test_basics2():
    # Remote tests
    url = "https://mast.stsci.edu/portal/Download/file?uri=mast:TESS/product/tess2019142115932-s0012-2-1-0144-s_ffic.fits"
    img = RemoteTessImage(url=url)
    assert img._download_range(0, 5).decode("ascii") == "SIMPLE"
    assert img._download_range_multiple([(0, 5), (8, 8)]) == [b"SIMPLE", b"="]
    assert img.download_cutout(col=0, row=0, shape=(1, 1))[0][0] == fts[1].data[0, 0]
    assert (
        img.download_cutout(col=1, row=1, shape=(3, 1)) == fts[1].data[1, (0, 1, 2)]
    ).all()
