import streamlit as st # フロントエンドを扱うstreamlitをインポート
from openai import OpenAI # 音声認識で利用するOpenAIをインポート
import os # 環境変数にしたopenai apiキーを呼び出すための機能をインポート
import wave # WAV形式のオーディオファイルを動かすための機能をインポート
import time
from msword_save import save_summary_to_word
from customer_list import SET_CUSTOMER_LIST
from record_utils import recorder, file_speech_to_text, summarize_text

# whisper利用のためのコード
OpenAI.api_key = os.environ['OPENAI_API_KEY'] # 環境変数化したAPIキーの読み込み
client = OpenAI() # openAIの機能をclientに代入

# streamlitでフロントエンド側を作成
st.title('ホカンサポ／訪問記録作成用') # タイトルを表示
st.header('利用者選択')
set_customer = st.selectbox('記録を行う利用者を選択してください',SET_CUSTOMER_LIST.keys(), index=0, placeholder='利用者を選択') 
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
        summarized_text = summarize_text(result_text, set_customer, content_maxStr_to_gpt) # ChatGPTを使って要約の実行
    st.success('要約結果:') # 表示を変更
    state_summary.empty() # 要約内容を入れるための箱を用意
    st.write(summarized_text) # メソッドから帰ってきた値を表示
    # 要約をwordファイルに保存
    word_file = save_summary_to_word(summarized_text)
    st.download_button(
        label='Wordファイルに保存',
        data=word_file,
        file_name='summary.docx',
        mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )

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
        summarized_text = summarize_text(recognized_text, set_customer, content_maxStr_to_gpt) # ChatGPTを使って要約の実行
    st.success('要約結果') # 表示を変更 
    state_summary.empty()# 要約内容を入れるための箱を用意
    st.write(summarized_text) # メソッドから帰ってきた値を表示
    # 要約をwordファイルに保存
    word_file = save_summary_to_word(summarized_text)
    st.download_button(
        label='Wordファイルに保存',
        data=word_file,
        file_name='summary.docx',
        mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )