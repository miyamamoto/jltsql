# JRVLTSQL - JRA-VAN Link To SQL

JRA-VAN DataLabの競馬データをSQLite/PostgreSQLにインポートするPythonツール

[![Tests](https://github.com/miyamamoto/jrvltsql/actions/workflows/test.yml/badge.svg)](https://github.com/miyamamoto/jrvltsql/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.10+%20(32bit)-blue.svg)](https://www.python.org/downloads/)

## 特徴

- **全38レコードタイプ対応**: 1986年以降の全競馬データ
- **58テーブル**: NL_38（蓄積系）+ RT_20（速報系）
- **SQLite標準**: 軽量・高速（PostgreSQLも対応）
- **レジストリー不要**: 設定ファイル/環境変数でサービスキーを管理
- **バッチ処理最適化**: 1000件/batch + 61インデックス
- **EveryDB2準拠**: JVOpen/JVRTOpen の全データ種別に対応

## クイックスタート

### 1. インストール

```bash
pip install git+https://github.com/miyamamoto/jrvltsql.git
```

### 2. セットアップ

```bash
# 対話形式で初期設定（サービスキー入力 → 過去10年分のデータ取得）
jltsql quickstart
```

これだけで完了です。

## 必要要件

| 項目 | 要件 |
|------|------|
| OS | Windows 10/11 |
| Python | 3.10+ **(32bit版のみ)** |
| 会員 | JRA-VAN DataLab（月額2,090円） |

### Python 32bit版について

JV-Link COM APIは32bit専用のため、**Python 32bit版が必須**です。

```bash
# ビット数を確認
python -c "import struct; print(struct.calcsize('P') * 8, 'bit')"
```

64bit版しかない場合は、[Python公式サイト](https://www.python.org/downloads/windows/)から「Windows installer (32-bit)」をダウンロードしてください。

## 設定

サービスキーは以下のいずれかで設定：

```bash
# 環境変数（推奨）
set JVLINK_SERVICE_KEY=XXXX-XXXX-XXXX-XXXX-X
```

```yaml
# config/config.yaml
jvlink:
  service_key: "XXXX-XXXX-XXXX-XXXX-X"
```

## コマンド一覧

```bash
jltsql quickstart              # 対話形式で初期セットアップ
jltsql init                    # 初期化のみ
jltsql create-tables           # テーブル作成
jltsql create-indexes          # インデックス作成
jltsql fetch --spec RACE       # データ取得
jltsql monitor                 # リアルタイム監視
jltsql status                  # ステータス確認
```

詳細: `jltsql --help`

## データベース構造

### NL_テーブル（蓄積系: 38テーブル）

| カテゴリ | テーブル | 説明 |
|---------|---------|------|
| レース | RA, SE, HR, JG, WF | レース詳細、出馬表、払戻、重賞、WIN5 |
| マスタ | UM, KS, CH, BR, BN, HN, SK | 馬、騎手、調教師、生産者、馬主、繁殖馬、産駒 |
| オッズ | O1-O6, H1, H6 | 単勝〜3連単オッズ、票数 |
| 調教 | WC, HS | ウッドチップ調教、坂路調教 |
| 成績 | JC, CC, TC, RC | 騎手成績、競走馬成績、調教師/騎手変更 |
| その他 | DM, TM, AV, YS, TK | データマイニング、場外発売、スケジュール、特別登録 |

### RT_テーブル（速報系: 20テーブル）

JVRTOpenで取得するリアルタイムデータ。`jltsql monitor`で監視。

| カテゴリ | テーブル | 説明 |
|---------|---------|------|
| 速報系（0B1x, 0B4x） | RA, SE, HR, WE, WH, DM, TM, AV, RC, TC | レース結果、馬体重、騎手/調教師変更 |
| 時系列（0B2x-0B3x） | O1-O6, H1, H6 | オッズ変動、票数推移 |

## 対応データ種別（JVOpen）

[EveryDB2表5.1-1](https://everydb.iwinz.net/edb2_manual/)に準拠。

| データ種別 | 説明 | Option 1 | Option 2 |
|-----------|------|----------|----------|
| TOKU | 特別登録馬 | o | o |
| RACE | レース情報 | o | o |
| DIFF/DIFN | マスタ情報 | o | - |
| BLOD/BLDN | 血統情報 | o | - |
| MING | データマイニング予想 | o | - |
| SLOP | 坂路調教 | o | - |
| WOOD | ウッドチップ調教 | o | - |
| YSCH | 開催スケジュール | o | - |
| HOSE/HOSN | 市場取引価格 | o | - |
| HOYU | 馬名の意味由来 | o | - |
| COMM | コメント情報 | o | - |
| TCVN | 調教師変更情報 | - | o |
| RCVN | 騎手変更情報 | - | o |
| O1-O6 | オッズ | o | - |

## 開発者向け

```bash
git clone https://github.com/miyamamoto/jrvltsql.git
cd jrvltsql
pip install -e ".[dev]"
pytest
```

## ライセンス

Apache License 2.0

### JRA-VAN利用規約

取得したデータは[JRA-VAN利用規約](https://jra-van.jp/info/rule.html)に従ってください。

- ✅ 個人的な競馬分析・研究
- ❌ データの再配布・第三者提供

## リンク

- [JRA-VAN DataLab](https://jra-van.jp/dlb/)
- [Issues](https://github.com/miyamamoto/jrvltsql/issues)
