import streamlit as st
from openai import OpenAI
import os
import datetime
import pandas as pd
from customer_list import SET_CUSTOMER_LIST

# OpenAI APIキーの設定
OpenAI.api_key = os.environ['OPENAI_API_KEY']  # 環境変数化したAPIキーの読み込み

# OpenAIクライアントの初期化
client = OpenAI()

# 今日の日付
today = datetime.date.today()

# 前月の1日と最終日を計算
first_day_last_month = (today.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)
last_day_last_month = (today.replace(day=1) - datetime.timedelta(days=1))

# StreamlitアプリのUI構築
st.title("ホカンサポ／月次報告書生成用")

# 利用者選択
st.header('利用者選択',divider=True)
set_customer = st.selectbox('記録を行う利用者を選択してください',SET_CUSTOMER_LIST.keys(), index=0, placeholder='利用者を選択') 
st.write('利用者名:', set_customer)

# 期間選択
st.header('期間選択', divider=True)
selected_dates = st.date_input(
    "出力する期間を選択してください",
    (first_day_last_month, last_day_last_month),
    format="YYYY-MM-DD",
)
st.write(f"選択した期間: {selected_dates[0]} から {selected_dates[1]}")

# 記録情報の入力
st.header('記録情報の入力', divider=True)
user_input = st.text_area(
    "看護記録に基づく情報を入力してください（例: 病状、看護内容、家庭状況など）",
    height=400
)

# GPTに看護記録を書かせる関数
def run_gpt(user_input):
    request_to_gpt = (
        f"以下の情報を元に訪問看護報告書の報告書式の各項目を出力してください:\n"
        f"{user_input}\n\n"
        "報告書式は以下の項目で構成されます：\n"
        "1. 病状の経過: 利用者の病状の経過や日常生活動作（ADL）の状況などを記載してください。\n"
        "2. 看護の内容: 実施した看護の内容を箇条書きで記載してください（例：入浴介助、褥瘡処置、点滴管理など）。\n"
        "3. 家庭での介護の状況: 家族が介護をしているのか、家族の状態などを記載してください。\n\n"
        "各項目を独立して、中立的かつ客観的な文章で記載してください。"
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": request_to_gpt}],
    )
    return response.choices[0].message.content.strip()

# 報告書出力
st.header('報告書の出力', divider=True)

# ボタンを押してGPTに看護記録を生成させる
if st.button("看護記録を生成"):
    if user_input.strip():  # 入力が空でない場合のみ実行
        st.info("看護記録を生成中...")
        try:
            # GPTで生成
            report_content = run_gpt(user_input)

            # 結果をDataFrameに分割して構成
            sections = ["病状の経過", "看護の内容", "家庭での介護の状況"]
            section_contents = report_content.split("\n\n")  # 各セクションを分割

            data = [{"項目": sections[i], "内容": section_contents[i]} for i in range(len(sections))]

            df = pd.DataFrame(data)

            # DataEditorの設定
            config = {
                "項目": st.column_config.TextColumn("項目名", width="small"),
                "内容": st.column_config.TextColumn("詳細内容", max_chars=None)  # 折り返しを有効化
            }

            # DataEditorで表示
            st.success("生成完了！以下の看護記録をご確認ください。")
            st.data_editor(
                df,
                column_config=config,
                hide_index=True,  # インデックスを非表示
                use_container_width=True,  # テーブル幅をコンテナに合わせる
                num_rows="fixed"  # 行の追加を禁止
            )

        except Exception as e:
            st.error(f"看護記録の生成中にエラーが発生しました: {e}")
    else:
        st.warning("看護記録に必要な情報を入力してください。")