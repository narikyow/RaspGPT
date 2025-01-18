#pip install openai

import openai
# streamを用いてレスポンスをスムーズにする。
# また、デフォルトで入れる指示についても色々考慮する。
class ConnectGPT:
    def __init__(self, api_key,
                 VoiceReading,
                 max_tokens=1024,
                 model="gpt-4o-mini",
                 system=""
                ):
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.model = model
        self.system = system
        self.VoiceReading = VoiceReading
        openai.api_key = self.api_key

    def send_text(self, text=None, history=None):
        self.text=text
        
        try:
            # Send the text input to ChatGPT and get the response
            if history is not None or len(history)>0:
                messages = [
                    {"role": "system", "content":self.system},
                ]
                messages = messages + history + [{"role":"user", "content":self.text}] # chatの内容を追加する。
            
            else:
                messages=[
                    {"role": "system", "content":self.system},
                    {"role": "user", "content": self.text}
                ]
            
            # 送信したメッセージを確認
            print(f"INPUT:\n{messages}")

            response = openai.chat.completions.create(
                model=self.model,
                stream=True,
                n=1,
                messages=messages,
                max_tokens=self.max_tokens,
            )

            # Extract the response content
            fullResponse = ""
            RealTimeResponse = ""

            for chunk in response:
                text = chunk['choices'][0]['delta'].get('content')

                if(text==None):
                    pass
                else:
                    fullResponse += text
                    RealTimeResponse += text
                    print(text, end='', flush=True) # 部分的なレスポンスを随時表示していく

                    target_char = ["。", "！", "？", ".", ",", "!", "?", "**", ":", ";"]
                    for index, char in enumerate(RealTimeResponse):
                        if char in target_char:
                            pos = index + 2        # 区切り位置
                            sentence = RealTimeResponse[:pos]           # 1文の区切り
                            RealTimeResponse = RealTimeResponse[pos:]   # 残りの部分
                            # 1文完成ごとにテキストを読み上げる(遅延時間短縮のため)
                            self.VoiceReading.read_text(sentence)
                            break
                        else:
                            pass
            
            print(f"OUTPUT:\n{fullResponse}")
            # APIからの完全なレスポンスを返す
            return fullResponse
        
        except Exception as e:
            return f"Error: {e}"

if __name__=="__main__":
    # Usage example
    # Initialize with your OpenAI API key
    import VoReading
    VoiceReading = VoReading.OpenJTalkReader()
    api_key = "your_openai_api_key"  # Replace with your actual API key
    gpt_connector = ConnectGPT(
        api_key=api_key,
        VoiceReading=VoiceReading
        )

    # Send a text message and print the response
    text = "Hello, ChatGPT! This is Test."
    response = gpt_connector.send_text(text)
    print("ChatGPT response:", response)
