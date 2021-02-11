import re
import io
import struct

import numpy as np
import httpx
import logging

from . import log

# FITS standard specifies that header and data units
# shall be a multiple of 2880 bytes long.
FITS_BLOCK_SIZE = 2880  # bytes

# TESS FFI dimensions
FFI_COLUMNS = 2136  # i.e. NAXIS1
FFI_ROWS = 2078  # i.e. NAXIS2

BYTES_PER_PIX = 4  # float32


class RemoteTessImage:
    def __init__(self, url, data_offset=None):
        self.url = url
        self.data_offset = data_offset if data_offset else self._find_data_offset(ext=1)

    def _download_range_multiple(self, byteranges: list) -> bytes:
        if isinstance(self.url, str):
            return http_get_range(self.url, byteranges)
        else:
            result = []
            for r in byteranges:
                self.url.seek(r[0], 0)
                result.append(self.url.read(r[1] - r[0] + 1))
            return result

    def _download_range(self, begin: int, end: int) -> bytes:
        return self._download_range_multiple([(begin, end)])[0]

    def _find_data_offset(self, ext=1) -> int:
        """Returns the byte offset of the start of the data section."""
        # We'll assume the data starts within the first 10 FITS BLOCKs.
        # This means the method will currently only work for extensions 0 and 1 of a TESS FFI file.
        max_seek = FITS_BLOCK_SIZE * 12
        data = self._download_range(0, max_seek)
        current_ext = 0
        offset = 0
        while offset <= max_seek:
            block = data[offset : offset + FITS_BLOCK_SIZE]
            offset += FITS_BLOCK_SIZE
            # Header sections end with "END" followed by whitespace until the end of the block
            if re.search("END\s*$", block.decode("ascii")):
                if current_ext == ext:
                    return offset
                current_ext += 1
        return None

    def _find_pixel_offset(self, col, row) -> int:
        """Returns the byte offset of a specific pixel position."""
        pixel_offset = col + row * FFI_COLUMNS
        return self.data_offset + BYTES_PER_PIX * pixel_offset

    def _find_pixel_range(self, col, row, shape=(1, 1)) -> list:
        """Returns the byte ranges of a rectangle."""
        result = []
        col1 = int(col) - shape[0] // 2
        row1 = int(row) - shape[1] // 2

        if col1 < 0 or col1 >= FFI_COLUMNS:
            raise ValueError(
                f"column out of bounds (col must be in range 0-{FFI_COLUMNS})"
            )
        if row1 < 0 or row1 >= FFI_ROWS:
            raise ValueError(f"row out of bounds (row must be in range 0-{FFI_ROWS})")

        for myrow in range(row1, row1 + shape[1]):
            myrange = (
                self._find_pixel_offset(col1, myrow),
                self._find_pixel_offset(col1 + shape[0], myrow) - 1,
            )
            result.append(myrange)
        return result

    def download_cutout(self, col, row, shape=(5, 5)) -> list:
        """Returns a 2D array of pixel values."""
        byterange = self._find_pixel_range(col=col, row=row, shape=shape)
        bytedata = self._download_range_multiple(byterange)
        data = []
        for b in bytedata:
            n_pixels = len(b) // BYTES_PER_PIX
            values = struct.unpack(">" + "f" * n_pixels, b)
            data.append(values)
        return np.array(data)


def http_get_range(url: str, byterange: list = None) -> bytes:
    """Download one or more byte ranges."""
    http_headers = {}
    if byterange:
        rangestr = ",".join([f"{r[0]}-{r[1]}" for r in byterange])
        http_headers["Range"] = f"bytes={rangestr}"
    resp = httpx.get(url, headers=http_headers)

    if "multipart/byteranges" not in resp.headers["content-type"]:
        data = [resp.content]
    else:
        lines = resp.content.split(b"\r\n")
        data = []
        for idx in range(len(lines)):
            # Data follows an empty line
            try:
                if idx > 0 and idx < len(lines) - 1 and lines[idx] == b"":
                    data.append(lines[idx + 1])
            except UnicodeDecodeError:
                pass
    return data
