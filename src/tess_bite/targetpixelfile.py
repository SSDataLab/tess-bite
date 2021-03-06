"""
A TESS TPF contains the following data:

ColDefs(
    name = 'TIME'; format = 'D'; unit = 'BJD - 2457000, days'; disp = 'D14.7'
    name = 'TIMECORR'; format = 'E'; unit = 'd'; disp = 'E14.7'
    name = 'CADENCENO'; format = 'J'; disp = 'I10'
    name = 'RAW_CNTS'; format = '143J'; unit = 'count'; null = -1; disp = 'I8'; dim = '(11,13)'
    name = 'FLUX'; format = '143E'; unit = 'e-/s'; disp = 'E14.7'; dim = '(11,13)'
    name = 'FLUX_ERR'; format = '143E'; unit = 'e-/s'; disp = 'E14.7'; dim = '(11,13)'
    name = 'FLUX_BKG'; format = '143E'; unit = 'e-/s'; disp = 'E14.7'; dim = '(11,13)'
    name = 'FLUX_BKG_ERR'; format = '143E'; unit = 'e-/s'; disp = 'E14.7'; dim = '(11,13)'
    name = 'QUALITY'; format = 'J'; disp = 'B16.16'
    name = 'POS_CORR1'; format = 'E'; unit = 'pixel'; disp = 'E14.7'
    name = 'POS_CORR2'; format = 'E'; unit = 'pixel'; disp = 'E14.7'
)
"""
from datetime import datetime
import numpy as np
from numpy import array, ndarray

from astropy.wcs import WCS
from astropy.io import fits


class TargetPixelFile:
    def __init__(
        self,
        time: array,
        cadenceno: array,
        flux: ndarray,
        flux_err: ndarray,
        quality: array,
        wcs: WCS = None,
        meta: dict = None,
    ):
        self.time = time
        self.cadenceno = cadenceno
        self.flux = flux
        self.flux_err = flux_err
        self.quality = quality
        self.wcs = wcs
        self.meta = meta

    @property
    def n_cadences(self):
        return self.time.shape[0]

    @property
    def n_columns(self):
        return self.flux.shape[1]

    @property
    def n_rows(self):
        return self.flux.shape[2]

    @property
    def timecorr(self):
        if not hasattr(self, "_timecorr"):
            self._timecorr = np.zeros(self.n_cadences, dtype="float32")
        return self._timecorr

    @property
    def raw_cnts(self):
        if not hasattr(self, "_raw_cnts"):
            self._raw_cnts = np.empty(
                (self.n_cadences, self.n_rows, self.n_columns), dtype="int"
            )
            self._raw_cnts[:, :, :] = -1
        return self._raw_cnts

    @property
    def pos_corr1(self):
        if not hasattr(self, "_pos_corr1"):
            self._pos_corr1 = np.zeros(self.n_cadences, dtype="float32")
        return self._pos_corr1

    @property
    def pos_corr2(self):
        if not hasattr(self, "_pos_corr2"):
            self._pos_corr2 = np.zeros(self.n_cadences, dtype="float32")
        return self._pos_corr2

    @staticmethod
    def from_cutouts(images: list) -> "TargetPixelFile":
        shape = (len(images), images[0].flux.shape[0], images[0].flux.shape[1])
        flux = np.empty(shape)
        flux_err = np.empty(shape)
        for idx, img in enumerate(images):
            flux[idx] = img.flux
            flux_err[idx] = np.nan

        time = np.array([img.time for img in images])
        cadenceno = np.array([img.cadenceno for img in images])
        quality = np.array([img.quality for img in images])
        return TargetPixelFile(
            time=time,
            cadenceno=cadenceno,
            flux=flux,
            flux_err=flux_err,
            quality=quality,
        )

    @staticmethod
    def read(path) -> "TargetPixelFile":
        f = fits.open(path)
        tpf = TargetPixelFile(
            time=f[1].data["TIME"],
            cadenceno=f[1].data["CADENCENO"],
            flux=f[1].data["FLUX"],
            flux_err=f[1].data["FLUX_ERR"],
            quality=f[1].data["QUALITY"],
        )
        return tpf

    def write(self, *args, **kwargs):
        hdulist = self._create_hdulist()
        return hdulist.writeto(*args, **kwargs)

    def _create_hdulist(self):
        """Returns an astropy.io.fits.HDUList object."""
        return fits.HDUList(
            [self._create_primary_hdu(), self._create_table_extension()]
        )

    def _create_primary_hdu(self):
        """Returns the primary extension (#0)."""
        hdu = fits.PrimaryHDU()
        hdu.header["ORIGIN"] = "Unofficial tess-bite product"
        hdu.header["DATE"] = datetime.now().strftime("%Y-%m-%d")
        hdu.header["CREATOR"] = "tess-bite"
        return hdu

    def _create_table_extension(self):
        """Create the 'TARGETTABLES' extension (i.e. extension #1)."""
        # Turn the data arrays into fits columns and initialize the HDU
        coldim = "({},{})".format(self.n_columns, self.n_rows)
        eformat = "{}E".format(self.n_rows * self.n_columns)
        jformat = "{}J".format(self.n_rows * self.n_columns)
        cols = []
        cols.append(
            fits.Column(name="TIME", format="D", unit="BJD - 2454833", array=self.time)
        )
        cols.append(
            fits.Column(name="TIMECORR", format="E", unit="D", array=self.timecorr)
        )
        cols.append(fits.Column(name="CADENCENO", format="J", array=self.cadenceno))
        cols.append(
            fits.Column(
                name="RAW_CNTS",
                format=jformat,
                unit="count",
                dim=coldim,
                array=self.raw_cnts,
            )
        )
        cols.append(
            fits.Column(
                name="FLUX", format=eformat, unit="e-/s", dim=coldim, array=self.flux
            )
        )
        cols.append(
            fits.Column(
                name="FLUX_ERR",
                format=eformat,
                unit="e-/s",
                dim=coldim,
                array=self.flux_err,
            )
        )
        cols.append(fits.Column(name="QUALITY", format="J", array=self.quality))
        cols.append(
            fits.Column(
                name="POS_CORR1", format="E", unit="pixels", array=self.pos_corr1
            )
        )
        cols.append(
            fits.Column(
                name="POS_CORR2", format="E", unit="pixels", array=self.pos_corr2
            )
        )
        coldefs = fits.ColDefs(cols)
        hdu = fits.BinTableHDU.from_columns(coldefs)

        return hdu
