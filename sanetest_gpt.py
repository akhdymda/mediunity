import streamlit as st
from openai import OpenAI
import os
import datetime 
from customer_list import SET_CUSTOMER_LIST

# OpenAI APIキーの設定
OpenAI.api_key = os.environ['OPENAI_API_KEY'] # 環境変数化したAPIキーの読み込み

# OpenAIクライアントの初期化
client = OpenAI()

# 今日の日付
today = datetime.date.today()

# 前月の1日と最終日を計算
first_day_last_month = (today.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)
last_day_last_month = (today.replace(day=1) - datetime.timedelta(days=1))

# StreamlitアプリのUI構築
st.title("ホカンサポ／月次報告書生成用")
st.header('利用者選択',divider=True)
set_customer = st.selectbox('記録を行う利用者を選択してください',SET_CUSTOMER_LIST.keys(), index=0, placeholder='利用者を選択') 
st.write('利用者名:', set_customer)

st.header('期間選択',divider=True)

# 日付入力
selected_dates = st.date_input(
    "出力する期間を選択してください",
    (first_day_last_month, last_day_last_month),  # デフォルトの選択期間
    format="YYYY-MM-DD",  # 表示フォーマット
)

# 選択結果を表示
st.write(f"選択した期間: {selected_dates[0]} から {selected_dates[1]}")

st.header('記録情報の入力',divider=True)

# ユーザー入力の取得（広い入力枠を提供）
user_input = st.text_area(
    "看護記録に基づく情報を入力してください（例: 病状、看護内容、家庭状況など）",
    height=400
)

# GPTに看護記録を書かせる関数
def run_gpt(user_input):
    # 日付範囲を文字列に変換
    start_date = selected_dates[0].strftime("%Y-%m-%d")
    end_date = selected_dates[1].strftime("%Y-%m-%d")
    
    request_to_gpt = (
        f"以下の情報を基に訪問看護報告書を作成してください:\n"
        f"{user_input}\n"
        "訪問看護報告書の内容は、利用者氏名、報告期間を記載した後、以下の記録の内容から「病状の経過」「看護・リハビリテーションの内容」「家庭での介護の状況」の順で、"
        "中立的かつ客観的な文章で出力してください。"
        f"利用者氏名は{set_customer}様、報告期間は（{start_date} から {end_date}）です。"
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": request_to_gpt}],
    )
    output_content = response.choices[0].message.content.strip()
    return output_content

# ボタンを押してGPTに看護記録を生成させる
state_report = st.empty()
if st.button("看護記録を生成"):
    if user_input.strip():  # 入力が空でない場合のみ実行
        st.info("看護記録を生成中...")
        try:
            # GPTを呼び出して看護記録を取得
            output_content = run_gpt(user_input)
            st.success("生成完了！以下の看護記録をご確認ください。")
            st.write("生成された訪問看護報告書:")
            state_report.empty()
            st.write(output_content, height=1000)

            # ダウンロードボタンを設置
            st.download_button(
                label="看護記録をダウンロード",
                data=output_content,
                file_name="nursing_record.txt",
                mime="text/plain",
            )
        except Exception as e:
            st.error(f"看護記録の生成中にエラーが発生しました: {e}")
    else:
        st.warning("看護記録に必要な情報を入力してください。")