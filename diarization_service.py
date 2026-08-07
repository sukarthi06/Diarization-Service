from generated import diarization_pb2
from generated import diarization_pb2_grpc

from pyannote.audio import Pipeline
from dotenv import load_dotenv

import io
import os
import structlog
import torchaudio

load_dotenv()

log = structlog.get_logger()

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    token=os.environ["HF_TOKEN"]
)


class DiarizationService(
    diarization_pb2_grpc.DiarizationServiceServicer
):

    def ProcessAudio(self, request, context):

        try:

            log.info("audio_received", bytes=len(request.audio_data))

            audio_stream = io.BytesIO(request.audio_data)

            waveform, sample_rate = torchaudio.load(audio_stream)

            log.info(
                "waveform_loaded",
                shape=list(waveform.shape),
                sample_rate=sample_rate
            )

            result = pipeline({
                "waveform": waveform,
                "sample_rate": sample_rate
            })

            log.info("pipeline_completed")

            segments = []

            for turn, _, speaker in result.speaker_diarization.itertracks(
                yield_label=True
            ):
                segments.append(
                    diarization_pb2.SpeakerSegment(
                        speaker=speaker,
                        start=turn.start,
                        end=turn.end
                    )
                )

            log.info("segments_returned", count=len(segments))

            return diarization_pb2.DiarizationResponse(
                segments=segments
            )

        except Exception as ex:

            log.error(
                "process_audio_failed",
                error_type=type(ex).__name__,
                error=str(ex)
            )

            raise