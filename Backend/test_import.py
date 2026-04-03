import sys
try:
    import fastapi
    print(f"FastAPI version: {fastapi.__version__}")
    print("FastAPI imported successfully.")
except ImportError as e:
    print(f"ImportError: {e}")
    print(f"Python path: {sys.path}")
except Exception as e:
    print(f"An error occurred: {e}")
