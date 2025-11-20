from ..base import *

cv2 = LazyImport('cv2')
# ffmpeg = LazyImport('ffmpeg')
# if 0:
#     import cv2


class Video_custom:
    def __init__(self, video_path):
        self.video_path = video_path
        self._video_info = {}

    def open_capture(self):
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise Exception(f"Error: Could not open video {self.video_path}")
        return cap
    
    @staticmethod
    def close_capture(cap):
        cap.release()

    def _query_video_info(self, key):
        if not self._video_info:
            cap = self.open_capture()
            self._video_info ={
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            }
            self.close_capture(cap)
        
        if key in self._video_info:
            return self._video_info[key]
        else:
            raise Exception(f'wrong key of video info: {key}')
    
    def cal_num_frames_by_new_fps(self, new_fps:float) -> int:
        cap = self.open_capture()
        old_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        self.close_capture(cap)
        if new_fps >= old_fps:
            new_frames = total_frames
        else:
            new_frames = total_frames / old_fps * new_fps
        new_frames = max(new_frames, 1)
        return int(new_frames+0.1)

    @property
    def fps(self) -> float:
        return self._query_video_info('fps')
    
    @property
    def total_frames(self) -> int:
        return self._query_video_info('total_frames')

    def __len__(self) -> int:
        return self.total_frames

    @property
    def duration(self) -> float:
        return self.total_frames / self.fps
    
    @property
    def width(self) -> int:
        return self._query_video_info('width')
    
    @property
    def height(self) -> int:
        return self._query_video_info('height')

    @property
    def shape(self) -> Tuple[int]:
        "(height, width)"
        return (self.height, self.width)

    def edit_video(
        self, new_video_path,
        width, height, fps,
        terminal_log=False, 
    ):
        """
        """
        try:
            import ffmpeg
        except Exception as err:
            print(err)
            print('Dowload ffmpeg by:\nsudo apt-get install ffmpeg\npip install ffmpeg-python')
            exit(0)

        video_path = path(self.video_path)
        assert video_path.exists()
        new_video_path = str(new_video_path)
        make_path(file_path=new_video_path)
        assert path(new_video_path).exists()

        stream = ffmpeg.input(video_path)
        stream = stream.filter('fps', fps=fps, round='up')
        stream = stream.filter('scale', width, height)
        if terminal_log:
            stream = stream.output(new_video_path)
        else:
            # print(new_video_path)
            stream = stream.output(
                new_video_path, 
                loglevel='error',
            )
        stream = stream.overwrite_output()
        stream = stream.run()
        # try:
        #     stream.run()
        # except ffmpeg.Error as e:
        #     raise Exception('Error:', e.stderr.decode())
        # ffmpeg.run(stream)
        return

    def __getitem__(self, index, cap=None, rgb=True):
        "return PIL.Image or None"
        from PIL import Image
        if index < 0:
            index += self.total_frames
        if not 0 <= index < self.total_frames:
            return None

        if cap is None:
            cap = self.open_capture()
            cap.set(cv2.CAP_PROP_POS_FRAMES, index)
            ret, frame = cap.read()
            self.close_capture(cap)
        else:
            cap.set(cv2.CAP_PROP_POS_FRAMES, index)
            ret, frame = cap.read()

        if not ret:
            return None
        if rgb:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame)
        return pil_image

    def __iter__(self):
        def _func():
            cap = self.open_capture()
            for _index in range(len(self)):
                yield self.__getitem__(index=_index, cap=cap)
            self.close_capture(cap)
        return _func()

    def hash_str(self, key_frames=(0,1,2,3,4,-5,-4,-3,-2,-1)) -> str:
        """
        total_frame + fps + phash of key frames
        """
        import imagehash
        from PIL import Image

        cap = self.open_capture()
        
        hash_strings = [f'{self.total_frames}_{self.fps}_']
        key_frames = [p if p >=0 else self.total_frames+p for p in key_frames]
        for _frame_id in key_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, _frame_id)
            ret, frame = cap.read()
            if not ret:
                break
            # frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame)
            hash_value = imagehash.phash(pil_image)
            hash_strings.append(str(hash_value))
        
        self.close_capture(cap)
        final_hash = '_'.join(hash_strings)
        return final_hash
    