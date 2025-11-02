#!/bin/bash

# Face Detection from Static Image Script

if [ -z "$1" ]; then
    echo "=========================================="
    echo "  📸 Face Detection from Image"
    echo "=========================================="
    echo ""
    echo "Usage:"
    echo "  ./detect_image.sh <image_path> [method]"
    echo ""
    echo "Examples:"
    echo "  ./detect_image.sh data/input_images/img1.jpeg"
    echo "  ./detect_image.sh data/input_images/img1.jpeg mtcnn"
    echo "  ./detect_image.sh /path/to/photo.jpg retinaface"
    echo ""
    echo "Methods:"
    echo "  - mtcnn      (default, fast)"
    echo "  - retinaface (accurate)"
    echo ""
    echo "Output: data/cropped_faces/"
    echo "=========================================="
    exit 1
fi

IMAGE_PATH="$1"
METHOD="${2:-mtcnn}"  # Default to mtcnn if not specified

echo "=========================================="
echo "  📸 Detecting Faces in Image"
echo "=========================================="
echo ""
echo "📁 Image: $IMAGE_PATH"
echo "🔍 Method: ${METHOD^^}"
echo ""

cd /home/alpha/Desktop/FYP/faceSystem
source myenv/bin/activate
python main.py --mode image --input "$IMAGE_PATH" --method "$METHOD"

echo ""
echo "=========================================="
echo "✅ Done! Check data/cropped_faces/"
echo "=========================================="

