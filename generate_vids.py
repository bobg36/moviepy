import os
import shutil
from datetime import timedelta
from moviepy.editor import VideoFileClip
from moviepy.editor import VideoFileClip, concatenate_videoclips
from vidFunctions import get_timestamps, create_subclips, join_subclips, empty_folder
import cv2
import sys


pixel_coordinates = (254, 369)  # Set the new pixel coordinates
rawvids_folder = 'rawvids'
subclips_folder = 'tempsubclips'
finishedvids_folder = 'finishedvids'
assets_folder = 'assets'
henesys1 = os.path.join(assets_folder, 'henesys1.wav')
henesys2 = os.path.join(assets_folder, 'henesys2.wav')
henesys3 = os.path.join(assets_folder, 'henesys3.wav')
henesys4 = os.path.join(assets_folder, 'henesys4.wav')
musiclist = [henesys1, henesys2, henesys3, henesys4]


def copy_assets():
    source_dir = 'assets'
    destination_dir = 'tempsubclips'
    files_to_copy = ['a_intro.mp4', 'z_outro.mp4']
    for file_name in files_to_copy:
        shutil.copy(f'{source_dir}/{file_name}', f'{destination_dir}/{file_name}')
    print("Files copied successfully.")


i = 0   
for video in os.listdir(rawvids_folder):
    empty_folder(subclips_folder)
    video_path = os.path.join(rawvids_folder, video)
    print(f'Processing video: {video_path}')
    #getting timestamps
    timestamps = get_timestamps(video_path, pixel_coordinates)
    print(timestamps)
    #creating subclips
    print(f'creating subclips for: {video}')
    create_subclips(video_path, timestamps, subclips_folder)
    copy_assets()
    subclips = os.listdir(subclips_folder)
    folder_subclips = []
    for clip in subclips:
        folder_clip = os.path.join(subclips_folder, clip)
        folder_subclips.append(folder_clip)
    for item in folder_subclips:
        print(item)

    output_path = os.path.join(finishedvids_folder, f'{video}.mp4')
    music = musiclist[i % len(musiclist)]
    i += 1
    join_subclips(folder_subclips, output_path, music)
