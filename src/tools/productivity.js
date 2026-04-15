// Productivity: time parsing, reminders, countdown

function parseIsraeliTime(text) {
    const now = new Date();
    const israelNow = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Jerusalem' }));

    // "בעוד X דקות"
    const minMatch = text.match(/בעוד\s+(\d+)\s+דקות?/);
    if (minMatch) return now.getTime() + parseInt(minMatch[1]) * 60000;

    // "בעוד X שעות"
    const hrMatch = text.match(/בעוד\s+(\d+)\s+שעות?/);
    if (hrMatch) return now.getTime() + parseInt(hrMatch[1]) * 3600000;

    // "בשעה HH:MM" or "שעה HH:MM"
    const timeMatch = text.match(/(?:ב?שעה?\s*)(\d{1,2})(?::(\d{2}))?/i);
    if (timeMatch) {
        const h = parseInt(timeMatch[1]);
        const m = timeMatch[2] ? parseInt(timeMatch[2]) : 0;
        const target = new Date(israelNow);
        target.setHours(h, m, 0, 0);
        if (target.getTime() <= israelNow.getTime()) target.setDate(target.getDate() + 1);
        // Adjust back to UTC
        const diff = israelNow.getTime() - now.getTime();
        return target.getTime() - diff;
    }

    // "מחר בשעה X" or "מחר ב-X"
    const tmrMatch = text.match(/מחר.*?(\d{1,2})(?::(\d{2}))?/);
    if (tmrMatch) {
        const h = parseInt(tmrMatch[1]);
        const m = tmrMatch[2] ? parseInt(tmrMatch[2]) : 0;
        const target = new Date(israelNow);
        target.setDate(target.getDate() + 1);
        target.setHours(h, m, 0, 0);
        const diff = israelNow.getTime() - now.getTime();
        return target.getTime() - diff;
    }

    // Hebrew hour words
    const hebrewHours = {
        'אחת': 1, 'שתיים': 2, 'שלוש': 3, 'ארבע': 4, 'חמש': 5, 'שש': 6,
        'שבע': 7, 'שמונה': 8, 'תשע': 9, 'עשר': 10, 'אחת עשרה': 11, 'שתים עשרה': 12
    };
    for (const [word, hour] of Object.entries(hebrewHours)) {
        if (text.includes(word)) {
            const target = new Date(israelNow);
            target.setHours(hour, 0, 0, 0);
            if (target.getTime() <= israelNow.getTime()) target.setDate(target.getDate() + 1);
            const diff = israelNow.getTime() - now.getTime();
            return target.getTime() - diff;
        }
    }

    return null;
}

function formatCountdown(targetMs) {
    const diff = targetMs - Date.now();
    if (diff < 0) return 'התאריך כבר עבר';
    const days = Math.floor(diff / 86400000);
    const hours = Math.floor((diff % 86400000) / 3600000);
    const mins = Math.floor((diff % 3600000) / 60000);
    const parts = [];
    if (days > 0) parts.push(`${days} ימים`);
    if (hours > 0) parts.push(`${hours} שעות`);
    if (mins > 0) parts.push(`${mins} דקות`);
    return parts.length ? parts.join(', ') : 'פחות מדקה';
}

module.exports = { parseIsraeliTime, formatCountdown };
