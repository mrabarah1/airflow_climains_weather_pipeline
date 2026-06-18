import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
desktop_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

if desktop_dir not in sys.path:
    sys.path.insert(0, desktop_dir)
    print(f"Added {desktop_dir} to sys.path")
    
from climains_weather_pipeline.pipeline import extract, transform, load, view_database_data #noqa: E402