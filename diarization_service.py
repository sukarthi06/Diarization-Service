from generated import diarization_pb2
from generated import diarization_pb2_grpc

from pyannote.audio import Pipeline
from dotenv import load_dotenv

import io
import os
import torchaudio

load_dotenv()

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    token=os.environ["HF_TOKEN"]
)


class DiarizationService(
    diarization_pb2_grpc.DiarizationServiceServicer
):
    
    def ProcessAudio(self, request, context):

        try:

            print(
                f"Received {len(request.audio_data)} bytes",
                flush=True
            )

            audio_stream = io.BytesIO(request.audio_data)

            waveform, sample_rate = torchaudio.load(audio_stream)

            print(
                f"Loaded waveform shape={waveform.shape}, sample_rate={sample_rate}",
                flush=True
            )

            result = pipeline({
                "waveform": waveform,
                "sample_rate": sample_rate
            })

            print("Pipeline completed", flush=True)

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

            print(f"Returning {len(segments)} segments", flush=True)

            return diarization_pb2.DiarizationResponse(
                segments=segments
            )

        except Exception as ex:

            print(
                f"ProcessAudio failed: {type(ex).__name__}: {ex}",
                flush=True
            )

            raise