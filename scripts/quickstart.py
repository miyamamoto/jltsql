#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""JLTSQL Quick Start Script - Claude Code風のモダンなUI

このスクリプトはJLTSQLの完全自動セットアップを実行します：
1. プロジェクト初期化
2. テーブル・インデックス作成
3. すべてのデータ取得（蓄積系データ）
4. リアルタイム監視の開始（オプション）
"""

import argparse
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.table import Table
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from src.utils.lock_manager import ProcessLock, ProcessLockError


console = Console() if RICH_AVAILABLE else None


def interactive_setup() -> dict:
    """対話形式で設定を収集"""
    if RICH_AVAILABLE:
        return _interactive_setup_rich()
    else:
        return _interactive_setup_simple()


def _check_service_key() -> tuple[bool, str]:
    """サービスキーの設定状況を確認"""
    import os

    # 環境変数をチェック
    env_key = os.environ.get("JVLINK_SERVICE_KEY", "")
    if env_key and len(env_key) >= 10:
        return True, env_key

    # config.yamlをチェック
    config_path = project_root / "config" / "config.yaml"
    if config_path.exists():
        try:
            import yaml
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            key = config.get("jvlink", {}).get("service_key", "")
            if key and not key.startswith("${") and len(key) >= 10:
                return True, key
        except Exception:
            pass

    return False, ""


def _save_service_key(service_key: str) -> bool:
    """サービスキーをconfig.yamlに保存"""
    import yaml

    config_dir = project_root / "config"
    config_dir.mkdir(exist_ok=True)

    config_path = config_dir / "config.yaml"

    # 既存の設定を読み込む
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
        except Exception:
            config = {}
    else:
        config = {}

    # jvlinkセクションを更新
    if "jvlink" not in config:
        config["jvlink"] = {}
    config["jvlink"]["service_key"] = service_key

    # databasesセクションがなければデフォルトを追加
    if "databases" not in config:
        config["databases"] = {
            "sqlite": {
                "enabled": True,
                "path": "./data/keiba.db",
            }
        }

    # 保存
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        return True
    except Exception:
        return False


def _interactive_setup_rich() -> dict:
    """Rich UIで対話形式設定"""
    console.clear()
    console.print()
    console.print(Panel(
        "[bold]JRA-VAN DataLab -> SQLite[/bold]\n"
        "[dim]競馬データベース自動セットアップ[/dim]",
        title="[bold blue]JLTSQL[/bold blue]",
        border_style="blue",
        padding=(1, 2),
    ))
    console.print()

    settings = {}

    # サービスキーの確認
    console.print("[bold]0. JV-Link サービスキー[/bold]")
    console.print("[dim]JRA-VAN DataLab会員のサービスキーが必要です[/dim]")
    console.print()

    has_key, existing_key = _check_service_key()

    if has_key:
        masked_key = existing_key[:4] + "-****-****-****-" + existing_key[-1]
        console.print(f"  [green]OK[/green] サービスキー設定済み: {masked_key}")
        console.print()
    else:
        console.print("  [yellow]未設定[/yellow] サービスキーが設定されていません")
        console.print()
        console.print("[dim]サービスキーは JRA-VAN DataLab 会員ページで確認できます[/dim]")
        console.print("[dim]https://jra-van.jp/dlb/[/dim]")
        console.print()

        service_key = Prompt.ask("サービスキーを入力 (例: XXXX-XXXX-XXXX-XXXX-X)")

        if service_key and len(service_key) >= 10:
            if _save_service_key(service_key):
                console.print("  [green]OK[/green] サービスキーを保存しました")
            else:
                console.print("  [red]NG[/red] 保存に失敗しました")
                console.print("[yellow]環境変数 JVLINK_SERVICE_KEY に設定してください[/yellow]")
        else:
            console.print("[red]サービスキーが無効です。セットアップを中止します。[/red]")
            sys.exit(1)

        console.print()

    # データ収集期間の選択
    console.print("[bold]1. データ収集期間[/bold]")
    console.print()

    period_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    period_table.add_column("No", style="cyan", width=4)
    period_table.add_column("Option")
    period_table.add_column("Description", style="dim")

    period_table.add_row("1", "過去1年間", "直近のデータのみ（高速）")
    period_table.add_row("2", "過去5年間", "中期分析向け")
    period_table.add_row("3", "過去10年間", "[yellow]推奨[/yellow]")
    period_table.add_row("4", "過去20年間", "長期分析向け")
    period_table.add_row("5", "全データ", "1986年以降すべて（時間がかかります）")

    console.print(period_table)
    console.print()

    choice = Prompt.ask(
        "選択",
        choices=["1", "2", "3", "4", "5"],
        default="3"
    )

    today = datetime.now()
    if choice == "1":
        settings['years'] = 1
        settings['from_date'] = (today - timedelta(days=365)).strftime("%Y%m%d")
    elif choice == "2":
        settings['years'] = 5
        settings['from_date'] = (today - timedelta(days=365 * 5)).strftime("%Y%m%d")
    elif choice == "3":
        settings['years'] = 10
        settings['from_date'] = (today - timedelta(days=365 * 10)).strftime("%Y%m%d")
    elif choice == "4":
        settings['years'] = 20
        settings['from_date'] = (today - timedelta(days=365 * 20)).strftime("%Y%m%d")
    else:  # 5: 全データ
        settings['years'] = None
        settings['from_date'] = "19860101"

    settings['to_date'] = today.strftime("%Y%m%d")
    console.print()

    # オッズデータ
    console.print("[bold]2. オッズデータ[/bold]")
    console.print("[dim]オッズデータは容量が大きいため、除外することもできます[/dim]")
    console.print()
    settings['no_odds'] = not Confirm.ask("オッズデータを取得しますか？", default=True)
    console.print()

    # リアルタイム監視
    console.print("[bold]3. リアルタイム監視[/bold]")
    console.print("[dim]開催日にリアルタイムでデータを取得するデーモンプロセス[/dim]")
    console.print()
    settings['no_monitor'] = not Confirm.ask("リアルタイム監視を開始しますか？", default=False)
    console.print()

    # 確認
    console.print(Panel("[bold]設定確認[/bold]", border_style="blue"))

    confirm_table = Table(show_header=False, box=None, padding=(0, 1))
    confirm_table.add_column("Key", style="dim")
    confirm_table.add_column("Value", style="white")

    if settings['years']:
        confirm_table.add_row("期間", f"過去{settings['years']}年間")
    else:
        confirm_table.add_row("期間", "全データ (1986年～)")
    confirm_table.add_row("開始日", settings['from_date'])
    confirm_table.add_row("終了日", settings['to_date'])
    confirm_table.add_row("オッズ", "[red]除外[/red]" if settings['no_odds'] else "[green]取得[/green]")
    confirm_table.add_row("監視", "[green]開始[/green]" if not settings['no_monitor'] else "[yellow]なし[/yellow]")

    console.print(confirm_table)
    console.print()

    if not Confirm.ask("[bold]この設定でセットアップを開始しますか？[/bold]", default=True):
        console.print("[yellow]キャンセルしました[/yellow]")
        sys.exit(0)

    return settings


def _interactive_setup_simple() -> dict:
    """シンプルな対話形式設定"""
    print("=" * 60)
    print("JLTSQL セットアップ")
    print("=" * 60)
    print()

    settings = {}

    # サービスキーの確認
    print("0. JV-Link サービスキー")
    print()

    has_key, existing_key = _check_service_key()

    if has_key:
        masked_key = existing_key[:4] + "-****-****-****-" + existing_key[-1]
        print(f"  [OK] サービスキー設定済み: {masked_key}")
    else:
        print("  [未設定] サービスキーが設定されていません")
        print()
        print("  サービスキーは JRA-VAN DataLab 会員ページで確認できます")
        print("  https://jra-van.jp/dlb/")
        print()
        service_key = input("サービスキーを入力: ").strip()

        if service_key and len(service_key) >= 10:
            if _save_service_key(service_key):
                print("  [OK] サービスキーを保存しました")
            else:
                print("  [NG] 保存に失敗しました")
        else:
            print("[NG] サービスキーが無効です。セットアップを中止します。")
            sys.exit(1)

    print()

    # データ収集期間
    print("1. データ収集期間を選択してください:")
    print("   1) 過去1年間")
    print("   2) 過去5年間")
    print("   3) 過去10年間 (推奨)")
    print("   4) 過去20年間")
    print("   5) 全データ (1986年～)")
    print()

    choice = input("選択 [3]: ").strip() or "3"

    today = datetime.now()
    if choice == "1":
        settings['years'] = 1
        settings['from_date'] = (today - timedelta(days=365)).strftime("%Y%m%d")
    elif choice == "2":
        settings['years'] = 5
        settings['from_date'] = (today - timedelta(days=365 * 5)).strftime("%Y%m%d")
    elif choice == "4":
        settings['years'] = 20
        settings['from_date'] = (today - timedelta(days=365 * 20)).strftime("%Y%m%d")
    elif choice == "5":
        settings['years'] = None
        settings['from_date'] = "19860101"
    else:
        settings['years'] = 10
        settings['from_date'] = (today - timedelta(days=365 * 10)).strftime("%Y%m%d")

    settings['to_date'] = today.strftime("%Y%m%d")
    print()

    # オッズデータ
    print("2. オッズデータを取得しますか？ [Y/n]: ", end="")
    odds_choice = input().strip().lower()
    settings['no_odds'] = odds_choice in ('n', 'no')
    print()

    # リアルタイム監視
    print("3. リアルタイム監視を開始しますか？ [y/N]: ", end="")
    monitor_choice = input().strip().lower()
    settings['no_monitor'] = monitor_choice not in ('y', 'yes')
    print()

    # 確認
    print("-" * 60)
    print("設定確認:")
    if settings['years']:
        print(f"  期間: 過去{settings['years']}年間")
    else:
        print("  期間: 全データ (1986年～)")
    print(f"  開始日: {settings['from_date']}")
    print(f"  終了日: {settings['to_date']}")
    print(f"  オッズ: {'除外' if settings['no_odds'] else '取得'}")
    print(f"  監視: {'開始' if not settings['no_monitor'] else 'なし'}")
    print("-" * 60)
    print()

    confirm = input("この設定でセットアップを開始しますか？ [Y/n]: ").strip().lower()
    if confirm in ('n', 'no'):
        print("キャンセルしました")
        sys.exit(0)

    return settings


class QuickstartRunner:
    """完全自動セットアップ実行クラス（Claude Code風UI）"""

    # すべてのデータスペック（優先順位順）
    DATA_SPECS = [
        ("DIFN", "マスタ情報", 1),
        ("BLDN", "血統情報", 1),
        ("RACE", "レース情報", 1),
        ("YSCH", "開催スケジュール", 1),
        ("TOKU", "特別登録", 1),
        ("JGDW", "重賞情報", 1),
        ("HOSN", "市場取引", 2),
        ("COMM", "各種解説", 2),
        ("SNPN", "速報情報", 2),
        ("0B11", "データマイニング", 2),
        ("0B20", "成績", 2),
        ("0B31", "払戻", 2),
        ("0B41", "繁殖牝馬", 1),
    ]

    # オッズデータスペック
    ODDS_SPECS = [
        ("SLOP", "単勝・複勝オッズ", 2),
        ("HOYU", "馬連・ワイドオッズ", 2),
        ("O4", "枠連オッズ", 2),
        ("O5", "馬単オッズ", 2),
        ("O6", "3連複・3連単オッズ", 2),
        ("WOOD", "調教データ", 2),
        ("MING", "当日発表", 2),
    ]

    def __init__(self, settings: dict):
        self.settings = settings
        self.project_root = Path(__file__).parent.parent
        self.errors = []
        self.warnings = []
        self.stats = {
            'specs_success': 0,
            'specs_failed': 0,
        }

    def run(self) -> int:
        """完全自動セットアップ実行"""
        if RICH_AVAILABLE:
            return self._run_rich()
        else:
            return self._run_simple()

    def _run_rich(self) -> int:
        """Rich UIで実行"""
        console.print()

        # 実行
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:

            # 1. 前提条件チェック
            task = progress.add_task("[cyan]前提条件チェック...", total=1)
            if not self._check_prerequisites_rich():
                progress.update(task, completed=1)
                self._print_summary_rich(success=False)
                return 1
            progress.update(task, completed=1)

            # 2. プロジェクト初期化
            task = progress.add_task("[cyan]初期化中...", total=1)
            if not self._run_init():
                progress.update(task, completed=1)
                self._print_summary_rich(success=False)
                return 1
            progress.update(task, completed=1)

            # 3. テーブル作成
            task = progress.add_task("[cyan]テーブル作成中...", total=1)
            if not self._run_create_tables():
                progress.update(task, completed=1)
                self._print_summary_rich(success=False)
                return 1
            progress.update(task, completed=1)

            # 4. インデックス作成
            task = progress.add_task("[cyan]インデックス作成中...", total=1)
            if not self._run_create_indexes():
                progress.update(task, completed=1)
                self._print_summary_rich(success=False)
                return 1
            progress.update(task, completed=1)

        # 5. データ取得（別のProgressで表示）
        if not self._run_fetch_all_rich():
            self._print_summary_rich(success=False)
            return 1

        # 6. リアルタイム監視
        if not self.settings.get('no_monitor', True):
            console.print()
            with console.status("[cyan]リアルタイム監視を開始中...", spinner="dots"):
                if not self._run_monitor():
                    self.warnings.append("リアルタイム監視の起動に失敗")

        # 完了
        self._print_summary_rich(success=True)
        return 0

    def _check_prerequisites_rich(self) -> bool:
        """前提条件チェック（Rich版）"""
        has_error = False
        checks = []

        # Python バージョン
        python_version = sys.version_info
        if python_version >= (3, 10):
            checks.append(("Python", f"{python_version.major}.{python_version.minor}", True))
        else:
            checks.append(("Python", f"{python_version.major}.{python_version.minor} (要3.10+)", False))
            has_error = True

        # OS
        if sys.platform == "win32":
            checks.append(("OS", "Windows", True))
        else:
            checks.append(("OS", f"{sys.platform} (要Windows)", False))
            has_error = True

        # JV-Link
        try:
            import win32com.client
            win32com.client.Dispatch("JVDTLab.JVLink")
            checks.append(("JV-Link", "OK", True))
        except Exception:
            checks.append(("JV-Link", "未インストール", False))
            has_error = True

        # 結果表示
        for name, value, ok in checks:
            status = "[green]OK[/green]" if ok else "[red]NG[/red]"
            console.print(f"  [{status}] {name}: {value}")

        return not has_error

    def _run_fetch_all_rich(self) -> bool:
        """データ取得（Rich UI）"""
        specs_to_fetch = self.DATA_SPECS.copy()
        if not self.settings.get('no_odds', False):
            specs_to_fetch.extend(self.ODDS_SPECS)

        total_specs = len(specs_to_fetch)

        console.print()
        console.print(Panel(
            f"[bold]データ取得[/bold] ({total_specs}スペック)",
            border_style="blue",
        ))

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:

            main_task = progress.add_task(
                "[cyan]データ取得中...",
                total=total_specs
            )

            for idx, (spec, description, option) in enumerate(specs_to_fetch, 1):
                progress.update(
                    main_task,
                    description=f"[cyan]{spec}: {description}"
                )

                success = self._fetch_single_spec(spec, option)

                if success:
                    self.stats['specs_success'] += 1
                else:
                    self.stats['specs_failed'] += 1

                progress.update(main_task, advance=1)
                time.sleep(0.5)

        return self.stats['specs_success'] > 0

    def _print_summary_rich(self, success: bool):
        """サマリー出力（Rich版）"""
        console.print()

        if success:
            console.print(Panel(
                "[bold green]セットアップ完了！[/bold green]",
                border_style="green",
            ))

            # 統計
            if self.stats['specs_success'] > 0:
                stats_table = Table(show_header=False, box=None)
                stats_table.add_column("", style="dim")
                stats_table.add_column("")
                stats_table.add_row("成功", f"[green]{self.stats['specs_success']}[/green]")
                stats_table.add_row("失敗", f"[red]{self.stats['specs_failed']}[/red]")
                console.print(stats_table)

            # 次のステップ
            console.print()
            console.print("[dim]次のステップ:[/dim]")
            console.print("  [cyan]jltsql status[/cyan]    - ステータス確認")
            console.print("  [cyan]jltsql export[/cyan]    - データエクスポート")
            if not self.settings.get('no_monitor', True):
                console.print("  [cyan]jltsql monitor --stop[/cyan] - 監視停止")
        else:
            console.print(Panel(
                "[bold red]セットアップ失敗[/bold red]",
                border_style="red",
            ))

            if self.errors:
                console.print()
                console.print("[red]エラー:[/red]")
                for error in self.errors[:5]:
                    safe_error = str(error)[:80]
                    console.print(f"  [dim]•[/dim] {safe_error}")

        console.print()

    # === シンプル版（richなしの場合）===

    def _run_simple(self) -> int:
        """シンプルなテキストUIで実行"""
        print()

        # 1. 前提条件
        print("[1/5] 前提条件チェック...")
        if not self._check_prerequisites_simple():
            return 1

        # 2. 初期化
        print("\n[2/5] 初期化中...")
        if not self._run_init():
            return 1
        print("  OK")

        # 3. テーブル作成
        print("\n[3/5] テーブル作成中...")
        if not self._run_create_tables():
            return 1
        print("  OK")

        # 4. インデックス作成
        print("\n[4/5] インデックス作成中...")
        if not self._run_create_indexes():
            return 1
        print("  OK")

        # 5. データ取得
        print("\n[5/5] データ取得中...")
        if not self._run_fetch_all_simple():
            return 1

        # 6. 監視
        if not self.settings.get('no_monitor', True):
            print("\nリアルタイム監視を開始中...")
            self._run_monitor()

        print("\n" + "=" * 60)
        print("セットアップ完了！")
        print("=" * 60)
        return 0

    def _check_prerequisites_simple(self) -> bool:
        """前提条件チェック（シンプル版）"""
        has_error = False

        v = sys.version_info
        if v >= (3, 10):
            print(f"  [OK] Python {v.major}.{v.minor}")
        else:
            print(f"  [NG] Python {v.major}.{v.minor} (3.10以上が必要)")
            has_error = True

        if sys.platform == "win32":
            print("  [OK] Windows")
        else:
            print(f"  [NG] {sys.platform} (Windowsが必要)")
            has_error = True

        try:
            import win32com.client
            win32com.client.Dispatch("JVDTLab.JVLink")
            print("  [OK] JV-Link")
        except Exception:
            print("  [NG] JV-Link (未インストール)")
            has_error = True

        return not has_error

    def _run_fetch_all_simple(self) -> bool:
        """データ取得（シンプル版）"""
        specs = self.DATA_SPECS.copy()
        if not self.settings.get('no_odds', False):
            specs.extend(self.ODDS_SPECS)

        total = len(specs)
        for idx, (spec, desc, option) in enumerate(specs, 1):
            print(f"  [{idx}/{total}] {spec}: {desc}...", end=" ", flush=True)

            if self._fetch_single_spec(spec, option):
                self.stats['specs_success'] += 1
                print("OK")
            else:
                self.stats['specs_failed'] += 1
                print("SKIP")

            time.sleep(0.5)

        print(f"\n  完了: {self.stats['specs_success']}/{total}")
        return self.stats['specs_success'] > 0

    # === 共通処理 ===

    def _run_init(self) -> bool:
        """プロジェクト初期化"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli.main", "init"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30,
            )
            if result.returncode != 0:
                self.errors.append(f"初期化失敗: {result.stderr}")
            return result.returncode == 0
        except Exception as e:
            self.errors.append(f"初期化エラー: {e}")
            return False

    def _run_create_tables(self) -> bool:
        """テーブル作成"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli.main", "create-tables"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=60,
            )
            if result.returncode != 0:
                self.errors.append(f"テーブル作成失敗: {result.stderr}")
            return result.returncode == 0
        except Exception as e:
            self.errors.append(f"テーブル作成エラー: {e}")
            return False

    def _run_create_indexes(self) -> bool:
        """インデックス作成"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli.main", "create-indexes"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=120,
            )
            if result.returncode != 0:
                self.errors.append(f"インデックス作成失敗: {result.stderr}")
            return result.returncode == 0
        except Exception as e:
            self.errors.append(f"インデックス作成エラー: {e}")
            return False

    def _fetch_single_spec(self, spec: str, option: int) -> bool:
        """単一データスペック取得"""
        try:
            cmd = [
                sys.executable, "-m", "src.cli.main", "fetch",
                "--from", self.settings['from_date'],
                "--to", self.settings['to_date'],
                "--spec", spec,
                "--option", str(option),
            ]
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=600,
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            self.errors.append(f"{spec}: タイムアウト")
            return False
        except Exception as e:
            self.errors.append(f"{spec}: {str(e)[:100]}")
            return False

    def _run_monitor(self) -> bool:
        """リアルタイム監視開始"""
        try:
            cmd = [sys.executable, "-m", "src.cli.main", "monitor", "--daemon"]
            result = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(2)
            return result.poll() is None
        except Exception:
            return False


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="JLTSQL セットアップ",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--years", type=int, default=None, help="過去N年間")
    parser.add_argument("--from", dest="from_date", default=None, help="開始日 (YYYYMMDD)")
    parser.add_argument("--to", dest="to_date", default=None, help="終了日 (YYYYMMDD)")
    parser.add_argument("--all", action="store_true", help="全データ (1986年～)")
    parser.add_argument("--no-odds", action="store_true", help="オッズ除外")
    parser.add_argument("--no-monitor", action="store_true", help="監視なし")
    parser.add_argument("--monitor", action="store_true", help="監視開始")
    parser.add_argument("-y", "--yes", action="store_true", help="確認スキップ（非対話モード）")
    parser.add_argument("-i", "--interactive", action="store_true", help="対話モード（デフォルト）")

    args = parser.parse_args()

    # 対話モードかどうかを判定
    # コマンドライン引数が指定されていなければ対話モード
    use_interactive = args.interactive or (
        args.years is None and
        args.from_date is None and
        not args.all and
        not args.yes
    )

    if use_interactive:
        # 対話形式で設定を収集
        settings = interactive_setup()
    else:
        # コマンドライン引数から設定を構築
        settings = {}
        today = datetime.now()

        if args.all:
            settings['years'] = None
            settings['from_date'] = "19860101"
        elif args.from_date:
            settings['from_date'] = args.from_date
            settings['years'] = None
        else:
            years = args.years or 10
            settings['years'] = years
            settings['from_date'] = (today - timedelta(days=365 * years)).strftime("%Y%m%d")

        settings['to_date'] = args.to_date or today.strftime("%Y%m%d")
        settings['no_odds'] = args.no_odds
        settings['no_monitor'] = not args.monitor if args.monitor else args.no_monitor

        # 日付検証
        try:
            datetime.strptime(settings['from_date'], "%Y%m%d")
            datetime.strptime(settings['to_date'], "%Y%m%d")
        except ValueError:
            parser.error("日付は YYYYMMDD 形式で指定してください")

    # 実行
    try:
        with ProcessLock("quickstart"):
            runner = QuickstartRunner(settings)
            sys.exit(runner.run())
    except ProcessLockError as e:
        if RICH_AVAILABLE:
            console.print(f"[red]エラー: {e}[/red]")
        else:
            print(f"エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
