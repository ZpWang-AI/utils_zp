from utils_zp import *
# video

_video = Video_custom(r'D:\NewDownload\ac5ssx.mp4')
with PrintInfoManager(print_running_time=True):
    print(_video.hash_str())
with PrintInfoManager(print_running_time=True):
    print(len(list(_video)))
# print(
#     # _video.fps,
#     # _video.total_frames,
#     _video.shape,
#     _video.duration,
#     _video.hash_str(),
#     len(list(_video)),
#     sep='\n'
# )

