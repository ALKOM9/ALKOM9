// Information sources: news, sports, movies, books, Shabbat, weather forecast, air quality, nutrition

async function fetchRSS(url, limit = 5) {
    try {
        const res = await fetch(url, {
            headers: { 'User-Agent': 'Mozilla/5.0', Accept: 'application/rss+xml, text/xml, */*' },
            signal: AbortSignal.timeout(8000)
        });
        if (!res.ok) return [];
        const xml = await res.text();
        const items = [];
        const re = /<item>([\s\S]*?)<\/item>/g;
        let m;
        while ((m = re.exec(xml)) !== null && items.length < limit) {
            const chunk = m[1];
            const title = extractXML(chunk, 'title');
            const desc = extractXML(chunk, 'description') || '';
            if (title) items.push(`• ${title}\n  ${desc.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim().slice(0, 90)}`);
        }
        return items;
    } catch { return []; }
}

function extractXML(text, tag) {
    const re = new RegExp(`<${tag}[^>]*>(?:<!\\[CDATA\\[)?([\s\S]*?)(?:\\]\\]>)?<\\/${tag}>`, 'i');
    const m = text.match(re);
    return m ? m[1].replace(/<[^>]+>/g, '').trim() : null;
}

async function getIsraeliNews(source) {
    const feeds = {
        ynet: 'https://www.ynet.co.il/Integration/StoryRss2.xml',
        walla: 'https://rss.walla.co.il/feed/1',
        n12: 'https://www.mako.co.il/rss/news-n12.xml'
    };
    const toFetch = source && feeds[source] ? [feeds[source]] : Object.values(feeds);
    const results = await Promise.allSettled(toFetch.map(url => fetchRSS(url, 3)));
    const items = results.flatMap(r => r.status === 'fulfilled' ? r.value : []);
    if (!items.length) return null;
    return `📰 חדשות ישראל:\n${items.slice(0, 6).join('\n\n')}`;
}

async function getGoogleNews(query) {
    try {
        const url = `https://news.google.com/rss/search?q=${encodeURIComponent(query)}&hl=iw&gl=IL&ceid=IL:iw`;
        const items = await fetchRSS(url, 5);
        if (!items.length) return null;
        return `📰 חדשות — ${query}:\n${items.join('\n\n')}`;
    } catch { return null; }
}

async function getSportsScores(sport) {
    try {
        const sportMap = {
            soccer: 'https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard',
            nba: 'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard',
            nfl: 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard',
        };
        const sportHe = { soccer: '⚽ פרמייר ליג', nba: '🏀 NBA', nfl: '🏈 NFL', f1: '🏎️ F1' };

        if (sport === 'f1') {
            const res = await fetch('https://ergast.com/api/f1/current/last/results.json', {
                signal: AbortSignal.timeout(8000)
            });
            if (!res.ok) return null;
            const d = await res.json();
            const race = d?.MRData?.RaceTable?.Races?.[0];
            if (!race) return 'אין תוצאות F1 זמינות';
            const results = (race.Results || []).slice(0, 5).map((r, i) =>
                `${i + 1}. ${r.Driver.givenName} ${r.Driver.familyName} (${r.Constructor.name})`
            );
            return `🏎️ F1 — ${race.raceName} (${race.date}):\n${results.join('\n')}`;
        }

        const ep = sportMap[sport] || sportMap.soccer;
        const res = await fetch(ep, { signal: AbortSignal.timeout(8000) });
        if (!res.ok) return null;
        const d = await res.json();
        const events = d.events?.slice(0, 6);
        if (!events?.length) return `אין משחקים ${sportHe[sport] || ''} עכשיו`;
        const lines = events.map(e => {
            const comps = e.competitions?.[0]?.competitors;
            if (!comps) return null;
            const home = comps.find(t => t.homeAway === 'home');
            const away = comps.find(t => t.homeAway === 'away');
            const score = e.status?.type?.completed ? `${home?.score || 0}-${away?.score || 0}` : e.status?.displayClock || 'טרם התחיל';
            return `${home?.team?.name || '?'} ${score} ${away?.team?.name || '?'}`;
        }).filter(Boolean);
        return `${sportHe[sport] || sport}:\n${lines.join('\n')}`;
    } catch { return null; }
}

async function getMovie(title) {
    try {
        // Try OMDb with demo key, fallback to search
        const res = await fetch(`https://www.omdbapi.com/?t=${encodeURIComponent(title)}&apikey=trilogy&plot=short`, {
            signal: AbortSignal.timeout(7000)
        });
        if (!res.ok) return null;
        const d = await res.json();
        if (d.Response === 'False') {
            const s = await fetch(`https://www.omdbapi.com/?s=${encodeURIComponent(title)}&apikey=trilogy`, {
                signal: AbortSignal.timeout(7000)
            });
            if (!s.ok) return `לא נמצא "${title}" ב-IMDB`;
            const sd = await s.json();
            if (sd.Response === 'False') return `לא נמצא "${title}" ב-IMDB`;
            const items = (sd.Search || []).slice(0, 3).map(i => `🎬 ${i.Title} (${i.Year}) — ${i.Type}`);
            return items.join('\n');
        }
        let r = `🎬 ${d.Title} (${d.Year})`;
        if (d.Genre && d.Genre !== 'N/A') r += `\nז'אנר: ${d.Genre}`;
        if (d.imdbRating && d.imdbRating !== 'N/A') r += `\n⭐ IMDB: ${d.imdbRating}/10`;
        if (d.Runtime && d.Runtime !== 'N/A') r += ` | ${d.Runtime}`;
        if (d.Director && d.Director !== 'N/A') r += `\n🎥 במאי: ${d.Director}`;
        if (d.Actors && d.Actors !== 'N/A') r += `\n👤 ${d.Actors}`;
        if (d.Plot && d.Plot !== 'N/A') r += `\n${d.Plot.slice(0, 200)}`;
        return r;
    } catch { return null; }
}

async function getBook(query) {
    try {
        // Try Hebrew first, then English
        for (const params of [`q=${encodeURIComponent(query)}&langRestrict=he&maxResults=3`, `q=${encodeURIComponent(query)}&maxResults=3`]) {
            const res = await fetch(`https://www.googleapis.com/books/v1/volumes?${params}`, {
                signal: AbortSignal.timeout(7000)
            });
            if (!res.ok) continue;
            const d = await res.json();
            if (!d.items?.length) continue;
            const books = d.items.slice(0, 3).map(item => {
                const info = item.volumeInfo;
                let r = `📚 ${info.title}`;
                if (info.authors?.length) r += `\n✍️ ${info.authors.slice(0, 2).join(', ')}`;
                if (info.publishedDate) r += ` (${info.publishedDate.slice(0, 4)})`;
                if (info.description) r += `\n${info.description.replace(/<[^>]+>/g, '').slice(0, 120)}...`;
                if (info.averageRating) r += `\n⭐ ${info.averageRating}/5`;
                return r;
            });
            return books.join('\n\n---\n\n');
        }
        return null;
    } catch { return null; }
}

async function getShabbatTimes(city) {
    try {
        const cityMap = {
            'תל אביב': 'Tel Aviv', 'ירושלים': 'Jerusalem', 'חיפה': 'Haifa',
            'באר שבע': 'Be\'er Sheva', 'נתניה': 'Netanya', 'ראשון לציון': 'Rishon LeZion',
            'אשדוד': 'Ashdod', 'פתח תקווה': 'Petah Tikva', 'הרצליה': 'Herzliya',
            'רמת גן': 'Ramat Gan', 'רחובות': 'Rehovot', 'אשקלון': 'Ashqelon'
        };
        const englishCity = cityMap[city] || city || 'Tel Aviv';
        const res = await fetch(`https://www.hebcal.com/shabbat?cfg=json&geo=city&city=${encodeURIComponent(englishCity)}&m=50`, {
            signal: AbortSignal.timeout(8000)
        });
        if (!res.ok) return null;
        const d = await res.json();
        const items = d.items || [];
        const candles = items.find(i => i.category === 'candles');
        const havdalah = items.find(i => i.category === 'havdalah');
        const parasha = items.find(i => i.category === 'parashat');
        if (!candles) return null;
        const fmt = (dateStr) => new Date(dateStr).toLocaleString('he-IL', {
            timeZone: 'Asia/Jerusalem', weekday: 'long', hour: '2-digit', minute: '2-digit'
        });
        let r = `🕯️ שבת ב${city || 'תל אביב'}:\nכניסה: ${fmt(candles.date)}`;
        if (havdalah) r += `\nיציאה: ${fmt(havdalah.date)}`;
        if (parasha) r += `\n📖 פרשת השבוע: ${parasha.hebrew || parasha.title}`;
        return r;
    } catch { return null; }
}

async function getHebrewDate() {
    try {
        const now = new Date();
        const res = await fetch(`https://www.hebcal.com/converter?cfg=json&gy=${now.getFullYear()}&gm=${now.getMonth() + 1}&gd=${now.getDate()}&g2h=1`, {
            signal: AbortSignal.timeout(7000)
        });
        if (!res.ok) return null;
        const d = await res.json();
        return d.hebrew ? `📅 תאריך עברי: ${d.hebrew}` : null;
    } catch { return null; }
}

async function getWeatherForecast(city) {
    try {
        const geoRes = await fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(city)}&count=1&language=he`, {
            signal: AbortSignal.timeout(7000)
        });
        if (!geoRes.ok) return null;
        const geoData = await geoRes.json();
        const loc = geoData.results?.[0];
        if (!loc) return `לא נמצאה עיר: ${city}`;

        const res = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${loc.latitude}&longitude=${loc.longitude}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode&timezone=Asia%2FJerusalem&forecast_days=7`, {
            signal: AbortSignal.timeout(8000)
        });
        if (!res.ok) return null;
        const d = await res.json();
        const daily = d.daily;
        if (!daily) return null;

        const icons = { 0: '☀️', 1: '🌤', 2: '⛅', 3: '☁️', 45: '🌫', 48: '🌫', 51: '🌦', 53: '🌦', 55: '🌧', 61: '🌧', 63: '🌧', 65: '🌧', 71: '❄️', 73: '❄️', 75: '❄️', 80: '🌦', 81: '🌧', 82: '⛈', 95: '⛈', 96: '⛈', 99: '⛈' };
        const days = daily.time.map((date, i) => {
            const icon = icons[daily.weathercode[i]] || '🌤';
            const dateStr = new Date(date).toLocaleDateString('he-IL', { weekday: 'short', month: 'numeric', day: 'numeric' });
            const rain = daily.precipitation_sum[i] > 0 ? ` 🌧${daily.precipitation_sum[i]}mm` : '';
            return `${icon} ${dateStr}: ${daily.temperature_2m_max[i]}°/${daily.temperature_2m_min[i]}°C${rain}`;
        });
        return `🌤 תחזית שבועית — ${loc.name}:\n${days.join('\n')}`;
    } catch { return null; }
}

async function getAirQuality(city) {
    try {
        const waqi = process.env.WAQI_TOKEN || 'demo';
        const res = await fetch(`https://api.waqi.info/feed/${encodeURIComponent(city)}/?token=${waqi}`, {
            signal: AbortSignal.timeout(7000)
        });
        if (!res.ok) return null;
        const d = await res.json();
        if (d.status !== 'ok') return null;
        const aqi = d.data.aqi;
        const level = aqi <= 50 ? '✅ טוב' : aqi <= 100 ? '🟡 מתון' : aqi <= 150 ? '🟠 לא בריא לרגישים' : aqi <= 200 ? '🔴 לא בריא' : '☠️ מסוכן';
        return `💨 איכות אוויר ב${city}:\nAQI: ${aqi} — ${level}`;
    } catch { return null; }
}

async function getNutrition(food) {
    try {
        const res = await fetch(`https://api.nal.usda.gov/fdc/v1/foods/search?query=${encodeURIComponent(food)}&pageSize=1&api_key=DEMO_KEY`, {
            signal: AbortSignal.timeout(8000)
        });
        if (res.ok) {
            const d = await res.json();
            const item = d.foods?.[0];
            if (item) {
                const nutrients = item.foodNutrients || [];
                const get = (name) => nutrients.find(n => n.nutrientName?.toLowerCase().includes(name))?.value;
                const cal = get('energy');
                const protein = get('protein');
                const carbs = get('carbohydrate');
                const fat = get('total lipid');
                const fiber = get('fiber');
                let r = `🥗 ${item.description} (100 גרם):\n`;
                if (cal) r += `🔥 קלוריות: ${Math.round(cal)} kcal\n`;
                if (protein) r += `💪 חלבון: ${Number(protein).toFixed(1)}g\n`;
                if (carbs) r += `🌾 פחמימות: ${Number(carbs).toFixed(1)}g\n`;
                if (fat) r += `🫒 שומן: ${Number(fat).toFixed(1)}g\n`;
                if (fiber) r += `🌿 סיבים: ${Number(fiber).toFixed(1)}g`;
                return r.trim();
            }
        }
    } catch { /* fallback */ }

    // Static table for common Israeli foods
    const table = {
        'חומוס': '166 kcal | חלבון 9g | פחמימות 14g | שומן 9g',
        'פלאפל': '333 kcal | חלבון 13g | פחמימות 32g | שומן 17g',
        'שווארמה': '250 kcal | חלבון 20g | פחמימות 15g | שומן 12g',
        'לחם': '265 kcal | חלבון 9g | פחמימות 49g | שומן 3g',
        'ביצה': '155 kcal | חלבון 13g | פחמימות 1g | שומן 11g',
        'עוף': '165 kcal | חלבון 31g | פחמימות 0g | שומן 4g',
        'בשר בקר': '250 kcal | חלבון 26g | פחמימות 0g | שומן 15g',
        'אורז': '130 kcal | חלבון 3g | פחמימות 28g | שומן 0g',
        'עגבניה': '18 kcal | חלבון 1g | פחמימות 4g | שומן 0g',
        'מלפפון': '16 kcal | חלבון 1g | פחמימות 4g | שומן 0g',
        'avocado': '160 kcal | חלבון 2g | פחמימות 9g | שומן 15g',
        'אבוקדו': '160 kcal | חלבון 2g | פחמימות 9g | שומן 15g',
        'בננה': '89 kcal | חלבון 1g | פחמימות 23g | שומן 0g',
        'תפוח': '52 kcal | חלבון 0g | פחמימות 14g | שומן 0g',
    };
    const lower = food.toLowerCase();
    for (const [key, val] of Object.entries(table)) {
        if (lower.includes(key.toLowerCase()) || key.toLowerCase().includes(lower)) {
            return `🥗 ${key} (100 גרם): ${val}`;
        }
    }
    return `לא נמצאו ערכים תזונתיים עבור "${food}". נסה לחפש שם ספציפי יותר.`;
}

module.exports = { getIsraeliNews, getGoogleNews, getSportsScores, getMovie, getBook, getShabbatTimes, getHebrewDate, getWeatherForecast, getAirQuality, getNutrition };
