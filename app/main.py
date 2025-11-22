import asyncio

from dotenv import load_dotenv
load_dotenv()

import nest_asyncio
import streamlit as st

from deep_research.agent import DeepResearchAgent


nest_asyncio.apply()


# --- Streamlit UI 定義 ---
st.title("Deep Research App")
st.markdown("入力されたトピックに関するリサーチレポートを生成します。")

# 質問の入力フォーム
with st.form(key="research_form"):
    st.markdown("⚙️ **設定**")

    # モデル名の選択
    model_name = st.selectbox(
        "使用するモデル:",
        ("gemini-flash-lite-latest", "gemini-2.5-pro"),
        index=0,  # デフォルトは 'gemini-flash-lite-latest'
        help="リサーチに使用するAIモデルを選択します。",
    )

    # 最大ループ回数の設定
    max_research_loop = st.number_input(
        "最大リサーチ回数（ループ数）:",
        min_value=1,  # 最小値
        max_value=10,  # 最大値
        value=3,  # デフォルト値
        step=1,  # 増加単位
        help="エージェントが内部でリサーチを行う最大回数を設定します。回数が多いほど深く調査しますが、時間がかかります。",
    )

    st.divider()

    query = st.text_area(
        "リサーチしたい質問を入力してください:",
        height=100,
        placeholder="例: AIエージェントとは？",
    )

    submit_button = st.form_submit_button(label="リサーチ実行")

# 実行ボタンが押された場合の処理
if submit_button:
    if not query.strip():
        st.warning("質問を入力してください。")
    else:
        with st.spinner("リサーチを実行中です... (数分かかる場合があります)"):
            # DeepResearchAgentの実行
            deep_research_agent = DeepResearchAgent(model_name, max_research_loop)
            report, grounding_search_list, grounding_web_site_list, err = asyncio.run(
                deep_research_agent.get_research_report(query)
            )

            if err:
                st.error(err)

            else:
                # レポートの表示
                st.markdown(report)

                # 検索結果ページの表示
                if grounding_search_list:
                    st.subheader("検索結果ページ")
                    # 重複を削除してから表示
                    unique_search_html = list(dict.fromkeys(grounding_search_list))
                    for html_content in unique_search_html:
                        # HTMLをそのままレンダリング
                        st.markdown(html_content, unsafe_allow_html=True)
                        st.divider()  # 各HTMLコンテンツ間に区切り線を入れる

                # 参照Webサイトの表示
                if grounding_web_site_list:
                    st.subheader("参照Webサイト")
                    # リンクの重複を削除（URLベース）
                    unique_links = {}
                    for site in grounding_web_site_list:
                        uri = site.web.uri
                        # URLが存在し、まだ辞書にない場合のみ追加
                        if uri and uri not in unique_links:
                            unique_links[uri] = site.web.title  # URIをキーに辞書に格納

                    # 箇条書きでリンクを表示
                    for uri, title in unique_links.items():
                        st.markdown(f"- [{title}]({uri})")
