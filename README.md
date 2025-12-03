# Deep Research Agent

これは、GoogleのAgent Development Kit (ADK)を利用して構築された、深層的なリサーチを行うAIエージェントです。ユーザーが指定したトピックについて、複数のAIエージェントが協調して調査を行い、詳細なレポートを生成します。

アプリケーションはStreamlitで構築されており、Webインターフェースを通じて誰でも簡単に利用できます。

## 主な機能

- **マルチエージェント・システム**: 3つの異なる役割を持つAIエージェントが連携してリサーチを行います。
    - **研究者 (Researcher)**: Google検索を使い、トピックに関する情報を収集します。
    - **質問者 (Questioner)**: 収集された情報をもとに、さらに調査を深めるための新たな質問を生成します。
    - **報告者 (Reporter)**: 最終的に得られた情報を統合し、構造化されたレポートを作成します。
- **モデル選択**: リサーチに使用するGoogleのGeminiモデル（`gemini-flash-lite-latest` または `gemini-2.5-pro`）を選択できます。
- **リサーチ回数の調整**: エージェントが調査を繰り返す最大回数を設定でき、リサーチの深度をコントロールできます。
- **参照元の表示**: 生成されたレポートには、情報源となったWebサイトへのリンクが含まれており、情報の信頼性を確認できます。

## 技術スタック

- **フレームワーク**: Google ADK (Agent Development Kit)
- **UI**: Streamlit
- **LLM**: Google Gemini
- **モニタリング**: Langfuse
- **言語**: Python 3.11+

## セットアップと実行方法

### 1. 前提条件

- Python 3.11以上
- Google AI StudioでAPIキーを取得していること
- Langfuseのアカウントを作成し、APIキーを取得していること（任意）

### 2. インストール

1. このリポジトリをクローンします。
   ```bash
   git clone https://github.com/your-username/adk-deepresearch.git
   cd adk-deepresearch
   ```

2. 依存関係をインストールします。`uv` を使ってインストールするのがおすすめです。
   ```bash
   pip install uv
   uv pip sync pyproject.toml
   ```
   もしくは`pip`のみを利用する場合：
   ```bash
   pip install .
   ```

### 3. 環境変数の設定

1. `app`ディレクトリにある`.env.sample`ファイルをコピーして、`.env`という名前のファイルを作成します。
   ```bash
   cp app/.env.sample app/.env
   ```

2. `.env`ファイルを編集し、各APIキーを設定します。
   ```plaintext
   # .env
   GOOGLE_API_KEY="your_google_api_key"

   # Langfuse (任意)
   LANGFUSE_PUBLIC_KEY="your_langfuse_public_key"
   LANGFUSE_SECRET_KEY="your_langfuse_secret_key"
   ```

### 4. アプリケーションの実行

仮想環境に入る

Mac
```
source .venv/bin/activate
```

Windows
```
.\.venv\Scripts\activate
```

以下のコマンドでStreamlitアプリケーションを起動します。

```bash
streamlit run app/main.py
```

ブラウザで `http://localhost:8501` を開くと、アプリケーションが表示されます。
