import os
import uuid
from multiprocessing import Process, Event, Queue, Value
from queue import Empty
from time import sleep
from sys import exit as sys_exit
import os

class UploadAdmin:
    """
    Accepts a file stream (upload) and writes to a local file line-wise.\n
    Creates seperate processes for reading and writing.\n
    Exposes methods to pause, resume and terminate.\n
    """
    def __init__(self, base_path, read_stream, filename):
        self.read_stream = read_stream
        self.filepath = os.path.join(base_path, filename)
        self.read_stream_position = Value('i', 0)
        self.queue = Queue()
        self.paused = Event()
        self.closed = Event()

    def _read_stream(self, read_stream, queue, position, pause_event, close_event):
        read_stream.seek(position.value)
        # read until the read event is set, keeps stream open while exiting
        while(True):
            if(close_event.is_set()):
                sys_exit()
            line = self.read_stream.readline()
            queue.put(line)
            position.value = read_stream.tell()
            if(not line):
                # EOF found
                sys_exit()
            sleep(1)

    def _write_stream(self, filepath, queue, pause_event, close_event):
        file = open(filepath, 'ab')
        while(True):
            # Listens for close signal
            if(close_event.is_set()):
                file.close()
                sys_exit()
            # Listens for pause signal
            if(not pause_event.is_set()):
                line = queue.get()
                file.write(line)
                if(not line):
                    # EOF found
                    file.close()
                    sys_exit()
            sleep(1)

    def start(self):
        read_process = Process(name='read_process', target=self._read_stream, args=[self.read_stream, self.queue, self.read_stream_position, self.paused, self.closed])
        read_process.start()
        write_process = Process(name='write_process', target=self._write_stream, args=[self.filepath, self.queue, self.paused, self.closed])
        write_process.start()

    def pause(self):
        self.paused.set()
    
    def resume(self):
        self.paused.clear()

    def stop(self):
        self.paused.set()
        self.closed.set()

    def terminate(self):
        self.stop()
        os.remove(self.filepath)

    def status(self):
        if(self.closed):
            return "closed"
        elif(self.paused):
            return "paused"
        else:
            return "ongoing"