#!/bin/bash

echo "=========================================="
echo "  Live Face Detection & Saving System"
echo "=========================================="
echo ""
echo "📹 Camera will start shortly..."
echo ""
echo "🎮 Controls:"
echo "   - Press 's' to SAVE detected faces"
echo "   - Press 'q' to QUIT"
echo ""
echo "💾 Saved faces will be stored in:"
echo "   data/cropped_faces/"
echo ""
echo "Starting..."
sleep 1

cd /home/alpha/Desktop/FYP/faceSystem
source myenv/bin/activate
python main.py --mode live --method mtcnn

echo ""
echo "✅ Session ended. Check data/cropped_faces/ for saved faces!"

