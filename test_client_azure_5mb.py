import grpc
import os
import time

from dotenv import load_dotenv

from generated import diarization_pb2
from generated import diarization_pb2_grpc

load_dotenv()

AUDIO_FILE = "test_5mb.wav"
SERVER_ADDRESS = os.environ["AZURE_SERVER_ADDRESS"]
API_KEY = os.environ["API_KEY"]
MAX_MESSAGE_SIZE_MB = int(os.environ.get("MAX_MESSAGE_SIZE_MB", "50"))


def run():
    with open(AUDIO_FILE, "rb") as f:
        audio_data = f.read()

    options = [
        ('grpc.max_receive_message_length', MAX_MESSAGE_SIZE_MB * 1024 * 1024),
        ('grpc.max_send_message_length', MAX_MESSAGE_SIZE_MB * 1024 * 1024),
    ]

    credentials = grpc.ssl_channel_credentials()

    with grpc.secure_channel(SERVER_ADDRESS, credentials, options=options) as channel:
        stub = diarization_pb2_grpc.DiarizationServiceStub(channel)

        request = diarization_pb2.DiarizationRequest(audio_data=audio_data)

        start = time.time()

        response = stub.ProcessAudio(
            request,
            metadata=[("x-api-key", API_KEY)]
        )

        elapsed = time.time() - start

        for segment in response.segments:
            print(
                f"{segment.speaker}: "
                f"{round(segment.start, 2)}s -> "
                f"{round(segment.end, 2)}s"
            )

        print()
        print("Total segments:", len(response.segments))
        print(f"Elapsed: {elapsed:.2f} seconds")


if __name__ == "__main__":
    run()
