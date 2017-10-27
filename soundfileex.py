import soundfile as sf
from ctypes.util import find_library as _find_library

# get PySoundfile FFI
ffi = sf._ffi

# add missing definitions
ffi.cdef("""
enum
{
    // SFC_GET_CUE_COUNT               = 0x10CD,
    // SFC_GET_CUE                     = 0x10CE,
    // SFC_SET_CUE                     = 0x10CF,

    SFC_GET_INSTRUMENT              = 0x10D0,
    SFC_SET_INSTRUMENT              = 0x10D1,
};

enum
{   /*
    **  The loop mode field in SF_INSTRUMENT will be one of the following.
    */
    SF_LOOP_NONE = 800,
    SF_LOOP_FORWARD,
    SF_LOOP_BACKWARD,
    SF_LOOP_ALTERNATING
};

typedef struct
{   int gain ;
    char basenote, detune ;
    char velocity_lo, velocity_hi ;
    char key_lo, key_hi ;
    int loop_count ;

    struct
    {   int mode ;
        uint32_t start ;
        uint32_t end ;
        uint32_t count ;
    } loops [16] ; /* make variable in a sensible way */
} SF_INSTRUMENT ;
""")

# reopen libsndfile with new definitions
libsndfile = ffi.dlopen(_find_library('sndfile'))
sf._snd = libsndfile


class InstrumentChunk(object):
    """
    """

    def __init__(self, gain=0, basenote=60, detune=0, 
                lovel=0, hivel=0, lokey=0, hikey=127, loops=[]):
        self.basenote = basenote
        self.detune   = detune
        self.gain     = gain
        self.lovel    = lovel
        self.hivel    = hivel
        self.lokey    = lokey
        self.hikey    = hikey
        self.loops    = loops  

    def __repr__(self):
        return "(basenote=%d, detune=%d, gain=%d, lovel=%d, hivel=%d, lokey=%d, hikey=%d, loops=%s)" % (
            self.basenote, 
            self.detune, 
            self.gain,
            self.lovel,
            self.hivel,
            self.lokey,
            self.hikey,
            str(self.loops)
            )


class SoundFileEx(sf.SoundFile):

    # def __init__(self, *args, **kwargs):
    #     sf.SoundFile.__init__(self, args, kwargs)

    def get_instrument_chunk(self):
        """
        """
        chunk = ffi.new("SF_INSTRUMENT*")
        size  = ffi.sizeof("SF_INSTRUMENT")
        result = libsndfile.sf_command(self._file, libsndfile.SFC_GET_INSTRUMENT, chunk, size)
        if result == libsndfile.SF_FALSE:
            error = ffi.string(libsndfile.sf_strerror(snd._file))
            print error
            raise RuntimeError(error)

        basenote = ffi.cast("int", chunk.basenote)
        detune   = ffi.cast("int", chunk.detune)
        gain     = ffi.cast("int", chunk.gain)
        lovel    = ffi.cast("int", chunk.velocity_lo)
        hivel    = ffi.cast("int", chunk.velocity_hi)
        lokey    = ffi.cast("int", chunk.key_lo)
        hikey    = ffi.cast("int", chunk.key_hi)
        loop_count = ffi.cast("int", chunk.loop_count)

        loops = []
        for i in range(loop_count):
            #start = int(ffi.cast("int", chunk.loops[i].start))
            start = int(chunk.loops[i].start)
            end   = int(chunk.loops[i].end)
            mode  = int(chunk.loops[i].mode)
            count = int(chunk.loops[i].count)
            loops.append((start, end, mode, count))

        return InstrumentChunk(gain=gain, basenote=basenote, detune=detune, 
                lovel=lovel, hivel=hivel, lokey=lokey, hikey=hikey, loops=loops)


    def set_instrument_chunk(self, gain=0, basenote=60, detune=0, 
                            lovel=0, hivel=0, lokey=0, hikey=127, loops=[]):
        """

        snd.set_instrument_chunk(basenote=note, 
                                 detune=detune, 
                                 loops=[(start, end)])
        """
        # TODO: test ranges
        assert len(loops) < 16

        chunk                = ffi.new("SF_INSTRUMENT*")
        chunk.basenote       = ffi.cast("char", basenote)
        chunk.detune         = ffi.cast("char", detune)
        chunk.gain           = ffi.cast("int", gain)
        chunk.velocity_lo    = ffi.cast("char", lovel)
        chunk.velocity_hi    = ffi.cast("char", hivel)
        chunk.key_lo         = ffi.cast("char", lokey)
        chunk.key_hi         = ffi.cast("char", hikey)
        chunk.loop_count     = ffi.cast("int", len(loops))

        for i in range(len(loops)):
            loop    = loops[i]
            assert len(loop) >= 2
            start   = loop[0]
            end     = loop[1]
            mode    = loop[2] if len(loop) > 2 else libsndfile.SF_LOOP_FORWARD
            count   = loop[3] if len(loop) > 3 else 0

            chunk.loops[i].start = ffi.cast("uint32_t", start)
            chunk.loops[i].end   = ffi.cast("uint32_t", end)
            chunk.loops[i].mode  = mode
            chunk.loops[i].count = ffi.cast("uint32_t", count)

        size    = ffi.sizeof("SF_INSTRUMENT")
        result  = libsndfile.sf_command(self._file, libsndfile.SFC_SET_INSTRUMENT, chunk, size)
        if result == libsndfile.SF_FALSE:
            error = ffi.string(libsndfile.sf_strerror(snd._file))
            print error
            raise RuntimeError(error)



if __name__ == "__main__":
    import numpy
    import math

    sr          = 44100
    f0          = 441/4.0
    midipitch   = 69 + 12 * (math.log(f0 / 440.0) / math.log(2))
    note        = int(math.floor(midipitch) + 0.5)    # nearest integer note
    detune      = int(math.floor(100 * (midipitch - note) + 0.5))  # detune in cents
    period      = int(math.floor(sr / float(f0) + 0.5))
    loop_start  = 40*period
    loop_end    = 80*period
    loop_count  = 0
    print "pitch: %f, note: %d, detune: %d cents" % (midipitch, note, detune)

    L = sr
    n = numpy.arange(L)
    t = n / float(sr)
    x = numpy.sin(2*numpy.pi*f0*t)

    with SoundFileEx("test.wav", "w", samplerate=sr, channels=1, format="WAV", subtype="FLOAT") as snd:
        snd.set_instrument_chunk(basenote=note, detune=detune, loops=[(loop_start, loop_end)])
        snd.write(x)

    with SoundFileEx("test.wav", "r") as snd:
        chunk = snd.get_instrument_chunk()
        print chunk

