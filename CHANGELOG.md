# Changelog - Face Detection System

## Latest Update: Live Camera Face Saving Feature

### ✨ New Features

#### 1. **Automatic Face Cropping & Saving from Live Camera**
- Press 's' during live detection to save all currently detected faces
- Faces are automatically cropped (background removed)
- Saved to `data/cropped_faces/` directory
- Unique timestamped filenames prevent overwriting

#### 2. **Enhanced Live Detection Display**
- Shows total count of saved faces in current session
- On-screen reminder: "Press 's' to save faces"
- Real-time counter: "Faces: 2 | Saved: 5"

#### 3. **Smart File Naming**
- Format: `live_face_YYYYMMDD_HHMMSS_N.jpg`
- Timestamp ensures no duplicate filenames
- Multiple faces in one frame get sequential numbers

### 📝 Changes Made

#### Modified Files:

**`modules/detection/face_detection_live.py`**
- ✅ Added face cropping functionality
- ✅ Added manual save trigger (press 's' key)
- ✅ Added session statistics (total saved counter)
- ✅ Added on-screen instructions
- ✅ Added timestamp-based file naming
- ✅ Improved user feedback with console messages

### 🎮 How It Works

1. **Detection**: System detects faces in each frame
2. **Cropping**: Each detected face is cropped from the frame (RGB, no background)
3. **Display**: Green boxes show detected faces on screen
4. **Save**: When you press 's', all current faces are saved
5. **Naming**: Files get unique names with timestamp
6. **Feedback**: Terminal shows confirmation message

### 🚀 Usage

**Quick Start:**
```bash
./run_live.sh
```

**Manual Command:**
```bash
cd /home/alpha/Desktop/FYP/faceSystem
source myenv/bin/activate
python main.py --mode live --method mtcnn
```

**Controls:**
- Press **'s'** to save detected faces
- Press **'q'** to quit

### 📊 Example Output

**Terminal Output:**
```
[INFO] Live Face Detection Controls:
      - Press 's' to save current detected faces
      - Press 'q' to quit

[+] Saved 2 face(s) - Total saved: 2
[+] Saved 1 face(s) - Total saved: 3
[+] Saved 2 face(s) - Total saved: 5

[INFO] Session complete. Total faces saved: 5
```

**Saved Files:**
```
data/cropped_faces/
├── live_face_20251101_191530_1.jpg
├── live_face_20251101_191530_2.jpg
├── live_face_20251101_191845_1.jpg
├── live_face_20251101_192020_1.jpg
└── live_face_20251101_192020_2.jpg
```

### 🎯 Benefits

1. ✅ **No Background**: Only the face is saved, background removed
2. ✅ **High Quality**: Full RGB color, original resolution
3. ✅ **No Overwrites**: Timestamp ensures unique filenames
4. ✅ **Multi-Face**: Save multiple people at once
5. ✅ **User Control**: You decide when to save (press 's')
6. ✅ **Session Stats**: Know exactly how many faces you've captured

### 🔧 Technical Details

**Face Cropping:**
- Uses bounding box coordinates from MTCNN
- Extracts face region: `frame[y1:y2, x1:x2]`
- Converts to PIL Image for saving
- Saves as high-quality JPEG

**File Format:**
- **Format**: JPEG
- **Color**: RGB (3 channels)
- **Quality**: Standard PIL JPEG quality
- **Naming**: `live_face_YYYYMMDD_HHMMSS_N.jpg`

### 📚 Documentation

See **`LIVE_DETECTION_GUIDE.md`** for complete usage guide with tips and troubleshooting.

---

## Previous Updates

### Initial Setup (Earlier)
- ✅ Fixed import paths
- ✅ Installed missing dependencies (onnxruntime)
- ✅ Created directory structure
- ✅ Implemented MTCNN detector
- ✅ Added live detection with bounding boxes
- ✅ Added confidence score display
- ✅ Image detection mode working

