from faster_whisper import WhisperModel, BatchedInferencePipeline
import time

class FasterWhisperSmall:
    def __init__(self, model_size="./modules/faster-whisper-small", device="cpu", compute_type="int8"):     
        # RaspberryPi5 でバランスが良い構成
        self.batch_size=3
        self.beam_size=1

        self.model_size=model_size
        self.device=device
        self.compute_type=compute_type
        
        self.model = WhisperModel(model_size, 
                            device=device, 
                            compute_type=compute_type)
        self.batched_model = BatchedInferencePipeline(model=self.model)        


    def transcribe(self,audio_file, context_data=None):
        start_time = time.perf_counter()

        # 音声ファイルを文字起こし
        segments, info = self.batched_model.transcribe(
            audio_file,
            language="ja",
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=700),
            batch_size=self.batch_size,
            beam_size=self.beam_size,
            without_timestamps=True,
            initial_prompt=context_data
            )

        # 結果の表示用にまとめる
        text_result = []
        for segment in segments:
            # segment.start, segment.end で時刻情報も取得可能
            text_result.append(segment.text)

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"実行時間: {elapsed_time:.6f} 秒")
        # 連結した文字起こし結果を返す
        return "".join(text_result)

if __name__ == "__main__":
    start_time = time.perf_counter()
    audio_file_path = "sampleTokyo.WAV"
    
    fws = FasterWhisperSmall(
        model_size="./modules/faster-whisper-small",   # "small", "medium", "medium.en" など
        device="cpu",          # CPUで動かす場合
        compute_type="int8"    # INT8精度で推論
    )

    # INT8モデルでの推論
    transcription = fws.transcribe(
        audio_file=audio_file_path,
    )
    
    print("文字起こし結果:")
    print(transcription)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"実行時間: {elapsed_time:.6f} 秒")