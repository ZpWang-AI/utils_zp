from .core import *


cv2 = LazyImport('cv2')
ffmpeg = LazyImport('ffmpeg')
# if 0:
#     import cv2


def get_video_info(video_path, print_res=False) -> Dict[str, Any]:
    """
    return {
        'fps': fps,  # float
        'width': width,  # int
        'height': height,  # int
    }
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception(f"Error: Could not open video {video_path}")
    
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

