#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""JVLinkWrapper直接テスト"""

import sys
import os

# Windows環境でのUTF-8出力設定
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from src.jvlink.wrapper import JVLinkWrapper
from src.jvlink.constants import get_error_message

print("=" * 70)
print("JVLinkWrapper 直接テスト")
print("=" * 70)
print()

# JVLinkWrapper初期化
print("JVLinkWrapper を初期化しています...")
print("注意: サービスキーはJRA-VAN DataLabアプリで設定されている必要があります")
print()
wrapper = JVLinkWrapper()  # デフォルト sid="UNKNOWN"
print("[OK] JVLinkWrapper 初期化完了")
print(f"  Session ID: {wrapper.sid}")
print()

# JV_Init呼び出し
print("JV_Init() を呼び出しています...")
try:
    ret_code = wrapper.jv_init()
    print(f"[OK] JV_Init() 実行完了")
    print(f"  戻り値: {ret_code}")
    print(f"  メッセージ: {get_error_message(ret_code)}")
    print()

    if ret_code == 0:
        print("[SUCCESS] JV-Link初期化成功！")
        print()
        print("次は実際のデータ取得テストを実行します...")
        print()

        # 簡単なステータスチェック
        print("JV_Status() でステータスを確認...")
        try:
            status = wrapper.jv_status()
            print(f"[OK] ステータス: {status}")
        except Exception as e:
            print(f"[WARN] ステータス取得失敗: {e}")

    else:
        print(f"[ERROR] JV-Link初期化失敗 (コード: {ret_code})")
        print()
        print("考えられる原因:")
        if ret_code == -101:
            print("  - JV-Linkサービスが起動していない")
            print("  - JRA-VAN DataLabアプリを起動してください")
        elif ret_code == -102:
            print("  - サービスキーが未登録")
            print("  - JRA-VAN DataLabで初回設定を完了してください")
        elif ret_code == -103:
            print("  - サービスキーが無効または期限切れ")
            print("  - JRA-VANの契約状況を確認してください")
        elif ret_code == -104:
            print("  - ネットワークエラー")
            print("  - インターネット接続を確認してください")
        else:
            print(f"  - 不明なエラー (コード: {ret_code})")
            print("  - JRA-VANサポートに問い合わせてください")
        print()
        print("【対処方法】")
        print("1. JRA-VAN DataLabアプリケーションを起動")
        print("2. 「設定」→「サービスキー設定」でキーを確認")
        print("3. JV-Linkサービスが実行中か確認")
        print("4. インターネット接続を確認")

except Exception as e:
    print(f"[ERROR] エラー発生: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("テスト完了")
print("=" * 70)
