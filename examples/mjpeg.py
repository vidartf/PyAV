import argparse

import av.video
import cv2

parser = argparse.ArgumentParser()
parser.add_argument('out')
parser.add_argument('frames', nargs='+')
args = parser.parse_args()

container = av.open(args.out, 'w')
stream = container.add_stream('mjpeg')
buffers = []

for i, path in enumerate(args.frames):


    if not i:
        img = cv2.imread(path)
        stream.height = img.shape[0]
        stream.width = img.shape[1]
        stream.pix_fmt = 'yuvj422p'

    packet = av.packet.Packet()
    buffers.append(packet._set_payload(open(path).read()))

    container.mux(packet)



