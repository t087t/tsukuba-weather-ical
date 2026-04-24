# tsukuba-weather-ical
本リポジトリは、つくば市の天気予報データ（JSON）を取得し、毎日決まった時間に詳細な天気をGoogleカレンダー等に自動反映します。

## コンセプト
* 既存のiCalendar形式の天気予報提供サービスでは県単位などの広域な予報のみであったため、「つくば市（茨城県南部）」のピンポイントな地点情報を提供します。
* iCal形式（URL参照型）はGoogleカレンダー側の更新頻度に依存するため、反映の遅延を解消するため、GASによる直接書き込みを採用しました。

## 構成
本リポジトリには、2つの手法を格納しています。現在はリアルタイム性を重視した**1. GAS版**での運用を推奨しています。

1. **Google Apps Script版 (推奨)**
GoogleカレンダーのAPIを直接叩くことで、iCal形式のURLインポートで発生する同期の遅延を解消した最新版です。
    - **実行環境**: Google Apps Script (GAS)
    - **同期頻度**: 1日3回（気象庁の発表タイミング：5時、11時、17時の直後に同期）
    - **ファイル**: `weather_sync.gs`

2. **Python + GitHub Actions版 (旧バージョン)**
iCalendar (.ics) ファイルを生成し、GitHub Pagesで公開する手法です。
OutlookやAppleカレンダーなど、Google以外のカレンダーアプリでも汎用的に利用可能です。
   - **言語**: Python 3.x
   - **実行環境**: GitHub Actions
   - **更新頻度**: 毎日 6:00 (JST)
   - **ファイル**: `main.py`, `.github/workflows/update.yml`

## 技術スタック
* **言語**: JavaScript (GAS) / Python
* **インフラ・自動化**: Google Apps Script / GitHub Actions
* **データソース**: 気象庁 予報JSON（茨城県南部・土浦地点）

## Google Apps Script版 (推奨)の使用方法
1. [Google Apps Script](https://script.google.com/home) で新規プロジェクトを作成。
2. 本リポジトリの `weather_sync.gs` の内容をコピー＆ペースト。
3. CALENDAR_ID を自身のGoogleカレンダーIDに書き換え。
4. トリガーを設定（毎日 5:15, 11:15, 17:15 など、発表直後の時間が推奨です）。

## Python + GitHub Actions版 (旧バージョン)の使用方法
1.  生成されたURL `https://t087t.github.io/tsukuba-weather-ical/tsukuba_weather.ics` をコピーします。
2.  Googleカレンダーを開き、「他のカレンダー」の＋アイコンから「URLで追加」を選択しコピーしたURLを貼り付けます。
