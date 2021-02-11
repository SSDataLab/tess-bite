from tess_locator import locate

from .core import RemoteTessImage


def bite_ffi(url, col, row, shape=(5, 5)):
    """Retrieve a section from an FFI."""
    img = RemoteTessImage(url)
    return img.download_cutout(col=col, row=row, shape=shape)


def bite_header():
    # to do
    pass


def bite(target, sector=None, shape=(5, 5)):
    """Returns a target pixel file."""
    from lightkurve.targetpixelfile import TargetPixelFileFactory

    crd = locate(target=target, sector=sector)[0]
    n_cadences = 1
    urls = [crd.get_images()[idx].url for idx in range(n_cadences)]
    factory = TargetPixelFileFactory(
        n_cadences=n_cadences, n_rows=shape[1], n_cols=shape[0]
    )
    for idx, url in enumerate(urls):
        flux = bite_ffi(url, col=crd.column, row=crd.row, shape=shape)
        factory.add_cadence(idx, flux=flux)
    tpf = factory.get_tpf(
        hdu0_keywords={"TELESCOP": "TESS", "CREATOR": "TessTargetPixelFile"}
    )
    tpf.quality_mask = [True] * n_cadences
    tpf.get_header(1)["1CRV5P"] = 0
    tpf.get_header(1)["2CRV5P"] = 0
    return tpf
