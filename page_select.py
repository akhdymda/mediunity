import streamlit as st

pages = {
    'アプリ': [
        st.Page('medi_app.py', title='ホカンサポ／訪問記録作成用'),
        st.Page('monthly_report.py', title='ホカンサポ／月次報告書生成用')
    ]}

pg = st.navigation(pages)
pg.run()