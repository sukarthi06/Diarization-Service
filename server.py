from concurrent import futures
import grpc

from diarization_service import DiarizationService
from generated import diarization_pb2_grpc


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=4),
        options=[
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),
            ('grpc.max_send_message_length', 50 * 1024 * 1024),
        ]
    )

    diarization_pb2_grpc.add_DiarizationServiceServicer_to_server(
        DiarizationService(),
        server
    )

    server.add_insecure_port("[::]:50051")

    server.start()

    print("gRPC server started on port 50051")

    server.wait_for_termination()


if __name__ == "__main__":
    serve()