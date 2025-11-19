#!/bin/bash

# Face Detection from Static Image Script

if [ -z "$1" ]; then
    echo "=========================================="
    echo "  📸 Face Detection from Image"
    echo "=========================================="
    echo ""
    echo "Usage:"
    echo "  ./detect_image.sh <image_path> [method] [--embed]"
    echo ""
    echo "Examples:"
    echo "  ./detect_image.sh data/input_images/img1.jpeg"
    echo "  ./detect_image.sh data/input_images/img1.jpeg mtcnn"
    echo "  ./detect_image.sh /path/to/photo.jpg retinaface"
    echo "  ./detect_image.sh data/input_images/img1.jpeg mtcnn --embed"
    echo ""
    echo "Methods:"
    echo "  - mtcnn      (default, fast)"
    echo "  - retinaface (accurate)"
    echo ""
    echo "Options:"
    echo "  --embed      Generate ArcFace embeddings after detection"
    echo ""
    echo "Output:"
    echo "  - Cropped faces: data/cropped_faces/"
    echo "  - Embeddings: data/embeddings/ (if --embed used)"
    echo "=========================================="
    exit 1
fi

IMAGE_PATH="$1"
METHOD="${2:-mtcnn}"  # Default to mtcnn if not specified
EMBED_FLAG=""

# Check if --embed is in arguments
if [[ "$*" == *"--embed"* ]]; then
    EMBED_FLAG="--embed"
fi

echo "=========================================="
echo "  📸 Detecting Faces in Image"
echo "=========================================="
echo ""
echo "📁 Image: $IMAGE_PATH"
echo "🔍 Method: ${METHOD^^}"
if [ -n "$EMBED_FLAG" ]; then
    echo "🧠 Embeddings: Enabled (ArcFace)"
fi
echo ""

cd /home/alpha/Desktop/FYP/faceSystem
source myenv/bin/activate
python main.py --mode image --input "$IMAGE_PATH" --method "$METHOD" $EMBED_FLAG

echo ""
echo "=========================================="
if [ -n "$EMBED_FLAG" ]; then
    echo "✅ Done! Check:"
    echo "   - Cropped faces: data/cropped_faces/"
    echo "   - Embeddings: data/embeddings/"
else
    echo "✅ Done! Check data/cropped_faces/"
fi
echo "=========================================="

