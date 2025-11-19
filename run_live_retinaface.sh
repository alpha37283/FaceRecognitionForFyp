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

cd /home/alpha/Desktop/FYP/faceSystem
source myenv/bin/activate
python main.py --mode live --method retinaface

echo ""
echo "✅ Session ended. Check data/cropped_faces/ for saved faces!"



