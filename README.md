# JRVLTSQL

JRA-VAN DataLabの競馬データをSQLite/PostgreSQLにインポートするツール

## インストール

### 必要要件

- Windows 10/11
- Python 3.10+ （32bit/64bit両対応）
- JRA-VAN DataLab会員

### セットアップ

```bash
pip install git+https://github.com/miyamamoto/jrvltsql.git
```

**quickstart.bat をダブルクリック** で対話形式のセットアップが始まります。

### Python 32bit/64bit について

JV-Link APIは32bit DLLですが、**64bit Pythonでも使用可能**です。

#### 64bit Pythonを使う場合（推奨）

`tools/enable_64bit_python.bat` を**管理者権限**で実行してください。
WindowsのDLLサロゲート機能を有効化し、64bit Pythonから32bit JV-Linkを呼び出せるようになります。

```batch
# 管理者権限でコマンドプロンプトを開いて実行
cd tools
enable_64bit_python.bat
```

#### Pythonバージョン確認

```bash
python -c "import struct; print(struct.calcsize('P') * 8, 'bit')"
```

## 使い方

### quickstartオプション

```bash
python scripts/quickstart.py              # 対話形式
python scripts/quickstart.py --years 5    # 過去5年分
python scripts/quickstart.py --no-odds    # オッズ除外
python scripts/quickstart.py -y           # 確認スキップ
```

### CLIコマンド

```bash
jltsql status           # ステータス確認
jltsql fetch --spec RA  # 個別データ取得
jltsql monitor          # リアルタイム監視
```

## データ構造

- **NL_テーブル**: 蓄積系データ（レース、馬、騎手など）
- **RT_テーブル**: 速報系データ（リアルタイムオッズなど）
- **TS_テーブル**: 時系列オッズ

## ライセンス

- 非商用利用: Apache License 2.0
- 商用利用: 事前にお問い合わせください → oracle.datascientist@gmail.com

取得データは[JRA-VAN利用規約](https://jra-van.jp/info/rule.html)に従ってください。
