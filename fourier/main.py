import cv2
import numpy as np
import scipy.fftpack
import os

print("CWD:", os.getcwd())

def process_video(input_path, output_path, window_seconds=2):
    # Open video file
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("Error: Could not open video file.")
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    window_size = window_seconds * fps  # Number of frames in the moving window
    
    print("fps:", fps, "frame_width:", frame_width, "frame_height:", frame_height, "total_frames:", total_frames)


    # Video writer setup
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height), isColor=False)
    
    # Buffer to store the moving window of frames
    frame_buffer = []
    
    for _ in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convert to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_buffer.append(gray_frame)
        
        if len(frame_buffer) > window_size:
            frame_buffer.pop(0)  # Keep only the last 'window_size' frames
        
        if len(frame_buffer) == window_size:
            # Convert buffer to 3D numpy array (time, height, width)
            frame_stack = np.array(frame_buffer, dtype=np.float32)
            
            # Apply FFT along the time axis
            fft_result = np.fft.fft(frame_stack, axis=0)
            fft_magnitudes = np.abs(fft_result)
            
            # Find dominant frequency index for each pixel
            dominant_freq_idx = np.argmax(fft_magnitudes[1:], axis=0) + 1  # Ignore DC component
            
            # Construct new frame from the dominant frequency values
            new_frame = np.abs(fft_result[dominant_freq_idx, np.arange(frame_height)[:, None], np.arange(frame_width)])
            
            # Normalize to 0-255
            new_frame = (new_frame - new_frame.min()) / (new_frame.max() - new_frame.min()) * 255
            new_frame = new_frame.astype(np.uint8)
            
            # Write frame to output video
            out.write(new_frame)

            # Display the new frame
            cv2.imshow('Processed Frame', new_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
                break
    
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Processing complete. Saved as {output_path}")

# Example usage
input_video = "./pergamon_disco1.mp4"
output_video = "output.avi"
process_video(input_video, output_video, window_seconds=2)


# To view the output video, you can use OpenCV to display it frame by frame
def show_video(video_path):
    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('Output Video', frame)
        if cv2.waitKey(30) & 0xFF == ord('q'):  # Press 'q' to quit
            break
    cap.release()
    cv2.destroyAllWindows()

# Uncomment the line below to display the output video
show_video(output_video)
