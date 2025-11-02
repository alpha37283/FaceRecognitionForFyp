# 🎯 Face Detector Comparison: MTCNN vs RetinaFace

## Quick Overview

| Feature | MTCNN | RetinaFace |
|---------|-------|------------|
| **Speed** | ⚡ Faster | 🐢 Slower |
| **Accuracy** | ✅ Good | ✅✅ Better |
| **Small Faces** | ✅ Good | ✅✅ Excellent |
| **Side Profiles** | ⚠️ Moderate | ✅✅ Excellent |
| **Occlusions** | ⚠️ Struggles | ✅ Better |
| **CPU Usage** | 💚 Lower | 🟡 Higher |
| **Model Size** | 📦 Small (5MB) | 📦 Large (281MB) |

---

## 🚀 How to Run

### MTCNN (Default):
```bash
./run_live.sh
```
or
```bash
python main.py --mode live --method mtcnn
```

### RetinaFace:
```bash
./run_live_retinaface.sh
```
or
```bash
python main.py --mode live --method retinaface
```

---

## 📊 Detailed Comparison

### ⚡ MTCNN (Multi-task Cascaded Convolutional Networks)

**Strengths:**
- ✅ **Fast** - Real-time performance on CPU
- ✅ **Lightweight** - Small model size
- ✅ **Good for frontal faces** - High accuracy for straight-on views
- ✅ **Low resource usage** - Works well on older hardware

**Weaknesses:**
- ❌ **Side profiles** - Struggles with faces turned >30°
- ❌ **Occlusions** - Issues when face is partially hidden
- ❌ **Poor lighting** - Performance drops in dark conditions

**Best For:**
- 🎓 Attendance systems (frontal faces)
- 🚪 Access control (controlled environment)
- 💻 Older/slower computers
- ⚡ Speed-critical applications

---

### 🎯 RetinaFace (State-of-the-art)

**Strengths:**
- ✅✅ **Highly accurate** - State-of-the-art detection
- ✅✅ **Robust** - Handles difficult angles (up to 70°)
- ✅✅ **Better with occlusions** - Masks, glasses, hands
- ✅✅ **Small faces** - Detects faces at greater distances
- ✅✅ **Challenging lighting** - Better in low light

**Weaknesses:**
- ❌ **Slower** - About 2-3x slower than MTCNN
- ❌ **Larger model** - 281MB download on first use
- ❌ **Higher CPU** - More processing power needed

**Best For:**
- 📹 Surveillance systems
- 👥 Crowded scenes
- 🎭 Varied poses and angles
- 🌙 Poor lighting conditions
- 🎯 Maximum accuracy required

---

## 🧪 Performance Benchmarks

### Speed (Average FPS on CPU)
- **MTCNN:** 15-20 FPS
- **RetinaFace:** 5-8 FPS

### Detection Range
- **MTCNN:** Face angle ±30°
- **RetinaFace:** Face angle ±70°

### Minimum Face Size
- **MTCNN:** ~40x40 pixels
- **RetinaFace:** ~20x20 pixels

---

## 💡 Recommendation Guide

### Use **MTCNN** if:
- ✅ Speed is more important than perfect accuracy
- ✅ People face the camera directly
- ✅ Controlled environment (good lighting)
- ✅ Limited hardware resources
- ✅ Need real-time performance (>15 FPS)

### Use **RetinaFace** if:
- ✅ Accuracy is critical
- ✅ People move around (varied angles)
- ✅ Uncontrolled environment (variable lighting)
- ✅ Distant or small faces
- ✅ Need to detect partially hidden faces
- ✅ Have decent hardware (modern CPU)

---

## 🎛️ Tuning Tips

### For MTCNN:
```python
# Increase detection interval for speed
detection_interval=90  # 3 seconds

# More strict matching to reduce duplicates
iou_threshold=0.6
```

### For RetinaFace:
```python
# Can use lower interval due to better tracking
detection_interval=45  # 1.5 seconds

# Slightly lower threshold due to better accuracy
iou_threshold=0.4
```

---

## 📈 Real-World Scenarios

### Scenario 1: Office Attendance
**Best:** MTCNN
- Employees face camera
- Good lighting
- Speed matters for queue

### Scenario 2: Security Surveillance  
**Best:** RetinaFace
- Multiple angles
- Variable lighting
- Accuracy critical

### Scenario 3: Event Photography
**Best:** RetinaFace
- People move around
- Various poses
- Capture everyone

### Scenario 4: Classroom Attendance
**Best:** MTCNN
- Students face forward
- Controlled setting
- Fast processing needed

### Scenario 5: Outdoor Monitoring
**Best:** RetinaFace
- Variable lighting
- Different distances
- Side profiles common

---

## 🔄 Switching Between Methods

You can easily switch methods without any code changes:

**Image Detection:**
```bash
# MTCNN
python main.py --mode image --input photo.jpg --method mtcnn

# RetinaFace
python main.py --mode image --input photo.jpg --method retinaface
```

**Live Detection:**
```bash
# MTCNN (fast)
./run_live.sh

# RetinaFace (accurate)
./run_live_retinaface.sh
```

---

## 🎯 Summary

**TL;DR:**
- **Want SPEED?** → Use MTCNN
- **Want ACCURACY?** → Use RetinaFace
- **Not sure?** → Try MTCNN first, switch to RetinaFace if missing faces

Both work with the same tracking system and save faces the same way!

