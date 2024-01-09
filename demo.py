from __future__ import division
from infer import format_text
import asyncio
import websockets
import json
import pyaudio


def process_transcript(message: str):
    """Receive and post process transcription.
    Args:
        message: json string received from server

    """
    message = json.loads(message)
    results = message['results']
    is_final = results[0]['final']
    transcript = results[0]['alternatives'][0]['transcript']
    if is_final:
        transcript = format_text(transcript)
        print(transcript)


async def microphone_client():
    """
    Stream audio from client voice using websocket
    """
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = int(RATE / 10)

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
    async with websockets.connect(
            'ws://103.252.02.162:3200/wav2vec/ws') as websocket:
        while True:
            data = stream.read(CHUNK)
            await websocket.send(data)
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                process_transcript(message)
            except asyncio.TimeoutError:
                pass


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(microphone_client())
