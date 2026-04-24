// 設定
const CALENDAR_ID = '544c01e5c3b31811764c176ec146e48f70bc1265802cd08335ae500dcbefd051@group.calendar.google.com'; // 自分のカレンダーIDを入力
const JMA_URL = 'https://www.jma.go.jp/bosai/forecast/data/forecast/080000.json';
const AREA_CODE = '080020'; // 茨城県南部
const TEMP_CODE = '40341'; // 土浦（つくばエリア代表）

function updateWeatherToCalendar() {
  const response = UrlFetchApp.fetch(JMA_URL);
  const data = JSON.parse(response.getContentText());
  const shortForecast = data[0];
  
  const calendar = CalendarApp.getCalendarById(CALENDAR_ID);
  
  // 1. 各シリーズからターゲットエリアを抽出
  const weatherSeries = shortForecast.timeSeries[0];
  const areaWeather = weatherSeries.areas.find(a => a.area.code === AREA_CODE);
  const popSeries = shortForecast.timeSeries[1];
  const areaPop = popSeries.areas.find(a => a.area.code === AREA_CODE);
  const tempSeries = shortForecast.timeSeries[2];
  const areaTemp = tempSeries.areas.find(a => a.area.code === TEMP_CODE);

  if (!areaWeather || !areaPop || !areaTemp) return;

  // 2. 既存の「つくばの天気」予定を削除（重複防止）
  const now = new Date();
  const endTime = new Date(now.getTime() + 3 * 24 * 60 * 60 * 1000); // 3日後まで
  const events = calendar.getEvents(now, endTime);
  events.forEach(event => {
    if (event.getTag('source') === 'jma_weather') {
      event.deleteEvent();
    }
  });

  // 3. 予報をカレンダーに登録
  weatherSeries.timeDefines.forEach((timeDefine, i) => {
    const date = new Date(timeDefine);
    const dateStr = timeDefine.substring(0, 10);
    
    // 降水確率の最大値取得
    const pops = areaPop.pops.filter((p, idx) => popSeries.timeDefines[idx].startsWith(dateStr)).map(Number);
    const popMax = pops.length > 0 ? Math.max(...pops) : "--";

    // 気温の取得
    const temps = areaTemp.temps.filter((t, idx) => tempSeries.timeDefines[idx].startsWith(dateStr));
    const tMin = temps[0] || "--";
    const tMax = temps[1] || "--";

    const weatherText = areaWeather.weathers[i].replace(/\s+/g, "");
    const summary = `${weatherText} (${tMin}/${tMax}℃) ☔${popMax}%`;
    
    const event = calendar.createAllDayEvent(summary, date);
    event.setTag('source', 'jma_weather'); // 削除時の識別用タグ
    event.setDescription(`気象庁発表: つくば市周辺\n最高気温: ${tMax}℃ / 最低気温: ${tMin}℃\n降水確率: ${popMax}%`);
  });
}
