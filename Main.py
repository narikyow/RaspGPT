from modules import DeepL, GPT, Record, SpreadSheet, VoReading, whisper_small_faster, whisper_medium_faster, Gemini
from gpiozero import LED, Button
import time
import os
import pickle
from datetime import datetime, timedelta
import random

def main():
    # 必要なapiキーの設定
    API_KEY_DEEPL = "hogehoge_DEEPL"
    API_KEY_GPT = None
    API_KEY_GEMINI = "hogehoge_GEMINI"
    GAS_URL = "hogehoge_GAS"

    INPUT_DEVICE_INDEX = 'SF-558: USB Audio (hw:2,0)'

    # 録音したwavファイルを保存するか否か。Trueなら、wavが上書きされず、累積していく。
    AUDIO_SAVE = True

    # 音声が格納されるディレクトリ
    OUTPUT_DIR = "RecWAV"

    # whisperのsmallか、mediumか
    WHISPER_MODEL = "small"

    # APIからの応答をinitial_inputとして入力する。
    # ChatGPTの場合は、ユーザからの入力しか履歴として保存していないので、処理は行わない。
    WHISPER_MODEL_CONTEXT = True

    # デフォルトのinitial_promptを設定
    # 応答から得たプロンプトも加えて渡す
    # 自分がよく聞く質問などを適宜設定
    WHISPER_MODEL_CONTEXT_DEFAULT = "文芸 哲学 医学（心理学） 社会 経済 機械学習 Transformer アテンション 差分進化アルゴリズム 進化計算 DE LSHADE 最適化"

    # 応答のうち何文をinitial_inputとするか。
    # ランダムに選択。
    WHISPER_MODEL_CONTEXT_NUM = 3

    # initial_inputから取り除く文字を指定
    WHISPER_MODEL_CONTEXT_REP = ['\n', '*', ' ', '　', '_']

    # どちらのAPIを使用するのか
    CHAT_API = "Gemini"

    #============================
    # チャットAPIに渡す設定（GPT, Gemini共通がほとんど。別々設定のものは名称を設定してある）
    #============================
    # ユーザからの過去の質問履歴
    CHAT_DATA = []
    
    # CHAT_DATAの要素数（参照する履歴の数）を指定
    CHAT_SIZE = 10

    # APIの応答の最大トークン数
    MAX_TOKEN = 150

    # ChatGPTの使用モデル
    GPT_MODEL = "gpt-4o-mini"

    # ChatGPTに送るシステムへの指示
    GPT_SYSTEM = "短く文を区切りながら応答"
    
    # Geminiの使用モデル
    # 使用モデルに応じて応答の最大トークン数を変更したい。
    # また、使用回数制限ギリギリまでProを自動で選択するようにする。
    pklName = "GeminiProLimit.pickle"
    GeminiProLimit = manage_pickle(pklName)
    print(GeminiProLimit)
    key = list(GeminiProLimit)[0]


    # Geminiの各モデルの最大トークン数を決める
    # Proの制限がいっぱいになると、この辞書に格納してある末尾のモデルに切り替わる
    GEMINI_MODEL_DIC = {
        "gemini-1.5-flash": MAX_TOKEN, 
        "gemini-1.5-pro": 2000,
        "gemini-2.0-flash-exp": MAX_TOKEN,
    }
    if CHAT_API=="Gemini":
        if GeminiProLimit[key] >= 50:# proのRPD
            GEMINI_MODEL = list(GEMINI_MODEL_DIC)[-1] # Proが使えない場合、辞書の末尾のモデルを指定
        else:
            GEMINI_MODEL = "gemini-1.5-pro"
            
        MAX_TOKEN = GEMINI_MODEL_DIC[GEMINI_MODEL] # 選択したモデルのmax_tokensを自動指定
    
    # Geminiに送るシステムへの指示
    GEMINI_SYSTEM = """
        文は短く区切る。話を広げつつ簡潔に答える。
        使って良い記号は、。のみ。
        回答は日本語。
        入力は、音声をwhisper-smallで文字起こししたものです。
        そのため、誤字や誤変換が多く見られます。
        日本語入力は文章をひらがなに置き換え、意味が通る適切な単語を推測、正しく置き換え、理解し回答してください。
        回答は話すような口調。
        英語入力ならそのまま文意を読み取って回答。
        英語表記（geminiやintel）などはカタカナ（ジェミニ、インテル）に直して
        """

    #=============================
    # OpenJTalkの設定
    #=============================

    # 話すスピード
    SPEED = 1.3

    # 声の種類
    VOICE_TYPE = "MEI_HAP"

    # 辞書のパス
    DIC_PATH = None


    #=============================
    # 初期化処理
    #=============================

    GPIO_PIN_SWITCH_1 = Button(17, pull_up=True) # LED RED
    # ja_to_en >> GPT >> ja

    GPIO_PIN_SWITCH_2 = Button(27, pull_up=True) # LED YELLOW
    # ja >> GPT >> ja
    
    GPIO_PIN_SWITCH_3 = Button(22, pull_up=True) # LED GREEN 



    GPIO_LED_RED = LED(5)
    GPIO_LED_YELLOW = LED(6)
    GPIO_LED_GREEN = LED(16)

    GPIO_LED_RED.on()
    GPIO_LED_YELLOW.on()
    GPIO_LED_GREEN.on()




    # オブジェクト諸々の定義
    DeepLTranslator = DeepL.DeepLTranslator(API_KEY_DEEPL)

    # Translator = TranslationHF()　# HFの翻訳モデルを呼び出すはずだったが断念
    
    AudioRecorder = Record.AudioRecorder(output_dir=OUTPUT_DIR, input_device_index=INPUT_DEVICE_INDEX)
    
    SaveSpreadSheet = SpreadSheet.SaveSpreadSheet(GAS_URL)
    
    if WHISPER_MODEL=="small":
        WavToText = whisper_small_faster.FasterWhisperSmall(
            model_size="./modules/faster-whisper-small",    
            device="cpu",                                   # CPUで動かす場合
            compute_type="int8"                             # INT8精度で推論
        )
    elif WHISPER_MODEL=="medium":
        WavToText = whisper_medium_faster.FasterWhisperMedium(
            model_size="./modules/faster-whisper-medium",   
            device="cpu",                                   # CPUで動かす場合
            compute_type="int8"                             # INT8精度で推論
        )
    else:
        print("ERROR: SET 'WHISPER_MODEL' ")
        exit()

    
    VoiceReading = VoReading.OpenJTalkReader(
        speed=SPEED, 
        voice_path=VOICE_TYPE, 
        dic_path=DIC_PATH, 
    )

    if CHAT_API=="GPT":
        ConnectChatAPI = GPT.ConnectGPT(
            api_key=API_KEY_GPT,        # OpenAI APIから取得したAPIキー
            VoiceReading=VoiceReading,  # 音声読み上げインスタンスを渡す
            max_tokens=MAX_TOKEN,       # GPT側の設定。最大トークン数
            model=GPT_MODEL,            # 指定するGPTのモデル
            system=GPT_SYSTEM           # システムに渡す最初の指示
            )
        
    elif CHAT_API=="Gemini":
        ConnectChatAPI = Gemini.ConnectGemini(
            api_key=API_KEY_GEMINI,     # Gemini APIから取得したAPIキー
            VoiceReading=VoiceReading,  # 音声読み上げインスタンスを渡す
            max_tokens=MAX_TOKEN,       # GPT側の設定。最大トークン数
            model=GEMINI_MODEL,         # 指定するGeminiのモデル
            system=GEMINI_SYSTEM        # システムに渡す最初の指示
            )
    else:
        print("ERROR: SET 'CHAT_API'")
        exit()

    #==========================
    # 主に使う関数の定義
    #==========================

    def JE_API_EJ_SP_SWITCH1(CHAT_DATA,GeminiProLimit):
        # 日本語>>deepLで英語翻訳>>ChatAPI>>日本語
        # 日本語で答えるようプロンプトを加える



        # 録音処理
        AudioFileName=AudioFileNameSelect(AUDIO_SAVE)
        OutputPath=AudioRecorder.start_record(filename=AudioFileName)
        GPIO_LED_RED.on()
        
        while True:
            time.sleep(0.3)
            if GPIO_PIN_SWITCH_1.is_pressed==True:# 再度スイッチを押して入力完了
                AudioRecorder.stop_record()
                break
            elif GPIO_PIN_SWITCH_3.is_pressed==True or GPIO_PIN_SWITCH_2.is_pressed==True:# スイッチ3への入力なら録音を途中終了。GPTに送信しない。
                GPIO_LED_RED.off()
                GPIO_LED_GREEN.on()
                AudioRecorder.stop_record()
                time.sleep(0.2)
                GPIO_LED_GREEN.blink()
                return CHAT_DATA
        GPIO_LED_RED.off()

        # whisperモデルで文字起こし
        GPIO_LED_RED.blink(on_time=0.3, off_time=0.3)

        context=None
        if WHISPER_MODEL_CONTEXT:
            if len(CHAT_DATA)>0:
                chat_data_split = CHAT_DATA[-1]["content"].split("。")
                length = len(chat_data_split)
                context = random.sample(chat_data_split, min(length, WHISPER_MODEL_CONTEXT_NUM))
                context="。".join(context)
                for i in WHISPER_MODEL_CONTEXT_REP:
                    context = context.replace(i, '')
                context = WHISPER_MODEL_CONTEXT_DEFAULT + " " + context

            else:
                context = WHISPER_MODEL_CONTEXT_DEFAULT
            print(f"CONTEXT: {context}")
        
        Text = WavToText.transcribe(OutputPath, context)
        
        GPIO_LED_RED.on()
        
        # 文章が空でないことを確認
        if not Text or  Text.strip()=="":
            e = "ERROR:Text is empty"
            print(e)
            return CHAT_DATA
        

        # DeepLで英語に翻訳
        GPIO_LED_YELLOW.blink(on_time=0.3, off_time=0.3)
        Text += ". 日本語で回答"
        TranslatedText = DeepLTranslator.translate_japanese_to_english(Text)
        GPIO_LED_YELLOW.on()

        # ChatGPTに送信
        GPIO_LED_GREEN.blink(on_time=0.4, off_time=0.4)
        FullResponse = ConnectChatAPI.send_text(TranslatedText, CHAT_DATA)
        
        GPIO_LED_GREEN.blink(on_time=0.1, off_time=0.1)
        # スプレッドシートに記録しメールを送る
        send_data = {
            "Input": Text,
            "TranslatedInput": TranslatedText,
            "Response": FullResponse,
        }
        res = SaveSpreadSheet.save_data(send_data)
        print(res) # スプレッドシートとの通信結果
        GPIO_LED_GREEN.on()


        # チャット履歴の更新
        if CHAT_API=="GPT":
            CHAT_DATA = manage_list(CHAT_DATA, [{
                "role":"user", "content":TranslatedText
                }])
        elif CHAT_API=="Gemini":
            CHAT_DATA = manage_list(CHAT_DATA, [
                {"role":"user", "content":TranslatedText,},
                {"role":"model", "content":FullResponse}
                ])
        print(f"CHAT: {CHAT_DATA}")

        if CHAT_API=="Gemini" and GEMINI_MODEL=="gemini-1.5-pro":
            GeminiProLimit[key] += 1
            # 新しい辞書をピクルとして保存
            with open(pklName, "wb") as f:
                pickle.dump(GeminiProLimit, f)

        # 処理の完了
        time.sleep(0.2)
        GPIO_LED_RED.off()
        GPIO_LED_YELLOW.off()
        GPIO_LED_GREEN.blink()


        return CHAT_DATA

    def JP_API_JP_SP_SWITCH2(CHAT_DATA,GeminiProLimit):
        # 日本語>>GPT>>出力

        # 録音処理
        AudioFileName=AudioFileNameSelect(AUDIO_SAVE)
        OutputPath=AudioRecorder.start_record(filename=AudioFileName)
        GPIO_LED_YELLOW.on()
        while True:
            time.sleep(0.3)
            if GPIO_PIN_SWITCH_2.is_pressed==True:# 再度スイッチを押して入力完了
                AudioRecorder.stop_record()
                break
            elif GPIO_PIN_SWITCH_1.is_pressed==True or GPIO_PIN_SWITCH_3.is_pressed==True:# スイッチ3への入力なら録音を途中終了。GPTに送信しない。
                GPIO_LED_GREEN.off()
                GPIO_LED_GREEN.on()
                AudioRecorder.stop_record()
                time.sleep(0.2)
                GPIO_LED_GREEN.blink()
                return CHAT_DATA
        #AudioRecorder.cleanup()
        GPIO_LED_YELLOW.off()

        # 文字起こし
        GPIO_LED_RED.blink(on_time=0.5, off_time=0.5)

        context=None
        if WHISPER_MODEL_CONTEXT:
            if len(CHAT_DATA)>0:
                chat_data_split = CHAT_DATA[-1]["content"].split("。")
                length = len(chat_data_split)
                context = random.sample(chat_data_split, min(length, WHISPER_MODEL_CONTEXT_NUM))
                context="。".join(context)
                for i in WHISPER_MODEL_CONTEXT_REP:
                    context = context.replace(i, '')
                context = WHISPER_MODEL_CONTEXT_DEFAULT + " " + context

            else:
                context = WHISPER_MODEL_CONTEXT_DEFAULT
            print(f"CONTEXT: {context}")

        Text = WavToText.transcribe(OutputPath, context)

        if not Text or  Text.strip()=="":
            e = "ERROR:Text is empty"
            print(e)
            return CHAT_DATA
        
        
        GPIO_LED_RED.on()

        GPIO_LED_YELLOW.on()

        GPIO_LED_GREEN.blink(on_time=0.4, off_time=0.4)
        FullResponse = ConnectChatAPI.send_text(Text)
        

        # スプレッドシート用にTranslatedTextに"SWITCH3"と記述
        # スプレッドシートに記録、メール送信
        TranslatedText = "None"

        GPIO_LED_GREEN.blink(on_time=0.1, off_time=0.1)
        send_data = {
            "Input": Text,
            "TranslatedInput": TranslatedText,
            "Response": FullResponse,
        }
        res = SaveSpreadSheet.save_data(send_data)
        print(res) # スプレッドシートとの通信結果
        
        GPIO_LED_GREEN.on()


        if CHAT_API=="GPT":
            CHAT_DATA = manage_list(CHAT_DATA, [{
                "role":"user", "content":Text
                }])
        elif CHAT_API=="Gemini":
            CHAT_DATA = manage_list(CHAT_DATA, [
                {"role":"user", "content":Text,},
                {"role":"model", "content":FullResponse}
                ])
        print(f"CHAT: {CHAT_DATA}")

        if CHAT_API=="Gemini" and GEMINI_MODEL=="gemini-1.5-pro":
            GeminiProLimit[key] += 1
            # 新しい辞書をピクルとして保存
            with open(pklName, "wb") as f:
                pickle.dump(GeminiProLimit, f)


        # 処理の完了
        time.sleep(0.2)
        GPIO_LED_YELLOW.off()
        GPIO_LED_RED.off()

        GPIO_LED_GREEN.blink()
        

        return CHAT_DATA

        
    def manage_list(lst, new_element, max_size=CHAT_SIZE, ):
        # リストの長さが最大サイズを超えた場合、最初の要素を削除
        if CHAT_API=="GPT":
            if len(lst) >= max_size:
                lst.pop(0)
        elif CHAT_API=="Gemini":
            if len(lst) >= 2*max_size:
                lst.pop(0)
                lst.pop(0)
                
        # 新しい要素をリストの末尾に追加
        lst = lst+new_element
        print(f"NEWGEN_List: {lst}")
        return lst

    def AudioFileNameSelect(mode=AUDIO_SAVE):
        if mode:
            # 日時でファイルを保存するのも。
            now = datetime.now()
            filename = now.strftime('%Y%m%d_%H%M%S') + '.wav'
            return filename
        else:
            return "recording.wav"

    # 初期処理の完了を知らせる
    print("ALL SETTING IS OK.")
    GPIO_LED_YELLOW.off()
    GPIO_LED_GREEN.off()
    GPIO_LED_RED.off()

    # 待機状態であることを知らせる
    GPIO_LED_GREEN.blink()

    #==========================
    # ユーザから入力待ち
    #==========================

    try:
        while True:
                if GPIO_PIN_SWITCH_1.is_pressed==True:
                    GPIO_LED_RED.off()
                    GPIO_LED_YELLOW.off()
                    GPIO_LED_GREEN.off()
                    CHAT_DATA=JE_API_EJ_SP_SWITCH1(CHAT_DATA, GeminiProLimit)
                    print(GeminiProLimit)
                    if GeminiProLimit[key] >= 50: # Proの制限。初期化する。
                        GPIO_LED_RED.blink()
                        GPIO_LED_YELLOW.blink()
                        GPIO_LED_GREEN.blink()
                        time.sleep(1)
                        break

                elif GPIO_PIN_SWITCH_2.is_pressed==True:
                    GPIO_LED_RED.off()
                    GPIO_LED_YELLOW.off()
                    GPIO_LED_GREEN.off()
                    CHAT_DATA=JP_API_JP_SP_SWITCH2(CHAT_DATA, GeminiProLimit)
                    print(GeminiProLimit)
                    if GeminiProLimit[key] >= 50: # Proの制限。初期化する。
                        GPIO_LED_RED.blink()
                        GPIO_LED_YELLOW.blink()
                        GPIO_LED_GREEN.blink()
                        time.sleep(1)
                        break

                
                elif GPIO_PIN_SWITCH_3.is_pressed==True:
                    # やりとりの内容をリセットする。
                    GPIO_LED_RED.on()
                    GPIO_LED_YELLOW.on()
                    GPIO_LED_GREEN.on()
                    time.sleep(0.3)
                    GPIO_LED_RED.off()
                    GPIO_LED_YELLOW.off()
                    GPIO_LED_GREEN.off()
                    break

                time.sleep(0.3)
    finally:
        AudioRecorder.cleanup()



# Gemini Pro の制限について更新処理を行うための関数。
def manage_pickle(filename):
    # 現在時刻を取得
    now = datetime.now()  # 例: 2025-01-16 13:23:45

    # hour をチェックして、16時より大きいかどうかで分岐
    if now.hour > 16:
        # 同日の16時に固定
        target_time = now.replace(hour=16, minute=0, second=0, microsecond=0)
    else:
        # 前日の16時に固定 (timedelta(days=1) 引いて 16時にする)
        # replace() する順番に注意し、いったん今日の16時に合わせてから1日戻す
        today_16 = now.replace(hour=16, minute=0, second=0, microsecond=0)
        target_time = today_16 - timedelta(days=1)

    # キーとして使う文字列 (例: "2025-01-15-16") を生成
    target_key = target_time.strftime("%Y-%m-%d-%H")

    # ピクルファイルから既存のデータを読み込み
    loaded_data = None
    if os.path.exists(filename):
        try:
            with open(filename, "rb") as f:
                loaded_data = pickle.load(f)
        except Exception as e:
            print(f"ピクルの読み込み中にエラーが発生しました: {e}")
            loaded_data = None

    if loaded_data is not None:
        # 辞書のキーを1つだけ持つと仮定し、そのキーを取得
        # （複数キーの場合は要件に応じた処理に修正する）
        current_key = list(loaded_data.keys())[0]

        # 現在のキーと target_key を比較する
        # 年月日時を文字列として比較する場合、単純な文字列比較だと
        # "2025-1-9" < "2025-01-10" のようなケースでずれる可能性があるので、
        # ここでは日付型にして比較するなど工夫する。
        try:
            # "YYYY-MM-DD-HH" を datetime に変換
            year_c, month_c, day_c, hour_c = current_key.split("-")
            dt_c = datetime(int(year_c), int(month_c), int(day_c), int(hour_c))

            year_t, month_t, day_t, hour_t = target_key.split("-")
            dt_t = datetime(int(year_t), int(month_t), int(day_t), int(hour_t))

            if dt_c < dt_t:
                # 既存キーの日時が target_key の日時より古いなら更新
                data = {target_key: 0}
                with open(filename, "wb") as f:
                    pickle.dump(data, f)
                return data
            else:
                # 既存キーの方が新しいか、同じであればそのまま返す
                return loaded_data
        except ValueError as e:
            # 変換エラー等があれば、新しいデータを作り直す
            print(f"キーの解析でエラーが発生しました: {e}")
            data = {target_key: 0}
            with open(filename, "wb") as f:
                pickle.dump(data, f)
            return data

    else:
        # ファイルがない or 読み込み失敗時は新しい辞書を作成して保存
        data = {target_key: 0}
        with open(filename, "wb") as f:
            pickle.dump(data, f)
        return data




if __name__=="__main__":
    while True:
        main()
