import os
import cv2
import numpy as np
from moviepy.editor import *
from PIL import Image
import glob

class VideoMaker:
    def __init__(self, image_dir, audio_path, output_dir="output"):
        """
        初始化视频制作器
        :param image_dir: 图片目录
        :param audio_path: 音频文件路径
        :param output_dir: 输出目录
        """
        self.image_dir = image_dir
        self.audio_path = audio_path
        self.output_dir = output_dir
        
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    def get_image_files(self):
        """获取所有图片文件"""
        extensions = ['*.jpg', '*.jpeg', '*.png']
        image_files = []
        for ext in extensions:
            image_files.extend(glob.glob(os.path.join(self.image_dir, ext)))
        return sorted(image_files)
    
    def create_zoom_clip(self, image_path, duration=2.0):
        """
        创建带缩放效果的视频片段
        :param image_path: 图片路径
        :param duration: 持续时间
        :return: 视频片段
        """
        img = ImageClip(image_path)
        
        def zoom(t):
            """缩放函数：从1.0变化到1.2"""
            return 1 + (0.2 * t/duration)
        
        clip = img.resize(zoom)
        clip = clip.set_duration(duration)
        
        # 确保视频尺寸一致，居中裁剪
        clip = clip.resize(width=1920, height=1080)
        return clip
    
    def process_image_batch(self, image_files, batch_index):
        """
        处理一批图片并生成视频
        :param image_files: 图片文件列表
        :param batch_index: 批次索引
        """
        clips = []
        for img_path in image_files:
            clip = self.create_zoom_clip(img_path)
            clips.append(clip)
        
        # 连接所有片段
        final_clip = CompositeVideoClip([clips[0]])
        for clip in clips[1:]:
            final_clip = CompositeVideoClip([final_clip, clip.set_start(final_clip.duration)])
            
        # 添加音频
        audio = AudioFileClip(self.audio_path)
        # 裁剪音频至视频长度
        audio = audio.subclip(0, final_clip.duration)
        final_clip = final_clip.set_audio(audio)
        
        # 保存视频 - 添加编码器参数
        output_path = os.path.join(self.output_dir, f'output_{batch_index}.mp4')
        final_clip.write_videofile(
            output_path,
            fps=30,
            codec='libx264',
            audio_codec='aac',
            preset='medium',
            threads=4
        )
        
        # 清理内存
        final_clip.close()
        audio.close()
        for clip in clips:
            clip.close()
            
    def process_all_images(self):
        """处理所有图片"""
        image_files = self.get_image_files()
        
        # 添加调试信息
        print(f"找到的图片文件: {len(image_files)} 个")
        if len(image_files) == 0:
            print(f"在目录 '{self.image_dir}' 中没有找到图片文件")
            return
        
        # 按每10张图片分批处理
        batch_size = 10
        for i in range(0, len(image_files), batch_size):
            batch = image_files[i:i+batch_size]
            print(f"正在处理第 {i//batch_size + 1} 批视频...")
            print(f"本批次处理的图片: {batch}")
            self.process_image_batch(batch, i//batch_size + 1)
            
def main():
    # 获取当前脚本所在目录的绝对路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 设置路径 - 去掉@符号
    image_dir = os.path.join(base_dir, "演示图")
    audio_path = os.path.join(base_dir, "biubiubiu.m4a")
    
    # 打印路径信息进行调试
    print(f"图片目录路径: {image_dir}")
    print(f"音频文件路径: {audio_path}")
    print(f"目录是否存在: {os.path.exists(image_dir)}")
    print(f"音频文件是否存在: {os.path.exists(audio_path)}")
    
    # 创建视频制作器实例
    maker = VideoMaker(image_dir, audio_path)
    
    # 处理所有图片
    maker.process_all_images()
    
if __name__ == "__main__":
    main() 