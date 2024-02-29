import cv2
import os
from datetime import timedelta
from moviepy.editor import VideoFileClip, concatenate_videoclips, concatenate_audioclips, AudioFileClip, CompositeAudioClip


import sys
import shutil

win = [241, 200, 61]
blue = [51, 110, 136]
loss = [146, 139, 119]

def get_timestamps(video_path, pixel_coordinates):
    timestamps_list = []
    cap = cv2.VideoCapture(video_path)  # Load the video
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    frame_rate = cap.get(cv2.CAP_PROP_FPS)  # Get video frame rate
    total_seconds = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / frame_rate)
    minutes = 0
    endseconds = 0
    currTimestamps = (0, 0)
    prevTimestamps = (-1, 0)
    for second in range(total_seconds):
        timeformat = str(timedelta(seconds=second))
        frame_number = int(second * frame_rate)  # Calculate the frame number
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)  # Set the video position to the frame
        ret, frame = cap.read()  # Read the frame
        if not ret:
            print(f"Error: Could not read frame at second {second}.")
            continue
        bgr_color = frame[pixel_coordinates[1], pixel_coordinates[0]].tolist()
        rgb_color = bgr_color[::-1]  # Reverse the color from BGR to RGB
        # print(f"Second {second}: RGB Color {rgb_color}")
        if second%60 == 0:
            minutes = minutes + 1
            # print(str(second/60) + ' minutes has passed')
        if rgb_color == win or rgb_color == loss:
            segmentEnd = timeformat
            endseconds = endseconds + 1
            if endseconds >= 2:
                currTimestamps = (segmentStart, segmentEnd)
            if endseconds >= 2 and currTimestamps[0] != prevTimestamps[0]:
                print('appending' + str(currTimestamps))
                timestamps_list.append(currTimestamps)
                prevTimestamps = currTimestamps
                endseconds = 0
        elif rgb_color == blue:
            segmentStart = timeformat
    cap.release()  # Release the video capture object
    return timestamps_list

def create_subclips(video_path, segments, output_folder):
    if not os.path.exists(output_folder): # Ensure the output directory exists
        os.makedirs(output_folder)
    clip = VideoFileClip(video_path) # Load the video
    for i, (start, end) in enumerate(segments): # Loop through each segment and create a subclip
        subclip = clip.subclip(start, end) # Create the subclip
        output_filename = f"subclip_{i+1}_{start.replace(':', '-')}_to_{end.replace(':', '-')}.mp4" # Define the output filename
        output_path = os.path.join(output_folder, output_filename)
        subclip.write_videofile(output_path, codec='libx264', audio_codec='aac') # Write the subclip to a file
    clip.close()  # Close the main video clip after all subclips are processed
    print(f"Created subclip: {output_path}")


def join_subclips(subclip_paths, output_path, music_path):
    clips = [VideoFileClip(path) for path in subclip_paths] # Load all the subclips
    final_clip = concatenate_videoclips(clips)  # Concatenate the clips

    music = AudioFileClip(music_path)
    total_duration_needed = final_clip.duration

    repeated_music_clips = []
    current_duration = 0
    while current_duration < total_duration_needed:
        repeated_music_clips.append(music)
        current_duration += music.duration

    looped_music = concatenate_audioclips(repeated_music_clips)
    looped_music = looped_music.set_duration(final_clip.duration)
    final_clip.audio = looped_music

    final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
    print(f"Joined video with looped music saved to {output_path}")
    for clip in clips:
        clip.close()
    music.close()  # Close the music clip

def empty_folder(folder_path):
    if os.path.exists(folder_path):    # Check if the folder exists
        files = os.listdir(folder_path) # Get a list of files in the folder
        if files: # Check if the list is not empty, indicating that there are files
            # Loop through each file and remove it
            for file in files:
                file_path = os.path.join(folder_path, file)
                try:
                    # If it's a file, delete it. If it's a directory, delete everything inside it
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')
            print("Folder emptied successfully.")
        else:
            print("Folder is already empty.")
    else:
        print("Folder does not exist.")