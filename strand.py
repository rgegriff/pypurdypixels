import time


class Strand(object):
    rgb2px = staticmethod(lambda r, g, b: ((r & 0xFF) << 16) | ((g & 0xFF) << 8) | (b & 0xFF))
    Color2rgb = staticmethod(lambda C: [int(C.red * 255), int(C.green * 255), int(C.blue * 255)])
    pixels = []
    debug_mode = None

    def __init__(self, strand_length=25, pixels=None,
                 write_on_init=True, debug_mode=True):
        self.debug_mode = debug_mode
        if pixels == None:
            self.pixels = [0] * strand_length
        else:
            if len(pixels) < strand_length: # pad if shorter
                pixels = pixels + [0] * (strand_length-len(pixels))
            elif len(pixels) > strand_length: # truncate if longer
                pixels = pixels[:25]
            self.pixels = pixels
        if write_on_init:
            self._write()

    def __len__(self):
        return len(self.pixels)

    def __getitem__(self, key):
        return self.pixels[key]

    def __setitem__(self, key, value):
        self.pixels[key] = value
        self._write()

    def _write(self):
        if not self.debug_mode:
            spidev = file("/dev/spidev0.0", "w")
            pixels = self.pixels
            for i in xrange(len(pixels)):
                spidev.write(chr((pixels[i] >> 16) & 0xFF))
                spidev.write(chr((pixels[i] >> 8) & 0xFF))
                spidev.write(chr(pixels[i] & 0xFF))
            spidev.close()
        time.sleep(0.002)


class Matrix(object):
    strand = None
    cols = 5
    rows = 5
    mapping = [20, 21, 22, 23, 24,
               19, 18, 17, 16, 15,
               10, 11, 12, 13, 14,
                9,  8,  7,  6,  5,
                0,  1,  2,  3,  4]

    def __init__(self, strand=Strand(), cols=None, rows=None, mapping=None):
        self.strand = strand
        if cols is not None:
            self.cols = cols
        if rows is not None:
            self.rows = rows
        if mapping is not None:
            self.mapping = mapping

    def get_row_indexes(self, i):
        if i > self.rows - 1 or i < 0:
            raise IndexError("Row index out of bounds")
        start = i * self.cols
        end = start + self.cols
        return self.mapping[start:end]

    def get_row_values(self, i):
        if i > self.rows - 1 or i < 0:
            raise IndexError("Row index out of bounds")
        pix_idx = self.get_row_indexes(i)
        row = []
        for i in pix_idx:
            row.append(self.strand[i])
        return row

    def get_col_indexes(self, i):
        pix_idx = []
        for r in xrange(self.rows):
            pix_idx.append(self.get_row_indexes(r)[i])
        return pix_idx

    def get_col_values(self, i):
        if i > self.cols - 1 or i < 0:
            raise IndexError("Column index out of bounds")
        pix_idx = self.get_col_indexes(i)
        col = []
        for idx in pix_idx:
            col.append(self.strand.pixels[idx])
        return col

    def set_row_values(self, i, newrow):
        pix_idx = self.get_row_indexes(i)
        if len(pix_idx) != len(newrow):
            raise Exception("length mismatch")
        for i, value in enumerate(pix_idx):
            self.strand.pixels[value] = newrow[i]
        self.strand._write()

    def set_col_values(self, i, newcol):
        pix_idx = self.get_col_indexes(i)
        if len(pix_idx) != len(newcol):
            raise Exception("length mismatch")
        for i, value in enumerate(pix_idx):
            self.strand.pixels[value] = newcol[i]
        self.strand._write()

    def __unicode__(self):
        return "%dx%d DisplayMatrix" % (self.rows, self.cols)
