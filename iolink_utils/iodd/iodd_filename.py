from typing import Optional
from datetime import date, datetime
import re


class IoddFilename:
    # <vendor name>-<device name>-<release date>-IODD<schema version>.xml
    def __init__(self, filename: Optional[str]):
        self.value = filename
        self.date: Optional[date] = None

        if filename is not None:
            match = re.search(r"-(\d{8})-IODD\d+(?:\.\d+)*\.xml", filename)
            if match:
                self.date = datetime.strptime(match.group(1), "%Y%m%d").date()
