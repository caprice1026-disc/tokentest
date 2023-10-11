import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)
from langchain.callbacks import get_openai_callback
import os  


# モデルごとのトークン価格（1000トークンあたりのドル）
MODEL_TOKEN_COST = {
    "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
    "gpt-4": {"input": 0.03, "output": 0.06},
}

# 為替レートを定義（1ドル=150円）
EXCHANGE_RATE = 150

def init_page():
    st.set_page_config(
        page_title="My Great ChatGPT",
        page_icon="🤗"
    )
    st.header("My Great ChatGPT 🤗")
    st.sidebar.title("Options")

def init_messages():
    clear_button = st.sidebar.button("Clear Conversation", key="clear")
    if clear_button or "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessage(content="You are a helpful assistant.")
        ]
        st.session_state.costs = []
        st.session_state.tokens = []

def select_model():
    model = st.sidebar.radio("Choose a model:", ("GPT-3.5", "GPT-4"))
    if model == "GPT-3.5":
        model_name = "gpt-3.5-turbo"
    else:
        model_name = "gpt-4"

    st.session_state.input_cost = MODEL_TOKEN_COST[model_name]["input"]
    st.session_state.output_cost = MODEL_TOKEN_COST[model_name]["output"]

    temperature = st.sidebar.slider("Temperature:", min_value=0.0, max_value=2.0, value=0.0, step=0.01)
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    openai_organization = os.environ.get("OPENAI_ORGANIZATION_ID")  # 環境変数から組織IDを取得（もしあれば）

    return ChatOpenAI(temperature=temperature, model_name=model_name, openai_api_key=openai_api_key, openai_organization=openai_organization)  # APIキーと組織IDを渡す

def get_answer(llm, messages):
    with get_openai_callback() as cb:
        answer = llm(messages)
    return answer.content, cb.total_cost, cb.total_tokens

def main():
    init_page()

    llm = select_model()
    init_messages()

    if user_input := st.chat_input("聞きたいことを入力してね！ ドル円は150円として計算しています。"):
        st.session_state.messages.append(HumanMessage(content=user_input))
        with st.spinner("ChatGPT is typing ..."):
            answer, cost, tokens = get_answer(llm, st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=answer))
        st.session_state.costs.append(cost)
        st.session_state.tokens.append(tokens)

    messages = st.session_state.get('messages', [])
    for message in messages:
        if isinstance(message, AIMessage):
            with st.chat_message('assistant'):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message('user'):
                st.markdown(message.content)
        else:  # isinstance(message, SystemMessage):
            st.write(f"System message: {message.content}")

    costs = st.session_state.get('costs', [])
    tokens = st.session_state.get('tokens', [])
    st.sidebar.markdown("## Costs")
    total_cost_dollar = sum(costs)
    total_cost_yen = total_cost_dollar * EXCHANGE_RATE
    st.sidebar.markdown(f"**Total cost: ${total_cost_dollar:.5f} ({total_cost_yen:.0f}円)**")
    for cost, token in zip(costs, tokens):
        cost_yen = cost * EXCHANGE_RATE
        token_cost_dollar = token * st.session_state.input_cost
        token_cost_yen = token_cost_dollar * EXCHANGE_RATE
        st.sidebar.markdown(f"- ${cost:.5f} ({cost_yen:.0f}円) for {token} tokens (${token_cost_dollar:.5f}, {token_cost_yen:.0f}円)")

if __name__ == '__main__':
    main()