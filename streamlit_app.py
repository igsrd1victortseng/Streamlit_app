import streamlit as st
import pandas as pd
import openai
import io

st.title("📄 OpenAI 批次工作流工具")

openai.api_key = st.secrets["OPENAI_API_KEY"]

uploaded_file = st.file_uploader("上傳 CSV 檔案（每列一個輸入）", type=["csv"])
prompt_template = st.text_area("請輸入提示詞（可使用 {input} 作為每列的佔位符）")
start_button = st.button("開始處理")

if uploaded_file and prompt_template and start_button:
    df = pd.read_csv(uploaded_file)
    input_column = df.columns[0]
    inputs = df[input_column].astype(str).tolist()

    output_data = []

    with st.spinner("呼叫 OpenAI API 處理中..."):
        for i, input_text in enumerate(inputs):
            final_prompt = prompt_template.replace("{input}", input_text)

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": final_prompt}]
                )
                output_text = response['choices'][0]['message']['content'].strip()
                output_data.append(output_text)
            except Exception as e:
                output_data.append(f"ERROR: {e}")

    # 分析第一行格式，決定是否需要分多欄
    first_output = output_data[0]
    if first_output.count(",") >= 2:
        out_df = pd.DataFrame([line.split(",") for line in output_data])
    else:
        out_df = pd.DataFrame(output_data, columns=["output"])

    # 匯出 CSV
    csv_buffer = io.StringIO()
    out_df.to_csv(csv_buffer, index=False)
    st.download_button("📥 下載結果 CSV", data=csv_buffer.getvalue(), file_name="output.csv", mime="text/csv")
