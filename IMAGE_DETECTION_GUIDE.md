# 📸 Static Image Face Detection Guide

## ✅ Status: WORKING

Both MTCNN and RetinaFace work perfectly for detecting faces in static images!

---

## 🚀 Quick Start

### Method 1: Using the Script (Easiest)

```bash
# Basic usage (uses MTCNN by default)
./detect_image.sh data/input_images/img1.jpeg

# Specify method
./detect_image.sh data/input_images/img1.jpeg mtcnn
./detect_image.sh data/input_images/img1.jpeg retinaface

# Use full path
./detect_image.sh /path/to/your/photo.jpg mtcnn
```

### Method 2: Direct Command

```bash
# Activate virtual environment
source myenv/bin/activate

# MTCNN (fast)
python main.py --mode image --input data/input_images/img1.jpeg --method mtcnn

# RetinaFace (accurate)
python main.py --mode image --input data/input_images/img1.jpeg --method retinaface
```

---

## 📁 File Locations

### Input Images
Place your images in:
```
data/input_images/
```

### Output (Cropped Faces)
Faces are saved to:
```
data/cropped_faces/
```

**Naming:** `face_1.jpg`, `face_2.jpg`, etc.

---

## 🎯 What Happens

1. **Reads** your image
2. **Detects** all faces using chosen method
3. **Crops** each face (removes background)
4. **Saves** to `data/cropped_faces/`

---

## 📊 Example Results

### Test with img1.jpeg:

**MTCNN:**
```bash
./detect_image.sh data/input_images/img1.jpeg mtcnn
```
Output: `[+] Saved 2 face(s) to data/cropped_faces/`

**RetinaFace:**
```bash
./detect_image.sh data/input_images/img1.jpeg retinaface
```
Output: `[+] Saved 1 face(s) to data/cropped_faces/`

**Why different?**
- MTCNN: More sensitive, may detect reflections/small faces
- RetinaFace: More conservative, focuses on clear faces

---

## 🎛️ Choosing a Method

### Use MTCNN when:
- ✅ Speed matters
- ✅ Processing many images
- ✅ Good quality frontal photos
- ✅ Want to catch all possible faces

### Use RetinaFace when:
- ✅ Accuracy is critical
- ✅ Difficult angles/poses
- ✅ Poor lighting conditions
- ✅ Want only clear, confident detections

---

## 📋 Supported Formats

- ✅ JPEG/JPG
- ✅ PNG
- ✅ BMP
- ✅ TIFF

---

## 💡 Tips

### 1. Batch Processing
Process multiple images:
```bash
for img in data/input_images/*.jpg; do
    ./detect_image.sh "$img" mtcnn
done
```

### 2. Different Locations
You can use images from anywhere:
```bash
./detect_image.sh ~/Pictures/family.jpg
./detect_image.sh /home/user/Downloads/photo.png
```

### 3. Check Results
After detection, view saved faces:
```bash
ls -lh data/cropped_faces/
```

### 4. Clear Old Results
Before new detection (optional):
```bash
rm data/cropped_faces/*.jpg
```

---

## 🐛 Troubleshooting

### "Image not found"
- Check the file path is correct
- Use absolute path if relative doesn't work
- Ensure image exists: `ls -l your_image.jpg`

### "No faces detected"
- Try the other method (MTCNN vs RetinaFace)
- Check image quality
- Ensure faces are clearly visible
- Try adjusting image brightness

### "Module not found"
- Activate virtual environment first:
  ```bash
  source myenv/bin/activate
  ```

---

## 📊 Performance

| Method | Speed | Faces in img1.jpeg |
|--------|-------|-------------------|
| MTCNN | ⚡ Fast (< 1 sec) | 2 faces |
| RetinaFace | 🐢 Slower (2-3 sec) | 1 face |

---

## 🎯 Complete Examples

### Example 1: Quick Detection
```bash
# Put your image in input folder
cp ~/my_photo.jpg data/input_images/

# Detect faces
./detect_image.sh data/input_images/my_photo.jpg

# View results
ls data/cropped_faces/
```

### Example 2: Compare Methods
```bash
# Try MTCNN
./detect_image.sh data/input_images/img1.jpeg mtcnn
# Output: Saved 2 face(s)

# Clear results
rm data/cropped_faces/*.jpg

# Try RetinaFace
./detect_image.sh data/input_images/img1.jpeg retinaface
# Output: Saved 1 face(s)
```

### Example 3: Process from Desktop
```bash
# Direct path to desktop image
./detect_image.sh ~/Desktop/party_photo.jpg retinaface

# Check results
ls -lh data/cropped_faces/
```

---

## ✨ Features

✅ **Automatic cropping** - Only face, no background  
✅ **Multiple faces** - Saves all detected faces  
✅ **Any location** - Works with full paths  
✅ **Two methods** - Choose speed or accuracy  
✅ **Easy to use** - Simple script interface  

---

## 📚 Quick Reference

```bash
# Show help
./detect_image.sh

# Default (MTCNN, fast)
./detect_image.sh path/to/image.jpg

# RetinaFace (accurate)
./detect_image.sh path/to/image.jpg retinaface

# View saved faces
ls data/cropped_faces/

# Clear old results
rm data/cropped_faces/*.jpg
```

---

**Your static image face detection is fully working! 📸✅**

