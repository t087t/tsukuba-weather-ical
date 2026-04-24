import requests
from icalendar import Calendar, Event
from datetime import datetime, timedelta
from typing import Dict, Optional, List

# 茨城県の予報JSON
JMA_JSON_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/080000.json"
TARGET_AREA_CODE = "080020"  # 茨城県南部のコード
OUTPUT_FILE = "tsukuba_weather.ics"

# 天気コード変換辞書
WEATHER_MAP: Dict[str, str] = {
    # 100番台：晴れベース
    "100": "晴れ", "101": "晴れ時々くもり", "102": "晴れ一時雨", "103": "晴れ時々雨",
    "104": "晴れ一時雪", "105": "晴れ時々雪", "106": "晴れ一時雨か雪", "107": "晴れ時々雨か雪",
    "108": "晴れ一時雨", "110": "晴れのち時々くもり", "111": "晴れのちくもり", "112": "晴れのち一時雨",
    "113": "晴れのち時々雨", "114": "晴れのち雨", "115": "晴れのち一時雪", "116": "晴れのち時々雪",
    "117": "晴れのち雪", "118": "晴れのち雨か雪", "119": "晴れのち雨か雷雨", "120": "晴れ一時雨",
    "121": "晴れ一時雨", "122": "晴れ夕方一時雨", "123": "晴れ山沿い雷雨", "124": "晴れ山沿い雪",
    "125": "晴れ午後は雷雨", "126": "晴れ昼頃から雨", "127": "晴れ夕方から雨", "128": "晴れ夜は雨",
    "129": "晴れ夜半から雨", "130": "朝の内霧のち晴れ", "131": "晴れ朝方霧", "132": "晴れ時々くもり",
    "140": "晴れ時々雨", "160": "晴れ一時雪か雨", "170": "晴れ時々雪か雨", "181": "晴れのち雪か雨",

    # 200番台：くもりベース
    "200": "くもり", "201": "くもり時々晴れ", "202": "くもり一時雨", "203": "くもり時々雨",
    "204": "くもり一時雪", "205": "くもり時々雪", "206": "くもり一時雨か雪", "207": "くもり時々雨か雪",
    "208": "くもり一時雨か雷雨", "209": "霧", "210": "くもりのち時々晴れ", "211": "くもりのち晴れ",
    "212": "くもりのち一時雨", "213": "くもりのち時々雨", "214": "くもりのち雨", "215": "くもりのち一時雪",
    "216": "くもりのち時々雪", "217": "くもりのち雪", "218": "くもりのち雨か雪", "219": "くもりのち雨か雷雨",
    "220": "くもり朝夕一時雨", "221": "くもり朝の内一時雨", "222": "くもり夕方一時雨", "223": "くもり日中時々晴れ",
    "224": "くもり昼頃から雨", "225": "くもり夕方から雨", "226": "くもり夜は雨", "227": "くもり夜半から雨",
    "228": "くもり昼頃から雪", "229": "くもり夕方から雪", "230": "くもり夜は雪", "231": "くもり海上海岸は霧か霧雨",
    "240": "くもり時々雨で雷を伴う", "250": "くもり時々雪で雷を伴う", "260": "くもり一時雪か雨", "270": "くもり時々雪か雨",
    "281": "くもりのち雪か雨",

    # 300番台：雨ベース
    "300": "雨", "301": "雨時々晴れ", "302": "雨時々止む", "303": "雨時々雪",
    "304": "雨か雪", "306": "大雨", "308": "雨で暴風を伴う", "309": "雨一時雪",
    "311": "雨のち晴れ", "313": "雨のちくもり", "314": "雨のち時々雪", "315": "雨のち雪",
    "316": "雨か雪のち晴れ", "317": "雨か雪のちくもり", "320": "朝の内雨のち晴れ", "321": "朝の内雨のちくもり",
    "322": "雨朝晩一時雪", "323": "雨昼頃から晴れ", "324": "雨夕方から晴れ", "325": "雨夜は晴れ",
    "326": "雨夕方から雪", "327": "雨夜は雪", "328": "雨一時強く降る", "329": "雨一時みぞれ",
    "340": "雪か雨", "350": "雷", "361": "雪か雨のち晴れ", "371": "雪か雨のちくもり",

    # 400番台：雪ベース
    "400": "雪", "401": "雪時々晴れ", "402": "雪時々止む", "403": "雪時々雨",
    "405": "大雪", "406": "風雪強い", "407": "暴風雪", "409": "雪一時雨",
    "411": "雪のち晴れ", "413": "雪のちくもり", "414": "雪のち雨", "420": "朝の内雪のち晴れ",
    "421": "朝の内雪のちくもり", "422": "雪昼頃から雨", "423": "雪夕方から雨", "424": "雪夜半から雨",
    "425": "雪一時強く降る", "426": "雪のちみぞれ", "427": "雪一時みぞれ", "430": "みぞれ",
    "450": "雪で雷を伴う",
}

def get_weather_label(code: str) -> str:
    """天気コードを日本語ラベルに変換する"""
    return WEATHER_MAP.get(code, f"不明({code})")

def fetch_weather_data() -> Optional[Dict]:
    """気象庁からデータを取得する"""
    try:
        response = requests.get(JMA_JSON_URL)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"データの取得に失敗しました: {e}")
        return None

def generate_ical():
    data = fetch_weather_data()
    if not data:
        return

    # data[1] が週間予報
    weekly_forecast = data[1]
    
    # 茨城県南部 (つくば周辺) の天気・降水確率データを特定
    weather_series = weekly_forecast['timeSeries'][0]
    area_weather = next((a for a in weather_series['areas'] if a['area']['code'] == TARGET_AREA_CODE), None)
    
    # 茨城県南部 (つくば周辺) の気温データを特定
    temp_series = weekly_forecast['timeSeries'][1]
    area_temp = next((a for a in temp_series['areas'] if a['area']['code'] == TARGET_AREA_CODE), None)

    if not area_weather or not area_temp:
        print("指定されたエリアのデータが見つかりませんでした。")
        return

    # カレンダーの作成
    cal = Calendar()
    cal.add('prodid', '-//Tsukuba Weather Calendar//v1.0//')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'つくばの天気予報')

    # 日付リストを取得
    time_defines = weather_series['timeDefines']

    for i in range(len(time_defines)):
        # 日付の変換
        dt = datetime.fromisoformat(time_defines[i])
        
        # 各種データの抽出
        w_code = area_weather['weatherCodes'][i]
        pop = area_weather['pops'][i] if 'pops' in area_weather else "--"
        t_max = area_temp['tempsMax'][i] if i < len(area_temp['tempsMax']) else "--"
        t_min = area_temp['tempsMin'][i] if i < len(area_temp['tempsMin']) else "--"
        
        weather_text = get_weather_label(w_code)
        
        # イベントの作成
        event = Event()
        # タイトル: "晴 (18/25℃) 降水10%"
        summary = f"{weather_text} ({t_min}/{t_max}℃) ☔{pop}%"
        event.add('summary', summary)
        
        # 期間: 終日イベント
        event.add('dtstart', dt.date())
        event.add('dtend', dt.date() + timedelta(days=1))
        
        # 説明文
        description = (
            f"気象庁発表: つくば市(茨城県南部)\n"
            f"天気: {weather_text}\n"
            f"最高気温: {t_max}℃\n"
            f"最低気温: {t_min}℃\n"
            f"降水確率: {pop}%"
        )
        event.add('description', description)
        
        cal.add_component(event)

    # ファイル書き出し
    with open(OUTPUT_FILE, 'wb') as f:
        f.write(cal.to_ical())
    print(f"成功: {OUTPUT_FILE} を生成しました。")

if __name__ == "__main__":
    generate_ical()
