/**
 * מזג אוויר - משתמש ב-wttr.in (חינמי לחלוטין, ללא API key)
 */
async function getWeather(city) {
    try {
        // wttr.in - שירות מזג אוויר חינמי וללא צורך ב-API key
        const encodedCity = encodeURIComponent(city);
        const url = `https://wttr.in/${encodedCity}?format=4&lang=he`;

        const response = await fetch(url, {
            headers: {
                'User-Agent': 'curl/7.81.0' // wttr.in מעדיף User-Agent של curl
            },
            signal: AbortSignal.timeout(8000)
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const text = (await response.text()).trim();

        if (!text || text.includes('Unknown location')) {
            // נסה פורמט אחר
            return await getWeatherSimple(city);
        }

        return text;

    } catch (error) {
        console.error('שגיאת מזג אוויר:', error.message);
        return await getWeatherSimple(city);
    }
}

async function getWeatherSimple(city) {
    try {
        const url = `https://wttr.in/${encodeURIComponent(city)}?format=3`;
        const response = await fetch(url, {
            headers: { 'User-Agent': 'curl/7.81.0' },
            signal: AbortSignal.timeout(6000)
        });
        const text = (await response.text()).trim();
        if (text && !text.includes('Unknown location')) {
            return text;
        }
        return `לא נמצא מידע מזג אוויר עבור "${city}". בדוק את שם העיר.`;
    } catch {
        return `לא ניתן לקבל מזג אוויר עבור "${city}" כרגע.`;
    }
}

module.exports = { getWeather };
