from datetime import datetime
import time

def struct_time_to_datetime(struct_time_obj: time.struct_time) -> datetime:
    """Converts `time.struct_time` object to `datetime.datetime` object.

    Args:
        struct_time_obj (time.struct_time): struct_time object

    Returns:
        datetime.datetime: datetime object
    """
    return datetime.fromtimestamp(time.mktime(struct_time_obj))


class TimeCheckpoint(object):
    def __init__(self, fn='timecheckpoint.txt'):
        self.filename = fn
        self._checkpoint = None
    
    @property
    def checkpoint(self):
        if self._checkpoint is None:
            self.load()
        
        return self._checkpoint
    
    @checkpoint.setter
    def checkpoint(self, value):
        self._checkpoint = value
        self.save()

    def load(self):
        try: 
            with open(self.filename, 'r') as f:
                raw_iso = f.read()
                self._checkpoint = datetime.fromisoformat(raw_iso)
        except FileNotFoundError:
            self._checkpoint = datetime.fromtimestamp(time.mktime(time.gmtime(0)))  # Epoch time
            return True
    
    def save(self):
        with open(self.filename, 'w') as f:
            f.write(self._checkpoint.isoformat())
        
        return True

