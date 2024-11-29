import ctypes
import typing

if typing.TYPE_CHECKING:
    import typed_sdl3
    from typed_sdl3 import *
    sdl3: typed_sdl3.SDL3DLL
    T = typing.TypeVar('T', bound=ctypes._CData)
    def byref(t:T) -> ctypes._Pointer[T]:
        return typing.cast(ctypes._Pointer[T], ctypes.byref(t))
else:
    from . import typed_sdl3
    from .typed_sdl3 import *
    byref = ctypes.byref
NULL = ctypes.POINTER(ctypes.c_int)()

# Added in SDL 3.2
SDL_IsAudioDevicePlayback = lambda x:(x)&(1<<0)
SDL_IsAudioDevicePhysical = lambda x:(x)&(1<<1)

def dB(db):
    return 10**(db/10)

class SDLError(RuntimeError):
    def __init__(self,*args: object) -> None:
        err = sdl3.SDL_GetError()
        assert err is not None
        super().__init__(err.decode("utf8"),*args)

def _init_library(sdl_dll_path:str):
    global sdl3
    sdl3 = typed_sdl3.load_sdl3_dll(sdl_dll_path)

    if not sdl3.SDL_WasInit(SDL_INIT_AUDIO):
        result = sdl3.SDL_Init(SDL_INIT_AUDIO)
        if result==False:
            raise SDLError()

def list_audio_drivers():
    n = sdl3.SDL_GetNumAudioDrivers()
    out = []
    for i in range(n):
        name = sdl3.SDL_GetAudioDriver(ctypes.c_int(i))
        assert name is not None
        out.append(name.decode("utf8"))
    return out

def get_current_audio_driver():
    drv_name = sdl3.SDL_GetCurrentAudioDriver()
    if drv_name is None:
        return None
    return drv_name.decode("utf8")

_str2fmt = {
"U8":SDL_AUDIO_U8.value,
"S8":SDL_AUDIO_S8.value,
"S16LE":SDL_AUDIO_S16LE.value,
"S16BE":SDL_AUDIO_S16BE.value,
"S32LE":SDL_AUDIO_S32LE.value,
"S32BE":SDL_AUDIO_S32BE.value,
"F32LE":SDL_AUDIO_F32LE.value,
"F32BE":SDL_AUDIO_F32BE.value,
}
_str2width = {
"U8":1,
"S8":1,
"S16LE":2,
"S16BE":2,
"S32LE":4,
"S32BE":4,
"F32LE":4,
"F32BE":4,
}
_fmt2str = {
SDL_AUDIO_U8.value:"U8",
SDL_AUDIO_S8.value:"S8",
SDL_AUDIO_S16LE.value:"S16LE",
SDL_AUDIO_S16BE.value:"S16BE",
SDL_AUDIO_S32LE.value:"S32LE",
SDL_AUDIO_S32BE.value:"S32BE",
SDL_AUDIO_F32LE.value:"F32LE",
SDL_AUDIO_F32BE.value:"F32BE",
}

class AudioSpec:
    _format:str
    _n_channels:int
    _sample_rate:int

    def __init__(self, format, n_channels=2, sample_rate=48000):
        assert format in _str2fmt
        self._format = format
        self._n_channels = n_channels
        self._sample_rate = sample_rate
    
    def __repr__(self):
        return f"<AudioSpec(format='{self._format}', n_channels={self._n_channels}, sample_rate={self._sample_rate})>"
    
    @property
    def format(self):
        return self._format
    
    @property
    def n_channels(self):
        return self.n_channels
    
    @property
    def sample_rate(self):
        return self._sample_rate
    
    @property
    def frame_size(self):
        return self._n_channels*_str2width[self._format]
    
    def _as_sdl_struct(self) -> SDL_AudioSpec:
        spec = SDL_AudioSpec()
        spec.format = _str2fmt[self._format]
        spec.channels = self._n_channels
        spec.freq = self._sample_rate
        return spec
    
    @classmethod
    def _from_sdl_struct(cls, struct:SDL_AudioSpec):
        format_str = _fmt2str[struct.format]
        return cls(format_str, struct.channels, struct.freq)
    
    def __eq__(self, value: object) -> bool:
        assert isinstance(value,AudioSpec)
        return (
            value._format==self._format and 
            value._n_channels==self._n_channels and
            value.sample_rate==self.sample_rate
        )

def _list_devices(is_playback:bool):
    cnt = ctypes.c_int(0)
    if is_playback:
        dev_id_p = sdl3.SDL_GetAudioPlaybackDevices(byref(cnt))
    else: # is record
        dev_id_p = sdl3.SDL_GetAudioRecordingDevices(byref(cnt)) 
    if dev_id_p is None: # NULL
        raise SDLError()
    out = []
    for dev_index in range(cnt.value):
        dev = PhysicalAudioDevice.__new__(PhysicalAudioDevice, dev_id_p[dev_index])
        out.append(dev)
    sdl3.SDL_free(dev_id_p)
    return out

def list_playback_devices() -> list["PhysicalAudioDevice"]:
    return _list_devices(is_playback=True)

def list_recording_devices() -> list["PhysicalAudioDevice"]:
    return _list_devices(is_playback=False)

def open_default_playback_device(spec_hint:AudioSpec|None=None) -> "LogicalAudioDevice":
    if spec_hint is None:
        spec_p = ctypes.POINTER(SDL_AudioSpec)() # NULL
    else:
        spec_p = byref(spec_hint._as_sdl_struct())
    dev_id = sdl3.SDL_OpenAudioDevice(SDL_AUDIO_DEVICE_DEFAULT_PLAYBACK, spec_p)
    if dev_id==0:
        raise SDLError()
    return LogicalAudioDevice.__new__(LogicalAudioDevice, dev_id)

def open_default_recording_device(spec_hint:AudioSpec|None=None) -> "LogicalAudioDevice":
    if spec_hint is None:
        spec_p = ctypes.POINTER(SDL_AudioSpec)() # NULL
    else:
        spec_p = byref(spec_hint._as_sdl_struct())
    dev_id = sdl3.SDL_OpenAudioDevice(SDL_AUDIO_DEVICE_DEFAULT_RECORDING, spec_p)
    if dev_id==0:
        raise SDLError()
    return LogicalAudioDevice.__new__(LogicalAudioDevice, dev_id)

class _AudioDevice:
    _device_id: SDL_AudioDeviceID
    def __new__(cls, device_id):
        instance = super().__new__(cls)
        instance._device_id = SDL_AudioDeviceID(device_id)
        return instance
    @property
    def name(self) -> str:
        name = sdl3.SDL_GetAudioDeviceName(self._device_id)
        if name is None:
            raise SDLError()
        return name.decode("utf8")
    
    @property
    def playback(self):
        return bool(SDL_IsAudioDevicePlayback(self._device_id.value))
    
    @property
    def recording(self):
        return bool(not SDL_IsAudioDevicePlayback(self._device_id.value))
    
    @property
    def id(self):
        return self._device_id
    
    def _open(self, spec_hint:AudioSpec|None=None) -> "LogicalAudioDevice":
        if spec_hint is None:
            spec_p = ctypes.POINTER(SDL_AudioSpec)() # NULL
        else:
            spec = spec_hint._as_sdl_struct()
            spec_p = byref(spec)
        dev_id = sdl3.SDL_OpenAudioDevice(self._device_id, spec_p)
        if dev_id==0:
            raise SDLError()
        cls = LogicalAudioDevice
        dev = cls.__new__(cls, dev_id)
        return dev
    
    def _get_spec(self) -> AudioSpec:
        spec_struct = SDL_AudioSpec()
        success = sdl3.SDL_GetAudioDeviceFormat(self._device_id, byref(spec_struct), NULL)
        if not success:
            raise SDLError()
        return AudioSpec._from_sdl_struct(spec_struct)

class PhysicalAudioDevice(_AudioDevice):
    def __init__(self,*_):
        raise TypeError("You should never call AudioDevice() directly")
    
    def __repr__(self):
        return f"<PhysicalAudioDevice('{self.name}', id={self._device_id.value})>"
    
    def open(self, spec_hint=None) -> "LogicalAudioDevice":
        return self._open(spec_hint=spec_hint)
    
    @property
    def preferred_spec(self) -> AudioSpec:
        return self._get_spec()
    
class LogicalAudioDevice(_AudioDevice):
    _device_id: SDL_AudioDeviceID
    
    def __repr__(self):
        if self._device_id.value == 0:
            return "<LogicalAudioDevice(Closed Device)>"
        return f"<LogicalAudioDevice('{self.name}', id={self._device_id.value})>"
    
    def __del__(self):
        self.close()

    def duplicate(self, spec_hint=None) -> "LogicalAudioDevice":
        return self._open(spec_hint=spec_hint)

    def close(self):
        sdl3.SDL_CloseAudioDevice(self._device_id)
        self._device_id.value = 0

    @property
    def spec(self) -> AudioSpec:
        return self._get_spec()
    
    @property
    def paused(self):
        return sdl3.SDL_AudioDevicePaused(self._device_id)
        # no error check, that is how they design this
    
    @paused.setter
    def paused(self, value:bool):
        if not value:
            success = sdl3.SDL_ResumeAudioDevice(self._device_id)
        else:
            success = sdl3.SDL_PauseAudioDevice(self._device_id)
        if not success:
            raise SDLError()
    
    @property
    def gain(self):
        result = sdl3.SDL_GetAudioDeviceGain(self._device_id)
        if result<0:
            raise SDLError()
        return result
    
    @gain.setter
    def gain(self, value):
        v = ctypes.c_float(value)
        success = sdl3.SDL_SetAudioDeviceGain(self._device_id, v)
        if not success:
            raise SDLError()

class Audio:
    _spec: AudioSpec
    _buffer: ctypes.Array[ctypes.c_char]

    @classmethod
    def from_buffer(cls, buf, spec:AudioSpec):
        assert len(buf)%spec.frame_size==0
        instance = cls.__new__(cls)
        instance._spec = spec
        instance._buffer = ctypes.create_string_buffer(buf, len(buf))
        return instance
    
    @classmethod
    def from_wav_file(cls, filename):
        spec = SDL_AudioSpec()
        buffer = ctypes.POINTER(ctypes.c_uint8)()
        length = ctypes.c_uint32()
        success = sdl3.SDL_LoadWAV(
            filename.encode("utf8"),
            byref(spec),
            byref(buffer),
            byref(length)
        )
        if not success:
            raise SDLError()

        # There should be a more elegant way to copy
        # But we are using python, so we don't care
        copied_buf = bytes([buffer[i] for i in range(length.value)])
        sdl3.SDL_free(buffer)

        instance = cls.__new__(cls)
        instance._spec = AudioSpec._from_sdl_struct(spec)
        instance._buffer = ctypes.create_string_buffer(copied_buf, length.value)
        return instance

    @classmethod
    def join(cls, lst:list["Audio"]):
        spec = lst[0].spec
        
        new_buf = b''.join(au._buffer[:] for au in lst) # type: ignore

        instance = cls.__new__(cls)
        instance._spec = spec
        instance._buffer = ctypes.create_string_buffer(new_buf, len(new_buf))
        return instance
    
    @property    
    def spec(self):
        return self._spec

    @property
    def duration(self):
        return len(self._buffer)/self._spec.frame_size/self._spec.sample_rate

    def convert(self, spec:AudioSpec):
        src_spec = self._spec._as_sdl_struct()
        dst_spec = spec._as_sdl_struct()
        dst_buf = ctypes.POINTER(ctypes.c_uint8)()
        dst_len = ctypes.c_int()
        success = sdl3.SDL_ConvertAudioSamples(
            byref(src_spec),
            self._buffer, # type:ignore
            ctypes.c_int(len(self._buffer)),
            byref(dst_spec),
            byref(dst_buf),
            byref(dst_len)
        )
        if not success:
            raise SDLError()
        
        copied_buf = bytes([dst_buf[i] for i in range(dst_len.value)])
        sdl3.SDL_free(dst_buf)

        converted = Audio.__new__(Audio)
        converted._spec = spec
        converted._buffer = ctypes.create_string_buffer(copied_buf, dst_len.value)

        return converted
    
    # could be implemented
    # repeat()
    # stretch()
    # mic()

PG_AUDIO_STREAM_PYOBJ = "pg_audio_stream_pyobj".encode("utf8")

def _get_stream_pyobj(stream) -> "AudioStream":
    prop_id = sdl3.SDL_GetAudioStreamProperties(stream)
    if prop_id==0:
        raise SDLError()
    stream_obj_p = sdl3.SDL_GetPointerProperty(
        prop_id, # type: ignore
        PG_AUDIO_STREAM_PYOBJ, # type: ignore
        NULL # type: ignore
    )
    if not stream_obj_p:
        raise RuntimeError("SDL stream is not bind to a AudioStream object")
    return ctypes.cast(stream_obj_p, ctypes.py_object).value # type: ignore

@SDL_AudioStreamCallback
def _audio_stream_get_callback(userdata, stream, additional_amount, total_amount):
    stream_obj = _get_stream_pyobj(stream)

@SDL_AudioStreamCallback
def _audio_stream_put_callback(userdata, stream, additional_amount, total_amount):
    stream_obj = _get_stream_pyobj(stream)
    if sdl3.SDL_GetSemaphoreValue(stream_obj._semaphore_get_audio)==0:
        sdl3.SDL_SignalSemaphore(stream_obj._semaphore_get_audio)

class AudioStream:
    if typing.TYPE_CHECKING:
        _stream_p: ctypes._Pointer[SDL_AudioStream]
        _semaphore_get_audio: ctypes._Pointer[SDL_Semaphore]

    def _register_callbacks(self):
        prop_id = sdl3.SDL_GetAudioStreamProperties(self._stream_p)
        if prop_id==0:
            raise SDLError()
        success = sdl3.SDL_SetPointerProperty(
            prop_id, # type: ignore
            PG_AUDIO_STREAM_PYOBJ, # type: ignore
            ctypes.py_object(self) # type: ignore
        )
        if not success:
            raise SDLError()
        success = sdl3.SDL_SetAudioStreamGetCallback(self._stream_p, _audio_stream_get_callback, NULL)
        if not success:
            raise SDLError()
        success = sdl3.SDL_SetAudioStreamPutCallback(self._stream_p, _audio_stream_put_callback, NULL)
        if not success:
            raise SDLError()
    
    def __repr__(self):
        dev_id = sdl3.SDL_GetAudioStreamDevice(self._stream_p)
        if dev_id==0:
            return f"<AudioStream(src_spec={self.src_spec}, dst_spec={self.dst_spec})>"
        else:
            return f"<AudioStream(bound_device_id={dev_id})>"

    def __init__(self,
        binding_device:LogicalAudioDevice|None,
        src_spec:AudioSpec|None=None,
        dst_spec:AudioSpec|None=None):
        if binding_device is None:
            if src_spec is None or dst_spec is None:
                raise TypeError("'src_spec' and 'dst_spec' should be set when 'binding_device' is None")
            src_spec_struct = src_spec._as_sdl_struct()
            dst_spec_struct = dst_spec._as_sdl_struct()
        else:
            device_spec_struct = SDL_AudioSpec()
            success = sdl3.SDL_GetAudioDeviceFormat(
                binding_device._device_id,
                byref(device_spec_struct),
                NULL
            )
            if not success:
                raise SDLError()
            if binding_device.playback:
                dst_spec_struct = device_spec_struct
                if src_spec is None:
                    src_spec_struct = device_spec_struct
                else:
                    src_spec_struct = src_spec._as_sdl_struct()
            else: # recording
                src_spec_struct = device_spec_struct
                if dst_spec is None:
                    dst_spec_struct = device_spec_struct
                else:
                    dst_spec_struct = dst_spec._as_sdl_struct()
                
        stream_p = sdl3.SDL_CreateAudioStream(
            byref(src_spec_struct),
            byref(dst_spec_struct)
        )
        if not stream_p: # NULL:
            raise SDLError()
        
        self._stream_p = stream_p

        self._semaphore_get_audio = sdl3.SDL_CreateSemaphore(0) # type:ignore
        if not self._semaphore_get_audio:
            raise SDLError()

        if binding_device is not None:
            self.bind(binding_device)
        self._register_callbacks()
    
    def __del__(self):
        sdl3.SDL_DestroyAudioStream(self._stream_p)
        sdl3.SDL_DestroySemaphore(self._semaphore_get_audio)

    def bind(self, device:LogicalAudioDevice):
        success = sdl3.SDL_BindAudioStream(
            device._device_id,
            self._stream_p
        )
        if not success:
            raise SDLError()

    def unbind(self):
        sdl3.SDL_UnbindAudioStream(self._stream_p)

    @property
    def src_spec(self):
        spec_struct = SDL_AudioSpec()
        success = sdl3.SDL_GetAudioStreamFormat(
            self._stream_p, 
            byref(spec_struct),
            ctypes.POINTER(SDL_AudioSpec)(), # NULL
        )
        if not success:
            raise SDLError()
        return AudioSpec._from_sdl_struct(spec_struct)
    
    @src_spec.setter
    def src_spec(self, new_spec:AudioSpec):
        spec_struct = new_spec._as_sdl_struct()
        success = sdl3.SDL_SetAudioStreamFormat(
            self._stream_p, 
            byref(spec_struct),
            ctypes.POINTER(SDL_AudioSpec)(), # NULL
        )
        if not success:
            raise SDLError()
    
    @property
    def dst_spec(self):
        spec_struct = SDL_AudioSpec()
        success = sdl3.SDL_GetAudioStreamFormat(
            self._stream_p,
            ctypes.POINTER(SDL_AudioSpec)(), # NULL
            byref(spec_struct),
        )
        if not success:
            raise SDLError()
        return AudioSpec._from_sdl_struct(spec_struct)
    
    @dst_spec.setter
    def dst_spec(self, new_spec:AudioSpec):
        spec_struct = new_spec._as_sdl_struct()
        success = sdl3.SDL_SetAudioStreamFormat(
            self._stream_p, 
            ctypes.POINTER(SDL_AudioSpec)(), # NULL
            byref(spec_struct),
        )
        if not success:
            raise SDLError()
    
    def queued_data_length(self):
        qsize = sdl3.SDL_GetAudioStreamQueued(self._stream_p)
        if qsize<0:
            raise SDLError()
        return qsize
    
    def available_data_length(self):
        asize = sdl3.SDL_GetAudioStreamAvailable(self._stream_p)
        if asize<0:
            raise SDLError()
        return asize
    
    def flush(self):
        success = sdl3.SDL_FlushAudioStream(self._stream_p)
        if not success:
            raise SDLError()
    
    def clear(self):
        success = sdl3.SDL_ClearAudioStream(self._stream_p)
        if not success:
            raise SDLError()
    
    def put_audio(self, audio:Audio):
        success = sdl3.SDL_PutAudioStreamData(
            self._stream_p, 
            audio._buffer, # type:ignore
            ctypes.c_int(len(audio._buffer))
        )
        if not success:
            raise SDLError()
    
    def get_audio(self, timeout=-1):
        if timeout==-1:
            success = sdl3.SDL_WaitSemaphoreTimeout(
                self._semaphore_get_audio, 
                ctypes.c_int32(-1)
            )
        elif timeout>=0:
            success = sdl3.SDL_WaitSemaphoreTimeout(
                self._semaphore_get_audio,
                ctypes.c_int32(int(timeout*1000))
            )
        else:
            raise ValueError("'timeout' should be -1, 0 or a positive number")
        if not success:
            raise TimeoutError("'get_audio' timeouot")
        size = self.available_data_length()
        return self.get_audio_nowait(size)
    
    def get_audio_nowait(self, length:int) -> Audio:
        buffer = ctypes.create_string_buffer(length)
        real_size = sdl3.SDL_GetAudioStreamData(
            self._stream_p,
            buffer, # type:ignore
            ctypes.c_int(length)
        )
        if real_size<0:
            raise SDLError()
        audio_instance = Audio.__new__(Audio)
        audio_instance._buffer = ctypes.create_string_buffer(
            buffer[:], # type:ignore
            real_size
        )
        audio_instance._spec = self.dst_spec
        return audio_instance

    @property
    def gain(self):
        gain = sdl3.SDL_GetAudioStreamGain(self._stream_p)
        if gain<0:
            raise SDLError()
        return gain
    
    @gain.setter
    def gain(self,gain:float):
        success = sdl3.SDL_SetAudioStreamGain(self._stream_p, ctypes.c_float(float(gain)))
        if not success:
            raise SDLError()
    
    @property
    def frequency_ratio(self):
        ratio = sdl3.SDL_GetAudioStreamFrequencyRatio(self._stream_p)
        if ratio<0:
            raise SDLError()
        return ratio
    
    @frequency_ratio.setter
    def frequency_ratio(self, ratio:float):
        success = sdl3.SDL_SetAudioStreamFrequencyRatio(self._stream_p, ctypes.c_float(float(ratio)))
        if not success:
            raise SDLError()


