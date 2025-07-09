# md2pptx - Markdown to PowerPoint Converter

Markdown ファイルから PowerPoint プレゼンテーションを自動生成するツールです。

## 特徴

- 📝 シンプルな Markdown 記法でスライドを作成
- 🎨 PowerPoint テンプレートによるデザイン統一
- 📊 Mermaid 図表の自動レンダリング
- 📋 表の自動変換
- 🖥️ GUI とコマンドラインの両方に対応
- 🔒 完全オフライン動作

## インストール

### 開発環境

```bash
# リポジトリのクローン
git clone https://github.com/yourusername/md2pptx.git
cd md2pptx

# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt
```

### 実行ファイルのビルド

```bash
# PyInstaller でビルド
python build.py
```

## 使い方

### GUI モード

```bash
python main.py
```

1. PowerPoint テンプレートを選択（オプション）
2. 変換する Markdown ファイルを選択
3. 出力先を指定
4. 「Convert」ボタンをクリック

### コマンドラインモード

```bash
# 基本的な使い方
python main.py -m sample.md -o output.pptx --silent

# テンプレートを指定
python main.py -m sample.md -t template.pptx -o output.pptx --silent

# 高解像度の図表
python main.py -m sample.md -o output.pptx --dpi 300 --silent
```

## Markdown 記法

### スライドの区切り

- `#` (H1) - 最初の H1 はタイトルスライド
- `##` (H2) - 新しいスライドの開始
- `###` (H3) - H2 直後の H3 はリード文として扱われます

### サポートする要素

- 段落テキスト
- 箇条書きリスト（`-`, `*`）
- 番号付きリスト
- コードブロック
- 画像（`![alt](path)`）
- 表
- Mermaid 図表

### 例

```markdown
# プレゼンテーションタイトル

サブタイトルや説明文

## スライド 1

### これはリード文です

本文の内容：

- 箇条書き項目 1
- 箇条書き項目 2

## Mermaid 図表の例

```mermaid
graph LR
    A[開始] --> B[処理]
    B --> C[終了]
```
```

## 開発

### テストの実行

```bash
pytest
```

### コードフォーマット

```bash
black md2pptx
```

## システム要件

- Python 3.13+
- Windows 11 (ARM/x64)
- オフライン環境対応

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します。大きな変更を行う場合は、まず Issue を作成して変更内容について議論してください。
