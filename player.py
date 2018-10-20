import socket
import threading
from collections import deque
import subprocess

"""
This is the configuration for now. There will be a separate configuration file
at some point, but it's not the time yet. Please feel free to open a PR if
you feel unsatisfied.
"""

host = "localhost"
port = 9999

"""
End of configuration
"""


def main():
    player = MusicThread()
    conn = socket.create_connection((host, port))

    buffer = ""
    messages = deque()

    while True:
        print("Listening...")
        data = conn.recv(1024)
        if not data:
            # Connection lost
            print("Connection lost")
            break

        buffer += data.decode("utf-8")
        while "\n" in buffer:
            index = buffer.find("\n")
            messages.append(buffer[0:index])
            buffer = buffer[index+1:]

        while len(messages) > 0:
            url = messages.popleft()
            print("Queueing {}".format(url))
            if not player.running:
                print("Starting player thread...")
                player = MusicThread()
                player.add(url)
                player.start()
            else:
                player.add(url)


class MusicThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.queue = deque()
        self.running = False

    def start(self):
        self.running = True
        super().start()

    def run(self):
        while len(self.queue) > 0:
            url = self.queue.popleft()
            print("Now playing {}".format(url))

            downloader = subprocess.Popen(("youtube-dl", "--no-playlist",
                                           "-o", "-", url),
                                          stdout=subprocess.PIPE)
            player = subprocess.Popen(("mpv", "--no-video", "-"),
                                      stdin=downloader.stdout)

            downloader.wait()
            player.wait()

        self.running = False

    def add(self, url):
        self.queue.append(url)


if __name__ == "__main__":
    main()
