import streamlit as st # フロントエンドを扱うstreamlitをインポート
from openai import OpenAI # 音声認識した文字の要約で利用するOpenAIをインポート
import os # 環境変数にしたopenai apiキーを呼び出すための機能をインポート
import speech_recognition as sr # 音声認識の機能をインポート
from audio_recorder_streamlit import audio_recorder # streamlit内でオーディオを録音するための機能をインポート
import wave # WAV形式のオーディオファイルを動かすための機能をインポート
import time
import datetime 

# 利用者リストの作成
set_customer_list = {
    '利用者を選択してください':'00',
    '山田太郎': 'yt',
    '鈴木一郎': 'st',
    '田中次郎': 'tj',
    '佐藤栄作': 'se',
    '後藤新平': 'gs',
    '津田梅子': 'tu'
}

# 日付を文字列としてフォーマット
today = datetime.datetime.now()  # 本日の日付を取得
today_str = today.strftime("%Y-%m-%d")  # YYYY-MM-DD 形式の文字列に変換

# streamlitで音声を録音するための関数を設定
def recorder():
    contents = audio_recorder(
        energy_threshold = (1000000000,0.0000000002), 
        pause_threshold=0.1, 
        sample_rate = 48_000,
        text="Clickして録音開始　→　"
    )
    return contents

# 音声ファイルを読み込んで認識する関数の設定
def file_speech_to_text(audio_file):
    with sr.AudioFile(audio_file) as source:
        audio = sr.Recognizer().record(source) # sr.Recognizer().record(開いた音声ファイル)で認識準備
    try:
        text = sr.Recognizer().recognize_google(audio, language='ja')  #  sr.Recognizer().recognize_google(音声データ,言語)で音声認識して、textに代入
    except:
        text = '音声認識に失敗しました'  
    return text # 認識した文字を返す

# 音声認識した内容を要約する機能の設定
OpenAI.api_key = os.environ['OPENAI_API_KEY'] # 環境変数化したAPIキーの読み込み
client = OpenAI() # openAIの機能をclientに代入

# chatGPTにリクエストするための関数を設定。引数には書いてほしい内容と最大文字数を指定
def summarize_text(input_text):
    # client.chat.completions.createでchatGPTにリクエスト。オプションとしてmodelにAIモデル、messagesに内容を指定
    responce = client.chat.completions.create(
        model= 'gpt-4o-mini',
        messages=[
            {
                "role": "system",
                "content": '看護師が書く記録として使用しますので、以下の内容を中立的で客観的な文章で出力してください。'
                           'なお、利用者氏名、日付（YYYY-MM-DD）、以下の記録の内容の順に出力してください。'
                           '利用者氏名は' + set_customer + '様 、日付は' + today_str +
                           'です。また、' + content_maxStr_to_gpt + '文字以内で出力してください'
            },
            {"role": "user", "content": input_text}]
    )
    output_content = responce.choices[0].message.content.strip() # 返って来たレスポンスの内容はresponse.choices[0].message.content.strip()に格納されているので、これをoutput_contentに代入
    return output_content # 返って来たレスポンスの内容を返す


# streamlitでフロントエンド側を作成
st.title('ホカンサポ(仮)') # タイトルを表示
st.header('利用者選択')
set_customer = st.selectbox('記録を行う利用者を選択してください',set_customer_list.keys(), index=0, placeholder='利用者を選択') 
st.write('利用者名:', set_customer)

# サイドバーにアップローダーを設定。wavファイルだけ許可する設定にする
file_upload = st.sidebar.file_uploader("ここに音声認識したいファイルをアップロードしてください。", type=['wav'])

# chatGPTに出力させる文字数
content_maxStr_to_gpt = str(st.sidebar.slider('要約したい文字数を設定してください。', 100,1000,300))

state_summary = st.empty() # 要約を示すための箱を用意

if (file_upload != None): # ファイルアップロードされた場合、file_uploadがNoneではなくなる
    st.write('音声認識結果:') # 案内表示：音声認識結果:
    result_text = file_speech_to_text(file_upload) # アップロードされたファイルと選択した言語を元に音声認識開始
    st.write(result_text) # メソッドから返ってきた値を表示
    st.audio(file_upload) # アップロードした音声をきける形で表示
    with st.spinner('要約中'):
        time.sleep(5)
        summarized_text = summarize_text(result_text) # ChatGPTを使って要約の実行
    st.success('要約結果:') # 表示を変更
    state_summary.empty() # 要約内容を入れるための箱を用意
    st.write(summarized_text) # メソッドから帰ってきた値を表示

# wisperによる音声認識の表示
contents = recorder() # contentsにrecorderメソッドを代入
if contents == None: # contentsが空の場合の表示を設定
    st.info('①　アイコンボタンを押して回答録音　(アイコンが赤色で録音中)。  \n②　もう一度押して回答終了　(再度アイコンが黒色になれば完了)')
    st.error('録音完了後は10秒程度お待ちください。')
    st.stop()
else: # contentsが空でない場合＝音声が入力された場合の表示を設定
    wave_data = st.audio(contents)
    print(type(contents)) # bytesデータで表示

    with wave.open("audio.wav", "wb") as audio_file: # waveモジュールを使用してMP3形式の音声データをwav形式に変換するための処理。audio.wavという名前のwavファイルを作成し、その中にcontentsを書き込んでいる。
        audio_file.setnchannels(2)
        audio_file.setsampwidth(2)
        audio_file.setframerate(48000)
        audio_file.writeframes(contents)

        audio_file= open("./audio.wav", "rb")

    # wisperで音声データをテキストに変換。transcriptionに代入。wisperモデルはwhisper-1を使用
    transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file,
    )
    recognized_text = transcription.text
        
    st.write(recognized_text) # テキストを表示

    with st.spinner('要約中'):
        time.sleep(5)
        summarized_text = summarize_text(recognized_text) # ChatGPTを使って要約の実行
    st.success('要約結果') # 表示を変更 
    state_summary.empty()# 要約内容を入れるための箱を用意
    st.write(summarized_text) # メソッドから帰ってきた値を表示