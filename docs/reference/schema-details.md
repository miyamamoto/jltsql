# スキーマ詳細

JRVLTSQLが管理する64テーブルの詳細なスキーマ定義です。

## データ型について

| 型 | 用途 | 例 |
|----|------|-----|
| INTEGER | 年、月日、回次、日次、レース番号、馬番、距離、頭数、着順 | Year, MonthDay, RaceNum |
| BIGINT | 賞金額（大きな数値） | HonSyokinTotal, Price |
| REAL | オッズ、タイム、ハロンタイム | Odds, Time |
| TEXT | コード（固定長）、日付、名前、その他 | JyoCD, Bamei |

## 共通フィールド

多くのテーブルで使用される共通フィールド：

| フィールド | 型 | 説明 |
|-----------|-----|------|
| RecordSpec | TEXT | レコード種別（RA, SE, HR等） |
| DataKubun | TEXT | データ区分（1=通常、2=訂正、3=削除） |
| MakeDate | TEXT | データ作成日（YYYYMMDD） |
| Year | INTEGER | 開催年（4桁） |
| MonthDay | INTEGER | 月日（MMDD形式、例：601=6月1日） |
| JyoCD | TEXT | 競馬場コード（01-10） |
| Kaiji | INTEGER | 回次（その競馬場の何回目の開催か） |
| Nichiji | INTEGER | 日次（その回の何日目か） |
| RaceNum | INTEGER | レース番号（1-12） |

## 競馬場コード

| コード | 競馬場 |
|--------|--------|
| 01 | 札幌 |
| 02 | 函館 |
| 03 | 福島 |
| 04 | 新潟 |
| 05 | 東京 |
| 06 | 中山 |
| 07 | 中京 |
| 08 | 京都 |
| 09 | 阪神 |
| 10 | 小倉 |

---

## NL_RA（レース詳細情報）

レースの基本情報を格納するテーブル。

**PRIMARY KEY**: `(Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum)`

| カラム | 型 | 説明 |
|--------|-----|------|
| RecordSpec | TEXT | レコード種別（RA） |
| DataKubun | TEXT | データ区分 |
| MakeDate | TEXT | データ作成日 |
| Year | INTEGER | 開催年 |
| MonthDay | INTEGER | 月日 |
| JyoCD | TEXT | 競馬場コード |
| Kaiji | INTEGER | 回次 |
| Nichiji | INTEGER | 日次 |
| RaceNum | INTEGER | レース番号 |
| YoubiCD | TEXT | 曜日コード（0=日〜6=土） |
| TokuNum | INTEGER | 特別競走番号 |
| Hondai | TEXT | レース名本題 |
| Fukudai | TEXT | レース名副題 |
| Kakko | TEXT | レース名かっこ内 |
| HondaiEng | TEXT | レース名（英語） |
| FukudaiEng | TEXT | 副題（英語） |
| KakkoEng | TEXT | かっこ内（英語） |
| Ryakusyo10 | TEXT | 略称10文字 |
| Ryakusyo6 | TEXT | 略称6文字 |
| Ryakusyo3 | TEXT | 略称3文字 |
| Kubun | TEXT | 競走区分 |
| Nkai | INTEGER | 第何回 |
| GradeCD | TEXT | グレードコード |
| GradeCDSub | TEXT | グレード補助コード |
| JyokenCD1-5 | TEXT | 競走条件コード |
| Kyori | INTEGER | 距離（メートル） |
| TrackCD | TEXT | トラックコード |
| CourseKubunCD | TEXT | コース区分 |
| SyubetuCD | TEXT | 競走種別コード |
| KigoCD | TEXT | 競走記号コード |
| JyuryoCD | TEXT | 重量種別コード |
| TorokuTosu | INTEGER | 登録頭数 |
| SyussoTosu | INTEGER | 出走頭数 |
| NyusenTosu | INTEGER | 入線頭数 |
| HassoTime | TEXT | 発走時刻（HHMM） |
| TenkoBaba | TEXT | 天候馬場コード |
| LapTime1-25 | REAL | ラップタイム（1-25ハロン） |
| SyogaiMileTime | REAL | 障害マイルタイム |
| Haron1-4 | REAL | ハロンタイム（上がり1-4） |
| Corner1-4 | TEXT | コーナー通過順 |
| RecordUpKubun | TEXT | レコード更新区分 |

---

## NL_SE（馬毎レース情報）

各レースにおける各馬の出走情報・成績を格納。

**PRIMARY KEY**: `(Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum, Umaban)`

| カラム | 型 | 説明 |
|--------|-----|------|
| RecordSpec | TEXT | レコード種別（SE） |
| DataKubun | TEXT | データ区分 |
| MakeDate | TEXT | データ作成日 |
| Year | INTEGER | 開催年 |
| MonthDay | INTEGER | 月日 |
| JyoCD | TEXT | 競馬場コード |
| Kaiji | INTEGER | 回次 |
| Nichiji | INTEGER | 日次 |
| RaceNum | INTEGER | レース番号 |
| Wakuban | INTEGER | 枠番（1-8） |
| Umaban | INTEGER | 馬番 |
| KettoNum | TEXT | 血統登録番号（10桁） |
| Bamei | TEXT | 馬名 |
| UmaKigoCD | TEXT | 馬記号コード |
| SexCD | TEXT | 性別（1=牡、2=牝、3=セン） |
| KeiroCD | TEXT | 毛色コード |
| Barei | INTEGER | 馬齢 |
| TozaiCD | TEXT | 東西コード（1=関東、2=関西） |
| ChokyosiCode | TEXT | 調教師コード |
| ChokyosiRyakusyo | TEXT | 調教師略称 |
| BanusiCode | TEXT | 馬主コード |
| BanusiName | TEXT | 馬主名 |
| Fukusyoku | TEXT | 服色 |
| Futan | REAL | 負担重量（kg） |
| Blinker | TEXT | ブリンカー有無 |
| KisyuCode | TEXT | 騎手コード |
| KisyuName | TEXT | 騎手名 |
| KisyuRyakusyo | TEXT | 騎手略称 |
| MinaraiCD | TEXT | 見習い区分 |
| Bataiju | INTEGER | 馬体重（kg） |
| ZogenFugo | TEXT | 増減符号（+/-） |
| ZogenSa | INTEGER | 増減差（kg） |
| Odds | REAL | 単勝オッズ |
| Ninki | INTEGER | 人気順 |
| KakuteiJyuni | INTEGER | 確定着順 |
| DochakuKubun | TEXT | 同着区分 |
| DochakuTosu | INTEGER | 同着頭数 |
| Time | REAL | 走破タイム（秒） |
| Chakusa1-3 | TEXT | 着差（1-3着との差） |
| TimeDiff | REAL | タイム差 |
| Corner1-4Jyuni | INTEGER | コーナー通過順（1-4） |
| Jyuni1c-4c | INTEGER | コーナー1-4位置取り |
| HaronTimeL3 | REAL | 上がり3ハロンタイム |
| SyokinInfo | TEXT | 賞金情報 |

---

## NL_HR（払戻情報）

各レースの払戻金情報を格納。

**PRIMARY KEY**: `(Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum)`

| カラム | 型 | 説明 |
|--------|-----|------|
| RecordSpec | TEXT | レコード種別（HR） |
| Year | INTEGER | 開催年 |
| MonthDay | INTEGER | 月日 |
| JyoCD | TEXT | 競馬場コード |
| Kaiji | INTEGER | 回次 |
| Nichiji | INTEGER | 日次 |
| RaceNum | INTEGER | レース番号 |
| TorokuTosu | INTEGER | 登録頭数 |
| SyussoTosu | INTEGER | 出走頭数 |
| FuseirituFlag1-8 | TEXT | 不成立フラグ（各式別） |
| TokubaraiFlag1-8 | TEXT | 特払いフラグ |
| HenkanFlag1-8 | TEXT | 返還フラグ |
| HenkanDoWaku1-8 | TEXT | 返還同枠番 |
| TansyoUmaban1-3 | TEXT | 単勝馬番 |
| TansyoPay1-3 | BIGINT | 単勝払戻金 |
| TansyoNinki1-3 | INTEGER | 単勝人気 |
| FukusyoUmaban1-5 | TEXT | 複勝馬番 |
| FukusyoPay1-5 | BIGINT | 複勝払戻金 |
| FukusyoNinki1-5 | INTEGER | 複勝人気 |
| WakurenKumi1-3 | TEXT | 枠連組番 |
| WakurenPay1-3 | BIGINT | 枠連払戻金 |
| WakurenNinki1-3 | INTEGER | 枠連人気 |
| UmarenKumi1-3 | TEXT | 馬連組番 |
| UmarenPay1-3 | BIGINT | 馬連払戻金 |
| UmarenNinki1-3 | INTEGER | 馬連人気 |
| WideKumi1-7 | TEXT | ワイド組番 |
| WidePay1-7 | BIGINT | ワイド払戻金 |
| WideNinki1-7 | INTEGER | ワイド人気 |
| UmatanKumi1-6 | TEXT | 馬単組番 |
| UmatanPay1-6 | BIGINT | 馬単払戻金 |
| UmatanNinki1-6 | INTEGER | 馬単人気 |
| SanrenpukuKumi1-3 | TEXT | 三連複組番 |
| SanrenpukuPay1-3 | BIGINT | 三連複払戻金 |
| SanrenpukuNinki1-3 | INTEGER | 三連複人気 |

---

## NL_H6（三連単払戻）

三連単の払戻情報（組み合わせが多いため別テーブル）。

**PRIMARY KEY**: `(Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum, SanrentanKumi)`

| カラム | 型 | 説明 |
|--------|-----|------|
| Year | INTEGER | 開催年 |
| MonthDay | INTEGER | 月日 |
| JyoCD | TEXT | 競馬場コード |
| Kaiji | INTEGER | 回次 |
| Nichiji | INTEGER | 日次 |
| RaceNum | INTEGER | レース番号 |
| SanrentanKumi | TEXT | 三連単組番 |
| SanrentanPay | BIGINT | 三連単払戻金 |
| SanrentanNinki | INTEGER | 三連単人気 |

---

## NL_UM（馬マスタ）

競走馬の基本情報マスタ。

**PRIMARY KEY**: `(KettoNum)`

| カラム | 型 | 説明 |
|--------|-----|------|
| RecordSpec | TEXT | レコード種別（UM） |
| DataKubun | TEXT | データ区分 |
| MakeDate | TEXT | データ作成日 |
| KettoNum | TEXT | 血統登録番号（10桁） |
| DelKubun | TEXT | 抹消区分 |
| RegDate | TEXT | 登録日 |
| DelDate | TEXT | 抹消日 |
| BirthDate | TEXT | 生年月日 |
| Bamei | TEXT | 馬名 |
| BameiKana | TEXT | 馬名カナ |
| BameiEng | TEXT | 馬名英語 |
| ZaikyuFlag | TEXT | 在厩フラグ |
| SexCD | TEXT | 性別コード |
| KeiroCD | TEXT | 毛色コード |
| Ketto3Info | TEXT | 3代血統情報 |
| TozaiCD | TEXT | 東西所属 |
| ChokyosiCode | TEXT | 調教師コード |
| ChokyosiRyakusyo | TEXT | 調教師略称 |
| BanusiCode | TEXT | 馬主コード |
| BanusiName | TEXT | 馬主名 |
| BreederCode | TEXT | 生産者コード |
| BreederName | TEXT | 生産者名 |
| SanchiName | TEXT | 産地名 |
| RuikeiHonsyokin | BIGINT | 累計本賞金 |
| RuikeiFukasyokin | BIGINT | 累計付加賞金 |
| RuikeiSyutokuSyokin | BIGINT | 累計収得賞金 |
| ChakuSogo | TEXT | 着回数総合 |
| ChakuChuo | TEXT | 着回数中央 |

---

## NL_KS（騎手マスタ）

騎手の基本情報マスタ。

**PRIMARY KEY**: `(KisyuCode)`

| カラム | 型 | 説明 |
|--------|-----|------|
| RecordSpec | TEXT | レコード種別（KS） |
| DataKubun | TEXT | データ区分 |
| MakeDate | TEXT | データ作成日 |
| KisyuCode | TEXT | 騎手コード（5桁） |
| DelKubun | TEXT | 抹消区分 |
| IssueDate | TEXT | 免許交付年月日 |
| DelDate | TEXT | 登録抹消年月日 |
| BirthDate | TEXT | 生年月日 |
| KisyuName | TEXT | 騎手名 |
| KisyuNameKana | TEXT | 騎手名カナ |
| KisyuNameEng | TEXT | 騎手名英語 |
| KisyuRyakusyo | TEXT | 騎手略称 |
| SexCD | TEXT | 性別 |
| SikakuCD | TEXT | 騎手資格コード |
| MinaraiCD | TEXT | 見習区分 |
| TozaiCD | TEXT | 東西所属 |
| Syozoku | TEXT | 所属（厩舎） |
| SyozokuCode | TEXT | 所属コード |
| HonSyokinTotal | BIGINT | 本賞金累計 |
| FukaSyokin | BIGINT | 付加賞金累計 |
| ChakuKaisu | TEXT | 着回数 |
| SyutokuSyokin | BIGINT | 収得賞金累計 |

---

## NL_CH（調教師マスタ）

調教師の基本情報マスタ。

**PRIMARY KEY**: `(ChokyosiCode)`

| カラム | 型 | 説明 |
|--------|-----|------|
| RecordSpec | TEXT | レコード種別（CH） |
| DataKubun | TEXT | データ区分 |
| MakeDate | TEXT | データ作成日 |
| ChokyosiCode | TEXT | 調教師コード（5桁） |
| DelKubun | TEXT | 抹消区分 |
| IssueDate | TEXT | 免許交付年月日 |
| DelDate | TEXT | 登録抹消年月日 |
| BirthDate | TEXT | 生年月日 |
| ChokyosiName | TEXT | 調教師名 |
| ChokyosiNameKana | TEXT | 調教師名カナ |
| ChokyosiNameEng | TEXT | 調教師名英語 |
| ChokyosiRyakusyo | TEXT | 調教師略称 |
| SexCD | TEXT | 性別 |
| TozaiCD | TEXT | 東西所属 |
| Syozoku | TEXT | 所属 |
| HonSyokinTotal | BIGINT | 本賞金累計 |
| FukaSyokin | BIGINT | 付加賞金累計 |
| ChakuKaisu | TEXT | 着回数 |
| SyutokuSyokin | BIGINT | 収得賞金累計 |

---

## NL_O1（単勝・複勝オッズ）

単勝・複勝オッズを格納。

**PRIMARY KEY**: `(Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum, Umaban)`

| カラム | 型 | 説明 |
|--------|-----|------|
| RecordSpec | TEXT | レコード種別（O1） |
| Year | INTEGER | 開催年 |
| MonthDay | INTEGER | 月日 |
| JyoCD | TEXT | 競馬場コード |
| Kaiji | INTEGER | 回次 |
| Nichiji | INTEGER | 日次 |
| RaceNum | INTEGER | レース番号 |
| Umaban | INTEGER | 馬番 |
| TansyoOdds | REAL | 単勝オッズ |
| FukusyoOddsLow | REAL | 複勝オッズ（下限） |
| FukusyoOddsHigh | REAL | 複勝オッズ（上限） |

---

## NL_O2（馬連オッズ）

馬連オッズを格納。

**PRIMARY KEY**: `(Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum, Kumi)`

| カラム | 型 | 説明 |
|--------|-----|------|
| Year | INTEGER | 開催年 |
| MonthDay | INTEGER | 月日 |
| JyoCD | TEXT | 競馬場コード |
| Kaiji | INTEGER | 回次 |
| Nichiji | INTEGER | 日次 |
| RaceNum | INTEGER | レース番号 |
| Kumi | TEXT | 組番（例：01-02） |
| UmarenOdds | REAL | 馬連オッズ |

---

## NL_O3（ワイドオッズ）

ワイドオッズを格納。

**PRIMARY KEY**: `(Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum, Kumi)`

| カラム | 型 | 説明 |
|--------|-----|------|
| Year | INTEGER | 開催年 |
| MonthDay | INTEGER | 月日 |
| JyoCD | TEXT | 競馬場コード |
| Kaiji | INTEGER | 回次 |
| Nichiji | INTEGER | 日次 |
| RaceNum | INTEGER | レース番号 |
| Kumi | TEXT | 組番 |
| WideOddsLow | REAL | ワイドオッズ（下限） |
| WideOddsHigh | REAL | ワイドオッズ（上限） |

---

## NL_O4（馬単オッズ）

馬単オッズを格納。

**PRIMARY KEY**: `(Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum, Kumi)`

| カラム | 型 | 説明 |
|--------|-----|------|
| Year | INTEGER | 開催年 |
| MonthDay | INTEGER | 月日 |
| JyoCD | TEXT | 競馬場コード |
| Kaiji | INTEGER | 回次 |
| Nichiji | INTEGER | 日次 |
| RaceNum | INTEGER | レース番号 |
| Kumi | TEXT | 組番（1着-2着の順） |
| UmatanOdds | REAL | 馬単オッズ |

---

## NL_O5（三連複オッズ）

三連複オッズを格納。

**PRIMARY KEY**: `(Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum, Kumi)`

| カラム | 型 | 説明 |
|--------|-----|------|
| Year | INTEGER | 開催年 |
| MonthDay | INTEGER | 月日 |
| JyoCD | TEXT | 競馬場コード |
| Kaiji | INTEGER | 回次 |
| Nichiji | INTEGER | 日次 |
| RaceNum | INTEGER | レース番号 |
| Kumi | TEXT | 組番（3頭） |
| SanrenpukuOdds | REAL | 三連複オッズ |

---

## NL_O6（三連単オッズ）

三連単オッズを格納。

**PRIMARY KEY**: `(Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum, Kumi)`

| カラム | 型 | 説明 |
|--------|-----|------|
| Year | INTEGER | 開催年 |
| MonthDay | INTEGER | 月日 |
| JyoCD | TEXT | 競馬場コード |
| Kaiji | INTEGER | 回次 |
| Nichiji | INTEGER | 日次 |
| RaceNum | INTEGER | レース番号 |
| Kumi | TEXT | 組番（1着-2着-3着の順） |
| SanrentanOdds | REAL | 三連単オッズ |

---

## NL_BN（馬主マスタ）

馬主の基本情報マスタ。

**PRIMARY KEY**: `(BanusiCode)`

| カラム | 型 | 説明 |
|--------|-----|------|
| RecordSpec | TEXT | レコード種別（BN） |
| DataKubun | TEXT | データ区分 |
| MakeDate | TEXT | データ作成日 |
| BanusiCode | TEXT | 馬主コード |
| BanusiName_Co | TEXT | 法人名 |
| BanusiName | TEXT | 馬主名 |
| BanusiNameKana | TEXT | 馬主名カナ |
| BanusiNameEng | TEXT | 馬主名英語 |
| Fukusyoku | TEXT | 服色 |
| SetYear | INTEGER | 初年度 |
| HonSyokinTotal | BIGINT | 本賞金累計 |
| FukaSyokin | BIGINT | 付加賞金累計 |
| ChakuKaisu | INTEGER | 着回数 |

---

## NL_BR（生産者マスタ）

生産者の基本情報マスタ。

**PRIMARY KEY**: `(BreederCode)`

| カラム | 型 | 説明 |
|--------|-----|------|
| RecordSpec | TEXT | レコード種別（BR） |
| DataKubun | TEXT | データ区分 |
| MakeDate | TEXT | データ作成日 |
| BreederCode | TEXT | 生産者コード |
| BreederName_Co | TEXT | 法人名 |
| BreederName | TEXT | 生産者名 |
| BreederNameKana | TEXT | 生産者名カナ |
| BreederNameEng | TEXT | 生産者名英語 |
| Address | TEXT | 住所 |
| SetYear | INTEGER | 初年度 |
| HonSyokinTotal | BIGINT | 本賞金累計 |
| FukaSyokin | BIGINT | 付加賞金累計 |
| ChakuKaisu | INTEGER | 着回数 |

---

## NL_CK（競走馬情報）

各レースにおける競走馬の詳細成績情報。

**PRIMARY KEY**: `(Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum, KettoNum)`

| カラム | 型 | 説明 |
|--------|-----|------|
| Year | INTEGER | 開催年 |
| MonthDay | INTEGER | 月日 |
| JyoCD | TEXT | 競馬場コード |
| Kaiji | INTEGER | 回次 |
| Nichiji | INTEGER | 日次 |
| RaceNum | INTEGER | レース番号 |
| KettoNum | TEXT | 血統登録番号 |
| Bamei | TEXT | 馬名 |
| HeichiHonsyokinTotal | BIGINT | 平地本賞金累計 |
| SyogaiHonsyokinTotal | BIGINT | 障害本賞金累計 |
| TotalChakuCount | INTEGER | 総着回数 |
| ChuoChakuCount | INTEGER | 中央着回数 |
| SibaChoChaku | INTEGER | 芝長距離着 |
| DirtChoChaku | INTEGER | ダート長距離着 |
| KyakusituKeiko | TEXT | 脚質傾向 |
| KisyuCode | TEXT | 騎手コード |
| KisyuName | TEXT | 騎手名 |
| ChokyosiCode | TEXT | 調教師コード |
| ChokyosiName | TEXT | 調教師名 |
| BanusiCode | TEXT | 馬主コード |
| BanusiName | TEXT | 馬主名 |
| BreederCode | TEXT | 生産者コード |
| BreederName | TEXT | 生産者名 |

---

## NL_WE（天候馬場状態）

天候・馬場状態情報。

**PRIMARY KEY**: `(Year, MonthDay, JyoCD, Kaiji, Nichiji, HenkoID)`

| カラム | 型 | 説明 |
|--------|-----|------|
| Year | INTEGER | 開催年 |
| MonthDay | INTEGER | 月日 |
| JyoCD | TEXT | 競馬場コード |
| Kaiji | INTEGER | 回次 |
| Nichiji | INTEGER | 日次 |
| HenkoID | TEXT | 変更ID |
| HappyoTime | TEXT | 発表時刻 |
| TenkoBaba | TEXT | 天候馬場 |
| TenkoCD | TEXT | 天候コード（1=晴〜6=小雪） |
| SibaBabaCD | TEXT | 芝馬場コード（1=良〜4=不良） |
| DirtBabaCD | TEXT | ダート馬場コード |

---

## NL_WH（馬体重情報）

馬体重情報。

**PRIMARY KEY**: `(Year, MonthDay, JyoCD, Kaiji, Nichiji, HappyoTime, HenkoID)`

| カラム | 型 | 説明 |
|--------|-----|------|
| Year | INTEGER | 開催年 |
| MonthDay | INTEGER | 月日 |
| JyoCD | TEXT | 競馬場コード |
| Kaiji | INTEGER | 回次 |
| Nichiji | INTEGER | 日次 |
| RaceNum | INTEGER | レース番号 |
| HappyoTime | TEXT | 発表時刻 |
| HenkoID | TEXT | 変更ID |
| Umaban | INTEGER | 馬番 |
| Bataiju | INTEGER | 馬体重（kg） |
| ZogenFugo | TEXT | 増減符号 |
| ZogenSa | INTEGER | 増減差 |

---

## NL_JC（騎手変更情報）

騎手変更情報。

**PRIMARY KEY**: `(Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum, Umaban)`

| カラム | 型 | 説明 |
|--------|-----|------|
| Year | INTEGER | 開催年 |
| MonthDay | INTEGER | 月日 |
| JyoCD | TEXT | 競馬場コード |
| Kaiji | INTEGER | 回次 |
| Nichiji | INTEGER | 日次 |
| RaceNum | INTEGER | レース番号 |
| Umaban | INTEGER | 馬番 |
| HappyoTime | TEXT | 発表時刻 |
| MaeKisyuCode | TEXT | 変更前騎手コード |
| MaeKisyuName | TEXT | 変更前騎手名 |
| MaeFutan | REAL | 変更前負担重量 |
| AtoKisyuCode | TEXT | 変更後騎手コード |
| AtoKisyuName | TEXT | 変更後騎手名 |
| AtoFutan | REAL | 変更後負担重量 |
| JiyuCD | TEXT | 変更事由コード |

---

## NL_JG（出走取消情報）

出走取消・競走除外情報。

**PRIMARY KEY**: `(Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum, KettoNum)`

| カラム | 型 | 説明 |
|--------|-----|------|
| Year | INTEGER | 開催年 |
| MonthDay | INTEGER | 月日 |
| JyoCD | TEXT | 競馬場コード |
| Kaiji | INTEGER | 回次 |
| Nichiji | INTEGER | 日次 |
| RaceNum | INTEGER | レース番号 |
| KettoNum | TEXT | 血統登録番号 |
| Umaban | INTEGER | 馬番 |
| Bamei | TEXT | 馬名 |
| HappyoTime | TEXT | 発表時刻 |
| TorikeKubun | TEXT | 取消区分（1=取消、2=除外） |
| TorikeJiyuCD | TEXT | 取消事由コード |

---

## NL_TC（発走時刻変更）

発走時刻変更情報。

**PRIMARY KEY**: `(Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum)`

| カラム | 型 | 説明 |
|--------|-----|------|
| Year | INTEGER | 開催年 |
| MonthDay | INTEGER | 月日 |
| JyoCD | TEXT | 競馬場コード |
| Kaiji | INTEGER | 回次 |
| Nichiji | INTEGER | 日次 |
| RaceNum | INTEGER | レース番号 |
| HappyoTime | TEXT | 発表時刻 |
| MaeHassoTime | TEXT | 変更前発走時刻 |
| AtoHassoTime | TEXT | 変更後発走時刻 |
| JiyuCD | TEXT | 変更事由コード |

---

## NL_CC（コース変更情報）

コース変更情報。

**PRIMARY KEY**: `(Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum)`

| カラム | 型 | 説明 |
|--------|-----|------|
| Year | INTEGER | 開催年 |
| MonthDay | INTEGER | 月日 |
| JyoCD | TEXT | 競馬場コード |
| Kaiji | INTEGER | 回次 |
| Nichiji | INTEGER | 日次 |
| RaceNum | INTEGER | レース番号 |
| HappyoTime | TEXT | 発表時刻 |
| MaeKyori | INTEGER | 変更前距離 |
| MaeTrackCD | TEXT | 変更前トラックコード |
| AtoKyori | INTEGER | 変更後距離 |
| AtoTrackCD | TEXT | 変更後トラックコード |
| JiyuCD | TEXT | 変更事由コード |

---

## NL_YS（開催スケジュール）

開催スケジュール情報。

**PRIMARY KEY**: `(Year, MonthDay, JyoCD, Kaiji, Nichiji)`

| カラム | 型 | 説明 |
|--------|-----|------|
| RecordSpec | TEXT | レコード種別（YS） |
| DataKubun | TEXT | データ区分 |
| Year | INTEGER | 開催年 |
| MonthDay | INTEGER | 月日 |
| JyoCD | TEXT | 競馬場コード |
| JyoName | TEXT | 競馬場名 |
| Kaiji | INTEGER | 回次 |
| Nichiji | INTEGER | 日次 |
| YoubiCD | TEXT | 曜日コード |
| KaisaiKubun | TEXT | 開催区分 |

---

## TS_O1〜TS_O6（時系列オッズ）

オッズの時系列データを格納。通常テーブルに加えてTimestampカラムを持つ。

**PRIMARY KEY**: 各テーブルの通常キー + `Timestamp`

| カラム | 型 | 説明 |
|--------|-----|------|
| （通常オッズテーブルと同じ） | - | - |
| Timestamp | TEXT | 記録時刻 |

---

## RT_テーブル（速報系）

RT_で始まるテーブルは対応するNL_テーブルと同じスキーマを持ち、リアルタイムデータを格納します。

| 速報テーブル | 対応蓄積テーブル |
|-------------|-----------------|
| RT_RA | NL_RA |
| RT_SE | NL_SE |
| RT_HR | NL_HR |
| RT_H1 | NL_H1 |
| RT_H6 | NL_H6 |
| RT_O1 | NL_O1 |
| RT_O2 | NL_O2 |
| RT_O3 | NL_O3 |
| RT_O4 | NL_O4 |
| RT_O5 | NL_O5 |
| RT_O6 | NL_O6 |
| RT_WE | NL_WE |
| RT_WH | NL_WH |
| RT_JC | NL_JC |
| RT_TC | NL_TC |
| RT_CC | NL_CC |
| RT_TM | NL_TM |
| RT_DM | NL_DM |
| RT_AV | NL_AV |

---

## コード値一覧

### グレードコード（GradeCD）

| コード | 説明 |
|--------|------|
| A | GI |
| B | GII |
| C | GIII |
| D | 重賞 |
| E | OP特別 |
| F | リステッド（L） |
| G | 3勝クラス |
| H | 2勝クラス |
| I | 1勝クラス |
| J | 未勝利 |
| K | 新馬 |

### 性別コード（SexCD）

| コード | 説明 |
|--------|------|
| 1 | 牡 |
| 2 | 牝 |
| 3 | セン |

### 毛色コード（KeiroCD）

| コード | 説明 |
|--------|------|
| 01 | 栗毛 |
| 02 | 栃栗毛 |
| 03 | 鹿毛 |
| 04 | 黒鹿毛 |
| 05 | 青鹿毛 |
| 06 | 青毛 |
| 07 | 芦毛 |
| 08 | 栗粕毛 |
| 09 | 鹿粕毛 |
| 10 | 白毛 |

### 天候コード（TenkoCD）

| コード | 説明 |
|--------|------|
| 1 | 晴 |
| 2 | 曇 |
| 3 | 雨 |
| 4 | 小雨 |
| 5 | 雪 |
| 6 | 小雪 |

### 馬場状態コード（BabaCD）

| コード | 説明 |
|--------|------|
| 1 | 良 |
| 2 | 稍重 |
| 3 | 重 |
| 4 | 不良 |

### トラックコード（TrackCD）

| コード | 説明 |
|--------|------|
| 10 | 芝・左 |
| 11 | 芝・右 |
| 12 | 芝・直線 |
| 17 | 芝・右→左 |
| 18 | 芝・左→右 |
| 20 | ダート・左 |
| 21 | ダート・右 |
| 22 | ダート・直線 |
| 23 | ダート・右→左 |
| 24 | ダート・左→右 |
| 29 | 障害芝 |
| 51 | 外回り |
| 52 | 内回り |

### 東西コード（TozaiCD）

| コード | 説明 |
|--------|------|
| 1 | 関東（美浦） |
| 2 | 関西（栗東） |
| 3 | 地方 |
| 4 | 外国 |
