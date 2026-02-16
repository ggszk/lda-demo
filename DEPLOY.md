# デプロイ手順

## 環境情報

| 項目 | 値 |
|------|-----|
| GCPプロジェクトID | `ggszk-lab` |
| リージョン | `asia-northeast1`（東京） |
| サービス名 | `lda-demo` |
| サービスURL | https://lda-demo-655957689949.asia-northeast1.run.app |

---

## ローカル開発

```bash
# 仮想環境のセットアップ（初回のみ）
python -m venv .venv
pip install -r requirements.txt

# 開発サーバー起動
make dev
# → http://localhost:8080 でアクセス
```

---

## Cloud Run へのデプロイ

### 初回のみ必要な設定

```bash
gcloud auth login
gcloud config set project ggszk-lab
gcloud services enable run.googleapis.com artifactregistry.googleapis.com
```

### デプロイ

```bash
make deploy
```

### その他のコマンド

```bash
make logs   # 直近50件のログを表示
make open   # ブラウザでアプリを開く
```

---

## トラブルシューティング

詳細は [`KPU/_tech-notes/gcp-cloud-run-setup.md`] を参照。
