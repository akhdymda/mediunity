import streamlit as st
import openai # 音声認識した文字の要約で利用するOpenAIをインポート
import os # 環境変数にしたopenai apiキーを呼び出すための機能をインポート
import speech_recognition as sr # 音声認識の機能をインポート
from audio_recorder_streamlit import audio_recorder # streamlit内でオーディオを録音するための機能をインポート
import datetime



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
api_key = st.secrets['opneai']['api_key']
openai.api_key = api_key # openAIの機能をclientに代入

# chatGPTにリクエストするための関数を設定。引数には書いてほしい内容と最大文字数を指定
def summarize_text(input_text, set_customer, content_maxStr_to_gpt):
    # 日付を文字列としてフォーマット
    today = datetime.datetime.now()  # 本日の日付を取得
    today_str = today.strftime("%Y-%m-%d")  # YYYY-MM-DD 形式の文字列に変換
    # client.chat.completions.createでchatGPTにリクエスト。オプションとしてmodelにAIモデル、messagesに内容を指定
    responce = openai.chat.completions.create(
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