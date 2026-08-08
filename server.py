from concurrent import futures
import grpc
import os
import structlog

from dotenv import load_dotenv

from diarization_service import DiarizationService
from generated import diarization_pb2_grpc

load_dotenv()

log = structlog.get_logger()

PORT = os.environ.get("PORT", "50051")
MAX_MESSAGE_SIZE_MB = int(os.environ.get("MAX_MESSAGE_SIZE_MB", "50"))


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=4),
        options=[
            ('grpc.max_receive_message_length', MAX_MESSAGE_SIZE_MB * 1024 * 1024),
            ('grpc.max_send_message_length', MAX_MESSAGE_SIZE_MB * 1024 * 1024),
        ]
    )

    diarization_pb2_grpc.add_DiarizationServiceServicer_to_server(
        DiarizationService(),
        server
    )

    server.add_insecure_port(f"[::]:{PORT}")

    server.start()

    log.info("server_started", port=PORT)

    server.wait_for_termination()


if __name__ == "__main__":
    serve()