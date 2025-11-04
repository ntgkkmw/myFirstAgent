# Codex MAS（日本語版）

Codex MASは、[pydantic_ai](https://github.com/pydantic/pydantic-ai) と OpenAI API を用いて構築された、本番運用を意識したマルチエージェントワークフローです。ユーザーからの問い合わせをルーター → 各専門家 → レビュアーというパイプラインで処理し、すべてのエージェント出力を Pydantic モデルで検証します。

## 特長

- ルーター、リサーチャー、コーダー、テスター、サマライザー、レビュアーが構造化出力で連携。
- トークン使用量のガードレールと、必要に応じてより高性能なコーダーモデルへエスカレーション。
- Web 検索、RAG 取得、ドライランでのパッチ適用、テスト実行のシミュレーションといったツール統合。
- `.env` / `.env.local` による設定と型付き DI（依存性注入）で柔軟に構成可能。
- `detect-secrets` を用いたプリコミット設定により、秘密情報の誤コミットを防止。

## はじめに

1. **環境ファイルを作成**

   ```bash
   cp .env.example .env
   ```

   `OPENAI_API_KEY` に有効なキーを設定してください。`.env` と `.env.local` は `.gitignore` によりリポジトリには含めないようになっています。

2. **依存関係をインストール**

   ```bash
   make dev
   ```

   これにより仮想環境（`.venv`）が作成され、ランタイム依存（`pydantic_ai[openai]`、`openai`、`pydantic` など）および開発ツール（`pre-commit`、`detect-secrets`）がインストールされます。

3. **ワークフローを実行**

   ```bash
   make run ask="Summarize the latest release notes"
   ```

   追加のフラグ例：

   - `make run ask="..." constraints="needs unit tests"`
   - `make run ask="..." style="concise"`

4. **プリコミットフックをセットアップ**

   ```bash
   .venv/bin/pre-commit install
   ```

   秘密情報は GitHub Actions Secrets や 1Password などのプラットフォームのボールトで管理してください。`.secrets.baseline` に含まれる `detect-secrets` ベースラインを活用し、カバレッジを維持します。

5. **スモークテスト（簡易評価）**

   ```bash
   make eval
   ```

   要約、テスト方針、コーディングの 3 つの代表的なフローを実行し、エージェントオーケストレーションを検証します。

## リポジトリ構成

```
packages/
  codex-mas -> spec 準拠のためのシンボリックリンク
  codex_mas/
    app/runner.py
    agents/
    tools/
    schemas/
    config/
    llm/
    examples/
```

- `config/settings.py` – 型付き設定と依存性コンテナ（`Deps`）。
- `llm/registry.py` – `pydantic_ai` 向けの OpenAI クライアントアダプタ。
- `schemas/models.py` – エージェント間で共有される Pydantic スキーマ。
- `app/runner.py` – ルーター → 各専門家 → レビュアーを調停する CLI オーケストレーター。
- `examples/quickstart.ipynb` – 対話的に学べるチュートリアルノートブック。

## シークレットと環境変数の管理

- `.env` と `.env.local` は Git にコミットしないでください。
- `OPENAI_API_KEY` は GitHub Secrets、1Password、Vault などの安全なストレージから取得します。
- CI パイプラインでは環境変数としてシークレットを注入してください。
- `detect-secrets` が意図しない認証情報のコミットを防ぎます。設定を変更した場合はベースラインを更新してください。

## 開発メモ

- トークン使用量のガード：`TOKEN_BUDGET_TOTAL` で構成可能。エージェントは使用量を見積もり、上限超過前に処理を中断します。
- コーダーのエスカレーション：スキーマ検証に失敗した場合、`.env` で指定した上位モデルで再実行します。
- ツールはオフライン開発向けにモック化されています。必要に応じて本番用の統合に差し替えてください。

## ライセンス

MIT
