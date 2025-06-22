from datetime import datetime
import os

class DetectionStatus:
    def __init__(self):
        self.screenshots_dir = "screenshots"
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
    
    def get_status(self):
        return {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

detection_tracker = DetectionStatus()
