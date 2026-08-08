import grpc
import os

from dotenv import load_dotenv

from generated import diarization_pb2
from generated import diarization_pb2_grpc

load_dotenv()

AUDIO_FILE = "test.wav"
PORT = os.environ.get("PORT", "50051")
SERVER_ADDRESS = f"localhost:{PORT}"
MAX_MESSAGE_SIZE_MB = int(os.environ.get("MAX_MESSAGE_SIZE_MB", "50"))


def run():
    with open(AUDIO_FILE, "rb") as f:
        audio_data = f.read()

    options = [
        ('grpc.max_receive_message_length', MAX_MESSAGE_SIZE_MB * 1024 * 1024),
        ('grpc.max_send_message_length', MAX_MESSAGE_SIZE_MB * 1024 * 1024),
    ]

    with grpc.insecure_channel(SERVER_ADDRESS, options=options) as channel:
        stub = diarization_pb2_grpc.DiarizationServiceStub(channel)

        request = diarization_pb2.DiarizationRequest(audio_data=audio_data)

        response = stub.ProcessAudio(request)

        for segment in response.segments:
            print(
                f"{segment.speaker}: "
                f"{round(segment.start, 2)}s -> "
                f"{round(segment.end, 2)}s"
            )

        print()
        print("Total segments:", len(response.segments))


if __name__ == "__main__":
    run()
