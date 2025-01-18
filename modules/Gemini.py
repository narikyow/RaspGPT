import google.generativeai as genai

class ConnectGemini:
    def __init__(self,api_key,
                 VoiceReading,
                 max_tokens=1024,
                 model="gemini-1.5-flash",
                 system="一文は短く。",
                 ):
        
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.model = model
        self.system = system
        self.VoiceReading = VoiceReading

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=model,
            system_instruction=self.system
            )
        self.chat = self.model.start_chat()

    def send_text(self, text=None, history=[]):
        self.text = text
        try:
            # 送信したメッセージを確認
            print(f"INPUT:\n{self.text}")

            response = self.chat.send_message(
                content=self.text,
                generation_config = genai.GenerationConfig(
                    max_output_tokens=self.max_tokens
                ),
                stream=True
            )

            # Extract the response content
            fullResponse = ""
            pos=0
            RealTimeResponse = ""
            haveRead = ""

            for chunk in response:
                text = chunk.text
                text = self.remove_invalid_characters(text)

                if(text==None):
                    pass
                else:
                    fullResponse += text
                    RealTimeResponse += text
                    print(text, end='', flush=True) # 部分的なレスポンスを随時表示していく

                    target_char = ["。", "！", "？", "\n","、"]
                    for index, char in enumerate(RealTimeResponse):
                        if char in target_char:
                            pos = index + len(char)   # 区切り位置
                            sentence = RealTimeResponse[:pos]           # 1文の区切り
                            RealTimeResponse = RealTimeResponse[pos:]   # 残りの部分
                            # 1文完成ごとにテキストを読み上げる(遅延時間短縮のため)
                            haveRead += RealTimeResponse
                            if True in [RealTimeResponse==i for i in target_char]:
                                break
                            print(f"\nSENTENCE: {sentence}\nREST:{RealTimeResponse}")
                            self.VoiceReading.read_text(sentence)
                            break
                        else:
                            pass
            # 最後の文を読み上げないため、修正。
            if RealTimeResponse:
                print(f"\nFINAL_SENT: {RealTimeResponse}")
                if "\n" in RealTimeResponse:
                    st_join = "".join(RealTimeResponse.split("\n"))
                    if "。" in st_join:
                        st_split = st_join.split("。")
                        for i in st_split:
                            self.VoiceReading.read_text(i)
                else:
                    self.VoiceReading.read_text(RealTimeResponse)

                pos = fullResponse.rfind(haveRead)
                if pos==-1:
                    pass
                else:
                    before = fullResponse[:pos]
                    after = fullResponse[pos+len(haveRead):]
                    print(f"BEFORE: {before}\nAFTER: {after}")
                    self.VoiceReading.read_text(after)

            print(f"OUTPUT:\n{fullResponse}")
            # APIからの完全なレスポンスを返す
            return fullResponse
        
        except Exception as e:
            return f"Error: {e}"
    
    def remove_invalid_characters(self, input_string, encoding="utf-8"):
        """
        入力文字列から指定されたエンコーディングでエンコードできない文字を削除します。
        
        :param input_string: 処理対象の文字列
        :param encoding: エンコードに使用する文字エンコーディング（デフォルトは"utf-8"）
        :return: エンコーディングできない文字が削除された文字列
        """
        valid_chars = []
        for char in input_string:
            try:
                char.encode(encoding)
                valid_chars.append(char)
            except UnicodeEncodeError:
                pass  # 無効な文字はスキップ

        return ''.join(valid_chars)

# 使用例
if __name__ == "__main__":
    try:
        import VoReading
        VoiceReading = VoReading.OpenJTalkReader()
        # ConnectGemini クラスのインスタンスを生成
        gemini_connector = ConnectGemini(
            api_key="hogehoge_GEMINI",
            VoiceReading=VoiceReading
        )

        # 送信するテキスト
        text_to_send = "トランスフォーマーモデル内部の行列演算について説明して"

        # テキストを送信し、応答を取得
        response_data = gemini_connector.send_text(
            text=text_to_send
            )

        # 取得した応答を表示
        print("Geminiの応答:", response_data)
    except Exception as e:
        print("エラーが発生しました:", e)
