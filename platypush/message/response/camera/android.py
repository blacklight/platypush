from typing import List

from platypush.message.response.camera import CameraResponse


class AndroidCameraStatusResponse(CameraResponse):
    """
    Example response:

      .. code-block:: json

        {
            "stream_url": "https://192.168.1.30:8080/video",
            "image_url": "https://192.168.1.30:8080/photo.jpg",
            "audio_url": "https://192.168.1.30:8080/audio.wav",
            "orientation": "landscape",
            "idle": "off",
            "audio_only": "off",
            "overlay": "off",
            "quality": "49",
            "focus_homing": "off",
            "ip_address": "192.168.1.30",
            "motion_limit": "250",
            "adet_limit": "200",
            "night_vision": "off",
            "night_vision_average": "2",
            "night_vision_gain": "1.0",
            "motion_detect": "off",
            "motion_display": "off",
            "video_chunk_len": "60",
            "gps_active": "off",
            "video_size": "1920x1080",
            "mirror_flip": "none",
            "ffc": "off",
            "rtsp_video_formats": "",
            "rtsp_audio_formats": "",
            "video_connections": "0",
            "audio_connections": "0",
            "ivideon_streaming": "off",
            "zoom": "100",
            "crop_x": "50",
            "crop_y": "50",
            "coloreffect": "none",
            "scenemode": "auto",
            "focusmode": "continuous-video",
            "whitebalance": "auto",
            "flashmode": "off",
            "antibanding": "off",
            "torch": "off",
            "focus_distance": "0.0",
            "focal_length": "4.25",
            "aperture": "1.7",
            "filter_density": "0.0",
            "exposure_ns": "9384",
            "frame_duration": "33333333",
            "iso": "100",
            "manual_sensor": "off",
            "photo_size": "1920x1080"
        }

    """

    attrs = {
        'orientation', 'idle', 'audio_only', 'overlay', 'quality', 'focus_homing',
        'ip_address', 'motion_limit', 'adet_limit', 'night_vision',
        'night_vision_average', 'night_vision_gain', 'motion_detect',
        'motion_display', 'video_chunk_len', 'gps_active', 'video_size',
        'mirror_flip', 'ffc', 'rtsp_video_formats', 'rtsp_audio_formats',
        'video_connections', 'audio_connections', 'ivideon_streaming', 'zoom',
        'crop_x', 'crop_y', 'coloreffect', 'scenemode', 'focusmode',
        'whitebalance', 'flashmode', 'antibanding', 'torch', 'focus_distance',
        'focal_length', 'aperture', 'filter_density', 'exposure_ns',
        'frame_duration', 'iso', 'manual_sensor', 'photo_size',
    }

    def __init__(self, *args,
                 name: str = None,
                 stream_url: str = None,
                 image_url: str = None,
                 audio_url: str = None,
                 orientation: str = None,
                 idle: str = None,
                 audio_only: str = None,
                 overlay: str = None,
                 quality: str = None,
                 focus_homing: str = None,
                 ip_address: str = None,
                 motion_limit: str = None,
                 adet_limit: str = None,
                 night_vision: str = None,
                 night_vision_average: str = None,
                 night_vision_gain: str = None,
                 motion_detect: str = None,
                 motion_display: str = None,
                 video_chunk_len: str = None,
                 gps_active: str = None,
                 video_size: str = None,
                 mirror_flip: str = None,
                 ffc: str = None,
                 rtsp_video_formats: str = None,
                 rtsp_audio_formats: str = None,
                 video_connections: str = None,
                 audio_connections: str = None,
                 ivideon_streaming: str = None,
                 zoom: str = None,
                 crop_x: str = None,
                 crop_y: str = None,
                 coloreffect: str = None,
                 scenemode: str = None,
                 focusmode: str = None,
                 whitebalance: str = None,
                 flashmode: str = None,
                 antibanding: str = None,
                 torch: str = None,
                 focus_distance: str = None,
                 focal_length: str = None,
                 aperture: str = None,
                 filter_density: str = None,
                 exposure_ns: str = None,
                 frame_duration: str = None,
                 iso: str = None,
                 manual_sensor: str = None,
                 photo_size: str = None,
                 **kwargs):

        self.status = {
            "name": name,
            "stream_url": stream_url,
            "image_url": image_url,
            "audio_url": audio_url,
            "orientation": orientation,
            "idle": True if idle == "on" else False,
            "audio_only": True if audio_only == "on" else False,
            "overlay": True if overlay == "on" else False,
            "quality": int(quality or 0),
            "focus_homing": True if focus_homing == "on" else False,
            "ip_address": ip_address,
            "motion_limit": int(motion_limit or 0),
            "adet_limit": int(adet_limit or 0),
            "night_vision": True if night_vision == "on" else False,
            "night_vision_average": float(night_vision_average or 0),
            "night_vision_gain": float(night_vision_gain or 0),
            "motion_detect": True if motion_detect == "on" else False,
            "motion_display": True if motion_display == "on" else False,
            "video_chunk_len": int(video_chunk_len or 0),
            "gps_active": True if gps_active == "on" else False,
            "video_size": video_size,
            "mirror_flip": mirror_flip,
            "ffc": True if ffc == "on" else False,
            "rtsp_video_formats": rtsp_video_formats,
            "rtsp_audio_formats": rtsp_audio_formats,
            "video_connections": int(video_connections or 0),
            "audio_connections": int(audio_connections or 0),
            "ivideon_streaming": True if ivideon_streaming == "on" else False,
            "zoom": int(zoom or 0),
            "crop_x": int(crop_x or 0),
            "crop_y": int(crop_y or 0),
            "coloreffect": coloreffect,
            "scenemode": scenemode,
            "focusmode": focusmode,
            "whitebalance": whitebalance,
            "flashmode": True if flashmode == "on" else False,
            "antibanding": True if antibanding == "on" else False,
            "torch": True if torch == "on" else False,
            "focus_distance": float(focus_distance or 0),
            "focal_length": float(focal_length or 0),
            "aperture": float(aperture or 0),
            "filter_density": float(filter_density or 0),
            "exposure_ns": int(exposure_ns or 0),
            "frame_duration": int(frame_duration or 0),
            "iso": int(iso or 0),
            "manual_sensor": True if manual_sensor == "on" else False,
            "photo_size": photo_size,
        }

        super().__init__(*args, output=self.status, **kwargs)


class AndroidCameraStatusListResponse(CameraResponse):
    def __init__(self, status: List[AndroidCameraStatusResponse], **kwargs):
        self.status = [s.status for s in status]
        super().__init__(output=self.status, **kwargs)


class AndroidCameraPictureResponse(CameraResponse):
    def __init__(self, image_file: str,  *args, **kwargs):
        self.image_file = image_file
        super().__init__(*args, output={'image_file': image_file}, **kwargs)


# vim:sw=4:ts=4:et:
