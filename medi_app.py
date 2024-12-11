import streamlit as st # フロントエンドを扱うstreamlitをインポート
from openai import OpenAI # 音声認識した文字の要約で利用するOpenAIをインポート
import os # 環境変数にしたopenai apiキーを呼び出すための機能をインポート
import speech_recognition as sr # 音声認識の機能をインポート

# 音声認識の言語を引数に音声認識をする関数の設定
def mic_speech_to_text():
    with sr.Microphone() as source: # マイク入力を音声ファイルとして読み込み
        audio = sr.Recognizer().listen(source, timeout=2, phrase_time_limit=30) # sr.Recognizer().listen(マイク入力, 音声入力されるまでの最大待機時間(秒), 音声入力の最大長さ(秒))で認識準備
    try:
        text = sr.Recognizer().recognize_google(audio, language='ja') #  sr.Recognizer().recognize_google(音声データ,言語)で音声認識して、textに代入
    except:
        text = '音声認識に失敗しました' 
    return text # 認識した文字を返す

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
            {"role": "system", "content":'以下の文章300文字以内で要約して出力してください'},
            {"role": "user", "content": input_text}]
    )
    output_content = responce.choices[0].message.content.strip() # 返って来たレスポンスの内容はresponse.choices[0].message.content.strip()に格納されているので、これをoutput_contentに代入
    return output_content # 返って来たレスポンスの内容を返す

# streamlitでフロントエンド側を作成
st.title('ホカンサポ(仮)') # タイトルを表示
# サイドバーにアップローダーを設定。wavファイルだけ許可する設定にする
file_upload = st.sidebar.file_uploader("ここに音声認識したいファイルをアップロードしてください。", type=['wav'])

if (file_upload != None): # ファイルアップロードされた場合、file_uploadがNoneではなくなる
    st.write('音声認識結果:') # 案内表示：音声認識結果:
    result_text = file_speech_to_text(file_upload) # アップロードされたファイルと選択した言語を元に音声認識開始
    st.write(result_text) # メソッドから返ってきた値を表示
    st.audio(file_upload) # アップロードした音声をきける形で表示
    state_summary = st.empty() # 要約中を示すための箱を用意
    state_summary.write('要約中')
    summarized_text = summarize_text(result_text) # ChatGPTを使って要約の実行
    st.write('要約結果:') # 表示を変更
    state_summary.empty() # 要約内容を入れるための箱を用意
    st.write(summarized_text) # メソッドから帰ってきた値を表示

st.sidebar.write('マイクでの音声認識はこちらのボタンをクリック') # 案内をサイドバーに表示
if st.sidebar.button('音声認識開始'): # ボタンが押されたら実行される。ボタンはサイドバーに表示
    state = st.empty() # マイク録音中を示すための箱を準備
    state.write('音声認識中')
    result_text = mic_speech_to_text() # 音声認識開始
    state.write('音声認識結果:') # 案内表示に変更
    st.write(result_text) # メソッドから返ってきた値を表示
    state_summary = st.empty() # 要約中を示すための箱を用意
    state_summary.write('要約中')
    summarized_text = summarize_text(result_text) # ChatGPTを使って要約の実行
    st.write('要約結果:') # 表示を変更
    state_summary.empty() # 要約内容を入れるための箱を用意
    st.write(summarized_text) # メソッドから帰ってきた値を表示