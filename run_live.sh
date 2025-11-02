#!/bin/bash

echo "=========================================="
echo "  🎯 Face Tracking & Auto-Save System"
echo "=========================================="
echo ""
echo "💡 How it works:"
echo "   ✅ Tracks each face with unique ID"
echo "   ✅ Saves NEW faces automatically"
echo "   ✅ ONE save per person per visit"
echo "   ✅ No duplicates while in frame"
echo ""
echo "📹 Camera starting..."
echo "🎮 Press 'q' to quit"
echo ""

cd /home/alpha/Desktop/FYP/faceSystem
source myenv/bin/activate
python main.py --mode live --method mtcnn

echo ""
echo "✅ Session ended. Check data/cropped_faces/ for saved faces!"
