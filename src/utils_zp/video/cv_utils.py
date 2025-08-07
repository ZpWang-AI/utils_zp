from ..base import *

cv2 = LazyImport('cv2')
ffmpeg = LazyImport('ffmpeg')
# if 0:
#     import cv2


class Video_:
    def __init__(self, video_path):
        self.video_path = video_path
        self._video_info = {}

    def open_capture(self):
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise Exception(f"Error: Could not open video {self.video_path}")
        return cap
    
    def close_capture(self, cap):
        cap.release()

    @property
    def fps(self):
        if 'fps' in self._video_info:
            

    def get_video_info(video_path, print_res=False) -> Dict[str, Any]:
        """
        return {
            'fps': fps,  # float
            'total_frames', 
            'width': width,  # int
            'height': height,  # int
        }
        """
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        res = {
            'fps': fps,
            'width': width,
            'height': height,
        }
        if print_res:
            print(f'fps: {fps:.1f} | width: {width:d} | height: {height:d}')
        return res


    def edit_video(
        video_path, new_video_path,
        width, height, fps,
        terminal_log=False, 
    ):
        """
        """
        import ffmpeg

        video_path = path(video_path)
        assert video_path.exists()
        new_video_path = str(new_video_path)
        make_path(file_path=new_video_path)

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


    def iterate_video(video_path) -> list:
        """
        return List["PIL.Image"]
        """
        import cv2
        from PIL import Image

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Error: Could not open video.")

        images = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            images.append(pil_image)

        cap.release()
        return images
        

    def get_video_duration(video_path):
        import cv2

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Error: Could not open video.")

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

        duration = frame_count / fps
        # duration = float(f'{duration:.2f}')
        cap.release()
        return duration


    def hash_video(video_path, key_frames=(0,1,2,3,4,-5,-4,-3,-2,-1)) -> str:
        """
        total_frame + fps + phash of key frames
        """
        import cv2
        import imagehash
        from PIL import Image

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Error: Could not open video.")
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        hash_strings = [f'{total_frames}_{fps}_']
        
        key_frames = [p if p >=0 else total_frames+p for p in key_frames]
        for _frame_id in key_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, _frame_id)
            ret, frame = cap.read()
            if not ret:
                break
            # frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame)
            hash_value = imagehash.phash(pil_image)
            hash_strings.append(str(hash_value))
        
        cap.release()
        final_hash = '_'.join(hash_strings)
        return final_hash