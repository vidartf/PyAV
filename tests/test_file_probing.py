from fractions import Fraction
import json
import subprocess
import sys

from .common import fate_suite, av, TestCase

try:
    long
except NameError:
    long = int


class TestProbe(TestCase):

    def get_probe(self, path):
        cmd = 'ffprobe -v quiet -print_format json -show_format -show_streams'.split()
        cmd.append(path)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        out, _ = proc.communicate()
        return json.loads(out)

    def assertContainer(self, fh, probe):
        self.assertEqual(fh.format.name, probe['format_name'])
        self.assertEqual(fh.format.long_name, probe['format_long_name'])
        self.assertEqual(fh.size, int(probe['size']))
        self.assertEqual(fh.bit_rate, int(probe['bit_rate']))
        self.assertEqual(fh.start_time, int(float(probe['start_time']) * av.time_base))
        self.assertEqual(fh.metadata, {})

    def assertBasicStream(self, stream, probe):
        self.assertEqual(stream.index, probe['index'])
        self.assertEqual(stream.type, probe['codec_type'])
        self.assertEqual(stream.name, probe['codec_name'])
        self.assertEqual(stream.long_name, probe['codec_long_name'])

    def assertAudioStream(self, stream, probe):
        self.assertBasicStream(stream, probe)
        self.assertEqual(stream.channels, int(probe['channels']))
        self.assertEqual(stream.layout.name, probe['channel_layout'])
        self.assertEqual(stream.rate, int(probe['sample_rate']))
        self.assertEqual(stream.format.name, probe['sample_fmt'])

    def assertVideoStream(self, stream, probe):
        self.assertBasicStream(stream, probe)

        self.assertEqual(stream.profile, probe['profile'])

        if 'bit_rate' in probe:
            self.assertEqual(stream.bit_rate, int(probe['bit_rate']))
        self.assertEqual(stream.max_bit_rate, int(probe['max_bit_rate']))

        self.assertEqual(
            str(stream.sample_aspect_ratio).replace('/', ':'),
            probe['sample_aspect_ratio']
        )
        self.assertEqual(
            str(stream.display_aspect_ratio).replace('/', ':'),
            probe['display_aspect_ratio']
        )
        self.assertEqual(stream.format.name, probe['pix_fmt'])
        self.assertEqual(stream.has_b_frames, bool(int(probe['has_b_frames'])))
        self.assertEqual(
            '%d/%d' % (stream.average_rate.numerator, stream.average_rate.denominator),
            probe['avg_frame_rate']
        )
        
        self.assertEqual(stream.width, int(probe['width']))
        self.assertEqual(stream.height, int(probe['height']))

    def test_mpeg2_ts_audio(self):
        path = fate_suite('aac/latm_stereo_to_51.ts')
        fh = av.open(path)
        probe = self.get_probe(path)
        self.assertContainer(fh, probe['format'])
        self.assertEqual(len(fh.streams), len(probe['streams']))
        self.assertAudioStream(fh.streams[0], probe['streams'][0])

    def test_mpeg2_ts_video(self):
        path = fate_suite('mpeg2/mpeg2_field_encoding.ts')
        fh = av.open(path)
        probe = self.get_probe(path)
        self.assertContainer(fh, probe['format'])
        self.assertEqual(len(fh.streams), len(probe['streams']))
        self.assertVideoStream(fh.streams[0], probe['streams'][0])

