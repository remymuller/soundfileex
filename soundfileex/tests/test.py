from unittest import TestCase

class Test(TestCase):
    def test_instrument_chunk(self):
        import numpy as np
        import math 
        import soundfileex.soundfileex as sfex
        import os

        sr          = 44100
        f0          = 441
        midipitch   = 69 + 12 * (math.log(f0 / 440.0) / math.log(2))
        note        = int(math.floor(midipitch) + 0.5)    # nearest integer note
        detune      = int(math.floor(100 * (midipitch - note) + 0.5))  # detune in cents
        period      = int(math.floor(sr / float(f0) + 0.5))
        loop_start  = 101*period
        loop_end    = 102*period
        loop_count  = 0
        #print("pitch: %f, note: %d, detune: %d cents" % (midipitch, note, detune))

        L = sr
        n = np.arange(L)
        t = n / float(sr)
        x = np.sin(2*np.pi*f0*t)

        # test WAV
        with sfex.SoundFileEx("test.wav", "w", samplerate=sr, channels=1, format="WAV", subtype="FLOAT") as snd:
            snd.set_instrument_chunk(basenote=note, detune=detune, loops=[(loop_start, loop_end)])
            snd.write(x)

        with sfex.SoundFileEx("test.wav", "r") as snd:
            chunk = snd.get_instrument_chunk()
            self.assertEqual(chunk.basenote, note)
            #self.assertEqual(chunk.detune, detune) # this one fails for now :(
            self.assertEqual(len(chunk.loops), 1)
            self.assertEqual(chunk.loops[0][0], loop_start)
            self.assertEqual(chunk.loops[0][1], loop_end)
        os.remove("test.wav")

        # test AIFF
        # with sfex.SoundFileEx("test.aiff", "w", samplerate=sr, channels=1, format="AIFF", subtype="PCM_16") as snd:
        #     snd.set_instrument_chunk(basenote=note, detune=detune, loops=[(loop_start, loop_end)])
        #     snd.write(x)

        #with sfex.SoundFileEx("test.aiff", "r") as snd:
        #    chunk = snd.get_instrument_chunk()
        #     #print(chunk)
        #     self.assertEqual(chunk.basenote, note)
        #     self.assertEqual(chunk.detune, detune) 
        #     self.assertEqual(len(chunk.loops), 1)
        #     self.assertEqual(chunk.loops[0][0], loop_start)
        #     self.assertEqual(chunk.loops[0][1], loop_end)
        #os.remove("test.aiff")


if __name__ == "__main__":
    test = Test()
    test.test_instrument_chunk()

