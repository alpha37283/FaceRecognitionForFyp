#!/bin/bash

echo "=========================================="
echo "  Live Face Detection with MTCNN"
echo "=========================================="
echo ""
echo "Instructions:"
echo "  - A window will open showing your webcam feed"
echo "  - Green boxes will appear around detected faces"
echo "  - Press 'q' to quit"
echo ""
echo "Starting in 2 seconds..."
sleep 2

cd /home/alpha/Desktop/FYP/faceSystem
source myenv/bin/activate
python main.py --mode live --method mtcnn

