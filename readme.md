face_system/
│
├── main.py                            # Entry point (for testing / running workflows)
│
├── config/
│   ├── settings.yaml                  # Configuration file (paths, thresholds, etc.)
│   └── __init__.py
│
├── data/
│   ├── input_images/                  # Raw uploaded images for enrollment
│   ├── cropped_faces/                 # Cropped faces after detection
│   ├── embeddings/                    # Saved face embeddings (serialized)
│   ├── database/                      # Database files (SQLite, etc.)
│   └── logs/                          # System logs
│
├── modules/
│   ├── __init__.py
│   │
│   ├── detection/
│   │   ├── __init__.py
│   │   ├── face_detection_base.py     # Common detection interface class
│   │   ├── face_detection_image.py    # For user image input
│   │   ├── face_detection_live.py     # For live camera feed
│   │   └── detectors/                 # Optional: model-specific detectors
│   │       ├── mtcnn_detector.py      # MTCNN-based detection
│   │       ├── mediapipe_detector.py  # MediaPipe-based detection
│   │       ├── opencv_dnn_detector.py # OpenCV DNN detector
│   │       └── __init__.py
│   │
│   ├── recognition/
│   │   ├── __init__.py
│   │   ├── embedding_generator.py     # Converts faces → embeddings
│   │   ├── face_matcher.py            # Compares embeddings (cosine/distance)
│   │   ├── database_handler.py        # Stores / retrieves embeddings + metadata
│   │   └── preprocessing.py           # Normalization, alignment, lighting correction
│   │
│   └── workflows/
│       ├── __init__.py
│       ├── enrollment_workflow.py     # Handles registration of known persons
│       ├── surveillance_workflow.py   # Handles real-time recognition
│       └── utils.py                   # Shared workflow utilities
│
├── utils/
│   ├── logger.py                      # Logging setup
│   ├── file_utils.py                  # File handling (saving faces, etc.)
│   ├── visualization.py               # Optional: bounding boxes / debug visualization
│   └── __init__.py
│
├── requirements.txt                   # All dependencies (facenet-pytorch, mediapipe, etc.)
├── README.md                          # Documentation for setup and usage
└── tests/
    ├── test_detection.py              # Unit tests for face detection
    ├── test_recognition.py            # Unit tests for embedding + matching
    ├── test_workflows.py              # End-to-end tests
    └── __init__.py
