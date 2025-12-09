#!/bin/bash

echo "=========================================="
echo "  🎯 Face Tracking (RetinaFace)"
echo "=========================================="
echo ""
echo "💡 Using RetinaFace detector:"
echo "   ✅ More accurate than MTCNN"
echo "   ✅ Better with challenging angles"
echo "   ✅ Slightly slower but robust"
echo ""
echo "📹 Camera starting..."
echo "🎮 Press 'q' to quit"
echo ""

cd "$(dirname "$0")"

# Activate virtual environment (adjust path if needed)
if [ -d "../myenv" ]; then
    source ../myenv/bin/activate
elif [ -d "myenv" ]; then
    source myenv/bin/activate
fi

python main.py --method retinaface

echo ""
echo "✅ Session ended. Check data/cropped_faces/ for saved faces!"



