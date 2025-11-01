# Live Face Detection & Saving Guide

## 🎥 Features

Your live camera system now has **automatic face cropping and saving**!

### What It Does:
1. ✅ Detects faces in real-time from your webcam
2. ✅ Shows green bounding boxes around each face
3. ✅ Displays confidence scores for each detection
4. ✅ **Crops detected faces (removes background)**
5. ✅ **Saves cropped faces to `data/cropped_faces/`**
6. ✅ Uses timestamps to avoid overwriting files
7. ✅ Shows counter of how many faces you've saved

## 🎮 Controls

When the webcam window is open:

| Key | Action |
|-----|--------|
| **`s`** | Save all currently detected faces |
| **`q`** | Quit the application |

## 🚀 How to Run

### Quick Start:
```bash
cd /home/alpha/Desktop/FYP/faceSystem
source myenv/bin/activate
python main.py --mode live --method mtcnn
```

### What You'll See:

The webcam window will show:
- **Green boxes** around detected faces
- **"Faces: 2 | Saved: 5"** - Current faces detected and total saved
- **"Press 's' to save faces"** - Reminder of the save key
- **Confidence scores** above each face (e.g., "Face: 0.99")

## 💾 Saving Faces

### Manual Save (Press 's'):
1. When you see faces detected in the window
2. Press the **'s' key** on your keyboard
3. All detected faces in the current frame will be cropped and saved
4. Terminal will show: `[+] Saved 2 face(s) - Total saved: 5`

### File Naming:
Saved faces are named with timestamps to prevent overwriting:
```
live_face_20251101_191845_1.jpg
live_face_20251101_191845_2.jpg
live_face_20251101_192130_1.jpg
```

Format: `live_face_YYYYMMDD_HHMMSS_N.jpg`
- **YYYYMMDD**: Date (Year, Month, Day)
- **HHMMSS**: Time (Hour, Minute, Second)
- **N**: Face number in that frame (1, 2, 3, etc.)

## 📁 Output Location

All cropped faces are saved to:
```
/home/alpha/Desktop/FYP/faceSystem/data/cropped_faces/
```

## 🔍 What Gets Saved

Each saved file contains:
- ✅ **Only the face** (cropped to bounding box)
- ✅ **No background** (removed automatically)
- ✅ **Full color RGB image**
- ✅ **JPG format** for compatibility

## 📊 Example Session

```bash
$ python main.py --mode live --method mtcnn

[INFO] Live Face Detection Controls:
      - Press 's' to save current detected faces
      - Press 'q' to quit

# User presses 's' when seeing 2 faces
[+] Saved 2 face(s) - Total saved: 2

# User moves, now 1 face detected, presses 's' again
[+] Saved 1 face(s) - Total saved: 3

# User presses 'q' to quit
[INFO] Session complete. Total faces saved: 3
```

## 💡 Tips

1. **Good Lighting**: Better lighting = better detection
2. **Face the Camera**: Front-facing works best
3. **Multiple People**: All detected faces save when you press 's'
4. **Don't Spam 's'**: Wait a moment between saves to avoid duplicates
5. **Check Output**: View saved faces in `data/cropped_faces/` folder

## 🛠️ Troubleshooting

### No Faces Detected?
- Ensure good lighting
- Face the camera directly
- Move closer to the camera
- Check if webcam is working: `ls /dev/video*`

### 's' Key Not Working?
- Make sure the **webcam window is in focus** (click on it)
- Don't press too fast, wait for the save confirmation

### Saved Images Too Dark?
- The cropped faces maintain original quality
- Improve room lighting for better results

## 🎯 Use Cases

Perfect for:
- 📸 Building face recognition datasets
- 👥 Capturing multiple people's faces
- 🎓 Academic face detection projects
- 🔬 Testing and research
- 📚 Creating training data for ML models

