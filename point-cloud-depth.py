#####################################################
##               Read bag from file                ##
#####################################################

import sys
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
sys.path.append('/usr/local/lib/python3.9/site-packages')
# Create object for parsing command-line options
parser = argparse.ArgumentParser(description="Read recorded bag file and display depth stream in jet colormap.\
                                Remember to change the stream fps and format to match the recorded.")
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
    #config.enable_stream(rs.stream.color, rs.format.rgb8, 30)
    queue = rs.frame_queue(capacity=500)
    # Start streaming from file
    pipeline.start(config)

    # Create opencv window to render image in
    cv2.namedWindow("Depth Stream", cv2.WINDOW_AUTOSIZE)
    
    # Create colorizer object
    colorizer = rs.colorizer()
    
    lastFrameNumber=0
    # Streaming loop
    while True:
        # Get frameset of depth
        frames = pipeline.wait_for_frames()
        frame_number = frames.get_frame_number()
        if (frame_number < lastFrameNumber ): 
            break
        else:
            lastFrameNumber = frame_number
            frames.keep()
            queue.enqueue(frames)
    folder = 'pointCloudDepth'
    while True:
        framesss = queue.wait_for_frame()
        depth_frame = framesss.as_frameset().get_depth_frame()
        frame_number = depth_frame.get_frame_number()
        point_cloud = rs.pointcloud()
        points = point_cloud.calculate(depth_frame)
        verts = np.asanyarray(points.get_vertices()).view(np.float32) # xyz
        key = cv2.waitKey(1)
        np.savetxt(folder+'/'+'_%06d.txt'%frame_number, verts, newline=" ")
        if frame_number == lastFrameNumber:
            break
finally:
    pass