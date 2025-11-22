from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai.types import HttpRetryOptions
from langfuse import get_client
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

from google.genai import types

from deep_research.prompt import (
    RESEARCHER_INSTRUCTION,
    QUESTIONER_INSTRUCTION,
    REPORTER_INSTRUCTION,
)


# langfuseへのトレーシング設定
get_client()
GoogleADKInstrumentor().instrument()

class DeepResearchAgent:
    def __init__(self, model_name:str, max_research_loop:int):
        # 頻繁に起こるmodelのrate_limit等のエラー回避のための設定
        retry_options = HttpRetryOptions(
            attempts=10,
            initial_delay=1.0,
            max_delay=10.0,
            exp_base=2,
            jitter=1,
            http_status_codes=[429, 503],
        )

        model = Gemini(model=model_name, retry_options=retry_options)

        questioner = LlmAgent(
            model=model,
            name="questioner",
            instruction=QUESTIONER_INSTRUCTION,
        )

        researcher = LlmAgent(
            model=model,
            name="researcher",
            instruction=RESEARCHER_INSTRUCTION,
            tools=[google_search],
        )

        looper = LoopAgent(
            name="looper",
            sub_agents=[researcher, questioner],
            max_iterations=max_research_loop,
        )

        reporter = LlmAgent(
            name="reporter",
            model=model,
            instruction=REPORTER_INSTRUCTION,
        )

        sequencer = SequentialAgent(name="sequencer", sub_agents=[looper, reporter])

        self.deep_research_agent = sequencer

    async def get_research_report(
        self, query: str,
        app_name:str = "agents",
        user_id:str = "streamlit-user",
        session_id:str = "session-id",
    ) -> tuple[str | None, list[str], list[types.GroundingChunk], str | None]:
        session_service = InMemorySessionService()

        try:
            # セッションとランナーの初期化
            session = await session_service.create_session(
                app_name=app_name, user_id=user_id, session_id=session_id
            )

            runner = Runner(
                agent=self.deep_research_agent,
                app_name=app_name,
                session_service=session_service,
            )

            # ユーザーのクエリをContentオブジェクトとして作成
            content = types.Content(role="user", parts=[types.Part(text=query)])

            grounding_search_list = []
            grounding_web_site_list = []
            # エージェントを非同期で実行
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=content,
            ):
                # イベントの中に、'reporter' の発言があった時のみtextを抽出する。
                if (
                    event.content
                    and event.content.parts
                    and event.content.parts[0].text
                    and event.author == "reporter"
                ):
                    report = event.content.parts[0].text

                # グラウンディングメタデータの取得
                if event.grounding_metadata:
                    # 検索結果画面（google_search利用規約上、表示が必須）
                    if (
                        event.grounding_metadata.search_entry_point
                        and event.grounding_metadata.search_entry_point.rendered_content
                    ):
                        rendered_content = (
                            event.grounding_metadata.search_entry_point.rendered_content
                        )
                        grounding_search_list.append(rendered_content)

                    # 検索されたWebサイトのリンク
                    if event.grounding_metadata.grounding_chunks:
                        grounding_web_site_list += (
                            event.grounding_metadata.grounding_chunks
                        )

            return report, grounding_search_list, grounding_web_site_list, None

        except Exception as e:
            # エラーハンドリング
            error_message = f"エージェント実行中にエラーが発生しました: {e}"
            return None, [], [], error_message
