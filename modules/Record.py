# pip install pyaudio

import os
import wave
import pyaudio
#import RPi.GPIO as GPIO

class AudioRecorder:
    def __init__(self, output_dir, input_device_index=None, channels=1, rate=44100, chunk=4096):
        self.output_dir = output_dir
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self.audio = pyaudio.PyAudio()
        self.input_device_index=None
        for x in range(0, self.audio.get_device_count()):
            print(self.audio.get_device_info_by_index(x)['name'])
            if input_device_index in self.audio.get_device_info_by_index(x)['name']:
                self.input_device_index = self.audio.get_device_info_by_index(x)['index']
        print(f"INPUT_DEVICE_INDEX: {self.input_device_index}")
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

    # コールバック関数
    def callback(self, in_data, frame_count, time_info, status):
        # wavに保存する
        self.wav_file.writeframes(in_data)
        return None, pyaudio.paContinue

    def start_record(self, filename="recording.wav"):
        # Full path for the output file
        
        output_path = os.path.join(self.output_dir, filename)
        self.wav_file = wave.open(output_path, 'w')
        self.wav_file.setnchannels(self.channels)
        self.wav_file.setsampwidth(2)  # 16bits
        self.wav_file.setframerate(self.rate)
        
        print(f"INPUT DEVICE: {self.input_device_index}")
        # Initialize recording stream
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.rate,
            input=True,
            output=False,
            input_device_index=self.input_device_index,
            frames_per_buffer=self.chunk,
            stream_callback=self.callback
        )
        print("Recording...")

        return output_path

    # 録音停止
    def stop_record(self):

        print("Stop recording")
        # ストリームを止める
        self.stream.stop_stream()
        self.stream.close()

        # wavファイルを閉じる
        self.wav_file.close()

    def cleanup(self):
        print("cleanup")
        # Clean up audio resources
        self.audio.terminate()



if __name__ == "__main__":
    # テストコード
    try:
        # 録音ディレクトリを指定
        output_dir = "./RecWAV"  # 一時ディレクトリを使用
        INPUT_DEVICE_INDEX = "使用するマイクの名前"
        recorder = AudioRecorder(output_dir=output_dir, INPUT_DEVICE_INDEX)

        # 録音を開始
        filename = "test_recording.wav"
        output_path = recorder.start_record(filename=filename)

        # 録音を5秒間実行
        import time
        time.sleep(5)

        # 録音を停止
        recorder.stop_record()

        # ファイルが正常に作成されたか確認
        if os.path.exists(output_path):
            print(f"録音が成功しました: {output_path}")
        else:
            print(f"録音ファイルが作成されませんでした: {output_path}")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        # リソースを解放
        recorder.cleanup()
