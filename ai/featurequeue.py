import socketserver
import json
import queue
import time
from threading import Thread

import common
from feature import Feature

class TCPMessageHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self.data = self.rfile.readline().strip()
        self.feature = Feature.from_json(self.data)
        #print("{} wrote:".format(self.client_address[0]))
        #print(self.feature.to_json())
        FeatureQueue.put(self.feature)
        self.wfile.write(bytes("OK: " + self.feature.to_json(), "utf-8"))

class FeatureQueue():
    feature_queue = queue.PriorityQueue(maxsize=100)

    @staticmethod
    def start_server_sync():
        print("Binding address...")
        while True:
            try:
                server = socketserver.TCPServer((common.HOST, common.PORT), TCPMessageHandler)
                break
            except:
                time.sleep(1)
                continue
        print("Starting server")
        try:
            server.serve_forever()
        finally:
            print("Closing server")
            server.server_close()

    @staticmethod
    def start_server():
        thread = Thread(target=FeatureQueue.start_server_sync)
        thread.start()

    @classmethod
    def put(cls, feature):
        if cls.feature_queue.full():
            cls.feature_queue.queue.pop()
        cls.feature_queue.put((feature.type, feature), block=False)
        #print(str(cls.feature_queue.qsize()) + ": " + str(cls.feature_queue.queue[0][1].to_json()))

    @classmethod
    def get(cls):
        return cls.feature_queue.get(block=False)

if __name__ == "__main__":
    FeatureQueue.start_server()
    print("Server started")
