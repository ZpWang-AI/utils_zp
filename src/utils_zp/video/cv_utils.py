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
        method:Literal['cv2','decord','ffmpeg']='cv2',
    ):
        video_path = path(self.video_path); assert video_path.exists()
        new_video_path = str(new_video_path); make_path(file_path=new_video_path)
        fps = min(fps, self.fps)

        def _use_decord():
            try:
                from decord import VideoReader, cpu, gpu
                import imageio
            except Exception as err:
                print(err)
                print('Install the required libraries:\npip install decord imageio[ffmpeg]')
                exit(0)

            video_reader = VideoReader(str(video_path), width=width, height=height)
            new_video_writer = imageio.get_writer(str(new_video_path), fps=fps)

            time_source = 0
            time_target = 0
            gap_source = 1/self.fps
            gap_target = 1/fps
            for frame in video_reader:
                if time_source >= time_target:
                    time_target += gap_target
                    # frame_np = frame.asnumpy()
                    # frame_resized = cv2.resize(frame_np, (width, height))
                    new_video_writer.append_data(frame.asnumpy())
                time_source += gap_source

            new_video_writer.close()
        
        def _use_ffmpeg():
            try:
                import ffmpeg
            except Exception as err:
                print(err)
                print('Dowload ffmpeg by:\nsudo apt install ffmpeg\npip install ffmpeg-python')
                exit(0)

            cmd = [
                'ffmpeg',
                '-i', str(self.video_path),       # 输入文件
                '-an',                       # 跳过音频 (no audio)
                '-vf', f'fps={fps},scale={width}:{height}:flags=fast_bilinear',  # 设置帧率和缩放
                '-c:v', 'mpeg4',  
                '-preset', 'fast',     
                '-y',

                str(new_video_path)
            ]
            # 执行命令，丢弃不必要输出以提升性能
            subprocess.run(cmd, capture_output=True, check=True)
            return

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
        
        def _use_cv2():
            cap = cv2.VideoCapture(str(video_path))
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(new_video_path, fourcc, fps, (width, height))
            
            time_source, time_target = 0.0, 0.0
            gap_source, gap_target = 1.0/self.fps, 1.0/fps
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if time_source >= time_target:
                    time_target += gap_target
                    frame_resized = cv2.resize(frame, (width, height))
                    writer.write(frame_resized)
                
                time_source += gap_source
            
            # 释放资源
            cap.release()
            writer.release()
            cv2.destroyAllWindows()

        if method == 'cv2': _use_cv2()
        elif method == 'decord': _use_decord()
        elif method == 'ffmpeg': _use_ffmpeg()
        else: raise Exception()

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
    