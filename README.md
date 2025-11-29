# JRVLTSQL - JRA-VAN Link To SQL

JRA-VAN DataLabの競馬データをSQLite/PostgreSQLにインポートするPythonツール

[![Tests](https://github.com/miyamamoto/jrvltsql/actions/workflows/test.yml/badge.svg)](https://github.com/miyamamoto/jrvltsql/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.10+%20(32bit)-blue.svg)](https://www.python.org/downloads/)

## 特徴

- **全38レコードタイプ対応**: 1986年以降の全競馬データ
- **57テーブル**: NL_38（蓄積系）+ RT_19（速報系）
- **SQLite標準**: 軽量・高速（PostgreSQLも対応）
- **レジストリー不要**: 設定ファイル/環境変数でサービスキーを管理
- **バッチ処理最適化**: 1000件/batch + 50+インデックス

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
| レース | RA, SE, HR, JG | レース詳細、出馬表、払戻、重賞 |
| マスタ | UM, KS, CH, BR, BN | 馬、騎手、調教師、生産者、馬主 |
| オッズ | O1-O6 | 単勝〜3連単 |

### RT_テーブル（速報系: 19テーブル）

リアルタイム監視（`jltsql monitor`）で取得。NL_テーブルと同じ構造。

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
