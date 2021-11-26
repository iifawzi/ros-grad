#####################################################
##               Read bag from file                ##
#####################################################


# First import library
import pyrealsense2 as rs
# Import Numpy for easy array manipulation
import numpy as np
import pandas as pd
# Import OpenCV for easy image rendering
import cv2
# Import argparse for command-line options
import argparse
# Import os.path for file path manipulation
import os.path
# import base64
import base64
# import json 
import json
# import csv
import csv

# Create object for parsing command-line options
parser = argparse.ArgumentParser(description="Read recorded bag file and display depth stream")
# Add argument which takes path to a bag file as an input
parser.add_argument("-i", "--input", type=str, help="Path to the bag file")
# Parse the command line arguments to an object
args = parser.parse_args()
# Safety if no parameter have been given
if not args.input:
    print("No input paramater have been given.")
    print("For help type --help")
    exit()
# Check if the given file have bag extension
if os.path.splitext(args.input)[1] != ".bag":
    print("The given file is not of correct file format.")
    print("Only .bag files are accepted")
    exit()
try:
    # Create pipeline
    pipeline = rs.pipeline()

    # Create a config object
    config = rs.config()

    # Tell config that we will use a recorded device from file to be used by the pipeline through playback.
    rs.config.enable_device_from_file(config, args.input)

    # Configure the pipeline to stream the depth stream
    # Change this parameters according to the recorded bag file resolution
    config.enable_stream(rs.stream.depth, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, rs.format.rgb8, 30)

    # Start streaming from file
    pipeline.start(config)

    # Create opencv window to render image in
    cv2.namedWindow("Depth Stream", cv2.WINDOW_AUTOSIZE)
    
    # Create colorizer object
    colorizer = rs.colorizer()

    count=0
    numberOfFrames = 0
    # Streaming loop
    while True:
        # Get frameset of depth
        frames = pipeline.wait_for_frames()
        # Get depth frame
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        frame_number = depth_frame.get_frame_number()
        print(frame_number, count)
        if (frame_number < count ): 
            break
        else:
            numberOfFrames += 1
            count = frame_number
        # Colorize depth frame to jet colormap
        depth_color_frame = colorizer.colorize(depth_frame)
        # coco_color_frame = colorizer.colorize(color_frame)
        # Convert depth_frame to numpy array to render image in opencv
        depth_color_image = np.asanyarray(depth_color_frame.get_data())
        color_color_image = np.asanyarray(color_frame.get_data())
        # Convert depth_frame to numpy array to render image in opencv
        # Render image in opencv window
        cv2.imshow("Depth Stream", depth_color_image)
        cv2.imshow("Color Stream", color_color_image)

        # Folder to save data
        folder = './fawziTest'

        # # Write the image output
        cv2.imwrite(folder+'/'+'_%06d.png'%count, color_color_image)
        # # write the 3d array
        depth_array = []
        frame_height = depth_frame.get_height() # start from zero
        frame_width = depth_frame.get_width()# because it starts form zero
        # loop through the pixels
        for y in range(frame_height):
            depth_array.append([])
            for x in range(frame_width):
                distance = depth_frame.get_distance(x, y)
                depth_array[-1].append(distance)
        with open(folder+'/'+'_%06d.txt'%count, "w") as filehandle:
            json.dump(depth_array, filehandle)
        key = cv2.waitKey(1)
        # if pressed escape exit program
        if key == 27:
            cv2.destroyAllWindows()
            break
    print(numberOfFrames)
finally:
    pass