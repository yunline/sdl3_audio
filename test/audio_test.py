import unittest
import os
import random
os.environ["SDL_AUDIO_DRIVER"]="dummy"

import sdl3_audio.audio as audio
audio._init_library(os.environ["SDL3_DLL_PATH"])

class AudioTest(unittest.TestCase):
    """Test cases of functions in audio module"""

    def test_dB(self):
        self.assertEqual(audio.dB(-20.0), 0.01)
        self.assertEqual(audio.dB(-10.0), 0.1)
        self.assertEqual(audio.dB(0), 1.0)
        self.assertEqual(audio.dB(+10.0), 10.0)
        self.assertEqual(audio.dB(+20.0), 100.0)

    def test_list_audio_drivers(self):
        result = audio.list_audio_drivers()
        self.assertIsInstance(result, list)
        for drv_name in result:
            self.assertIsInstance(drv_name, str)
    
    def test_get_current_audio_driver(self):
        result = audio.get_current_audio_driver()
        self.assertIsInstance(result, str)
    
    def test_list_playback_devices(self):
        result = audio.list_playback_devices()
        self.assertIsInstance(result, list)
        for phy_dev in result:
            self.assertIsInstance(phy_dev, audio.PhysicalAudioDevice)
            self.assertTrue(phy_dev.playback)
    
    def test_list_recording_devices(self):
        result = audio.list_recording_devices()
        self.assertIsInstance(result, list)
        for phy_dev in result:
            self.assertIsInstance(phy_dev, audio.PhysicalAudioDevice)
            self.assertTrue(phy_dev.recording)
    
    def test_open_default_playback_device(self):
        dev = audio.open_default_playback_device()
        self.assertIsInstance(dev, audio.LogicalAudioDevice)
        self.assertTrue(dev.playback)
        del dev

        self.assertRaises(
            TypeError,
            lambda: audio.open_default_playback_device(
                spec_hint = "NOT A CORRECT TYPE" # type: ignore
            )
        )
    
    def test_open_default_recording_device(self):
        dev = audio.open_default_recording_device()
        self.assertIsInstance(dev, audio.LogicalAudioDevice)
        self.assertTrue(dev.recording)
        del dev

        self.assertRaises(
            TypeError,
            lambda: audio.open_default_recording_device(
                spec_hint = "NOT A CORRECT TYPE" # type: ignore
            )
        )

class AudioSpecTest(unittest.TestCase):
    """Test cases of audio.AudioSpec class"""

    def test___init__(self):
        audio.AudioSpec("U8")
        audio.AudioSpec("S8")
        audio.AudioSpec("S16LE")
        audio.AudioSpec("S16BE")
        audio.AudioSpec("S32LE")
        audio.AudioSpec("S32BE")
        audio.AudioSpec("F32LE")
        audio.AudioSpec("F32BE")
        audio.AudioSpec("S16LE", 2)
        audio.AudioSpec("S16LE", 2, 48000)
        audio.AudioSpec("S16LE", n_channels=2)
        audio.AudioSpec("S16LE", sample_rate=48000)

        # Test the argument 'format'
        self.assertRaises(
            TypeError,
            lambda: audio.AudioSpec(0.1) # type: ignore
        )

        self.assertRaises(
            ValueError,
            lambda: audio.AudioSpec("NOT A CORRECT FORMAT NAME") # type: ignore
        )

        # Test the argument 'n_channels'
        self.assertRaises(
            TypeError,
            lambda: audio.AudioSpec("S16LE", n_channels=0.5) # type: ignore
        )
        spec = audio.AudioSpec("S16LE", n_channels=114)
        self.assertEqual(spec.n_channels, 114)

        # Test the argument 'sample_rate'
        self.assertRaises(
            TypeError,
            lambda: audio.AudioSpec("S16LE", sample_rate=0.5) # type: ignore
        )
        spec = audio.AudioSpec("S16LE", sample_rate=11451)
        self.assertEqual(spec.sample_rate, 11451)

    def test_format_property(self):
        spec = audio.AudioSpec("S16LE")
        self.assertIsInstance(spec.format, str)
        self.assertEqual(spec.format, "S16LE")

        # Should be read-only
        self.assertRaises(
            AttributeError,
            lambda: setattr(spec, "format", "F32LE")
        )

    def test_n_channels_property(self):
        spec = audio.AudioSpec("S16LE", 4)
        self.assertIsInstance(spec.n_channels, int)
        self.assertEqual(spec.n_channels, 4)

        # Should be read-only
        self.assertRaises(
            AttributeError,
            lambda: setattr(spec, "n_channels", 114514)
        )

    def test_sample_rate_property(self):
        spec = audio.AudioSpec("S16LE", 2, 44100)
        self.assertIsInstance(spec.sample_rate, int)
        self.assertEqual(spec.sample_rate, 44100)

        # Should be read-only
        self.assertRaises(
            AttributeError,
            lambda: setattr(spec, "sample_rate", 114514)
        )
    
    def test_frame_size_property(self):
        formats = ["U8","S8","S16LE","S16BE","S32LE","S32BE","F32LE","F32BE"]
        byte_sizes = [1,1,2,2,4,4,4,4]
        nchs = [random.randint(1,10) for _ in formats]
        specs = [audio.AudioSpec(fmt,n_channels=nch) for fmt,nch in zip(formats,nchs)]

        for byte_size, nch, spec in zip(byte_sizes, nchs, specs):
            self.assertIsInstance(spec.frame_size, int)
            self.assertEqual(spec.frame_size, byte_size*nch)
        
        spec = audio.AudioSpec("U8")
        # Should be read-only
        self.assertRaises(
            AttributeError,
            lambda: setattr(spec, "frame_size", 114514)
        )
    
    def test___eq__(self):
        a1 = audio.AudioSpec("S16LE",2,48000)
        a2 = audio.AudioSpec("S16LE",2,48000)
        a3 = audio.AudioSpec("F32LE",2,48000)
        a4 = audio.AudioSpec("S16LE",2,44100)
        a5 = audio.AudioSpec("S16LE",4,48000)
        self.assertEqual(a1, a2)
        self.assertNotEqual(a1, a3)
        self.assertNotEqual(a1, a4)
        self.assertNotEqual(a1, a5)
        self.assertNotEqual(a1, "NOT CORRECT TYPE")

class _AudioDeviceTest:
    """Test cases of audio._AudioDevice base class"""
    testing_audio_device: audio._AudioDevice

    def test_name_property(self):
        name = self.testing_audio_device.name
        self.assertIsInstance(name, str) # type: ignore

        # Should be read-only
        self.assertRaises( # type: ignore
            AttributeError,
            lambda: setattr(self.testing_audio_device, "name", "string")
        )
    
    def test_playback_property_and_recording_property(self):
        is_playback = self.testing_audio_device.playback
        is_recordinng = self.testing_audio_device.recording

        self.assertEqual(is_playback, not is_recordinng) # type: ignore
        self.assertIsInstance(is_playback, bool) # type: ignore
        self.assertIsInstance(is_recordinng, bool) # type: ignore

        # Should be read-only
        self.assertRaises( # type: ignore
            AttributeError,
            lambda: setattr(self.testing_audio_device, "playback", False)
        )
        self.assertRaises( # type: ignore
            AttributeError,
            lambda: setattr(self.testing_audio_device, "recording", False)
        )
    
    def test_id_property(self):
        _id = self.testing_audio_device.id
        self.assertIsInstance(_id, int) # type: ignore

        # Should be read-only
        self.assertRaises( # type: ignore
            AttributeError,
            lambda: setattr(self.testing_audio_device, "id", 0)
        )

class PhysicalAudioDeviceTest(unittest.TestCase, _AudioDeviceTest):
    """Test cases of audio.PhysicalAudio class"""
    testing_physical_audio_device: audio.PhysicalAudioDevice

    def setUp(self):
        self.testing_physical_audio_device = audio.list_playback_devices()[0]
        self.testing_audio_device = self.testing_physical_audio_device
    
    def test___init__(self):
        self.assertRaises(
            TypeError,
            lambda: audio.PhysicalAudioDevice()
        )
    
    def test_preferred_spec_property(self):
        spec = self.testing_physical_audio_device.preferred_spec
        self.assertIsInstance(spec, audio.AudioSpec)

        # Should be read-only
        self.assertRaises(
            AttributeError,
            lambda: setattr(self.testing_audio_device, "preferred_spec", None)
        )
    
    def test_open(self):
        logical = self.testing_physical_audio_device.open()
        self.assertIsInstance(logical, audio.LogicalAudioDevice)
        del logical

        self.assertRaises(
            TypeError,
            lambda: self.testing_physical_audio_device.open(
                spec_hint="NOT CORRECT TYPE" # type: ignore
            )
        )
        

if __name__ == '__main__':
    unittest.main()