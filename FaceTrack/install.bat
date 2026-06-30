@echo off
title FaceTrack Pro — Install Dependencies
color 0A
echo.
echo  ╔══════════════════════════════════════════╗
echo  ║     FaceTrack Pro — Installing...        ║
echo  ╚══════════════════════════════════════════╝
echo.
echo  Installing all required packages...
echo  (This may take 5-10 minutes on first run)
echo.

pip install -r requirements.txt --prefer-binary

echo.
echo  ─────────────────────────────────────────
echo  Verifying installation...
echo  ─────────────────────────────────────────
python -c "import cv2; print('  [OK] OpenCV')"
python -c "import numpy; print('  [OK] NumPy')"
python -c "import PIL; print('  [OK] Pillow')"
python -c "import insightface; print('  [OK] InsightFace')"
python -c "import mediapipe; print('  [OK] MediaPipe')"
python -c "import openpyxl; print('  [OK] OpenPyXL')"
python -c "import onnxruntime; print('  [OK] ONNX Runtime')"
echo.
echo  ─────────────────────────────────────────
echo  Installation complete!
echo  Double-click run.bat to start the app.
echo  ─────────────────────────────────────────
echo.
pause
