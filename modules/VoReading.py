import subprocess
import os

class OpenJTalkReader:
    def __init__(self, 
                 speed=1.0, 
                 voice_path="MEI_HAP", 
                 dic_path=None, 
                 output_path="output.wav"):
        
        # Set default paths
        voice_paths = {
            "DEFAULT": "/usr/share/hts-voice/nitech-jp-atr503-m001/nitech_jp_atr503_m001.htsvoice",
            "MEI_ANG": "/usr/share/hts-voice/mei_angry.htsvoice",
            "MEI_BAS": "/usr/share/hts-voice/mei_angry.htsvoice",
            "MEI_HAP": "/usr/share/hts-voice/mei_angry.htsvoice",
            "MEI_NOR": "/usr/share/hts-voice/mei_angry.htsvoice",
            "MEI_SAD": "/usr/share/hts-voice/mei_angry.htsvoice",
        }
        self.voice_path = voice_paths[voice_path]
        self.dic_path = dic_path or "/var/lib/mecab/dic/open-jtalk/naist-jdic"
        self.speed = str(speed)
        self.output_path = output_path

    def read_text(self, text):
        # Ensure OpenJTalk is installed
        if not os.path.exists(self.voice_path):
            raise FileNotFoundError(f"Voice file not found: {self.voice_path}")
        if not os.path.exists(self.dic_path):
            raise FileNotFoundError(f"Dictionary path not found: {self.dic_path}")
        
        # Execute OpenJTalk
        cmd = [
            "open_jtalk",
            "-m", self.voice_path,
            "-x", self.dic_path,
            "-r", self.speed,
            "-ow", self.output_path
        ]
        try:
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            process.communicate(input=text.encode("utf-8"))
            process.wait()

            # Play the generated audio
            subprocess.run(["aplay", self.output_path])
        except Exception as e:
            print(f"Error during OpenJTalk execution: {e}")

if __name__ == "__main__":
    # Usage example
    reader = OpenJTalkReader()
    text = "こんにちは、PythonからOpenJTalkを使っています。"
    reader.read_text(text)
