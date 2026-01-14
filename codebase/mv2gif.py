
from moviepy.editor import VideoFileClip

def convert_video_to_gif(input_video, output_gif, fps=60):
    # 加载视频剪辑
    video_clip = VideoFileClip(input_video)
    video_clip = video_clip.speedx(factor=1)
    # 设置帧率
    video_clip = video_clip.set_fps(fps)

    # 选择视频的一部分（可选）
    # video_clip = video_clip.subclip(start_time, end_time)
    # 调整视频速度
    

    # 将视频保存为GIF
    video_clip.write_gif(output_gif)

    # 关闭视频剪辑
    video_clip.close()

# 指定输入视频文件和输出GIF文件
input_video_file = 'ToS.mp4'
output_gif_file = 'ToS.gif'
# 调用函数进行转换
convert_video_to_gif(input_video_file, output_gif_file)
