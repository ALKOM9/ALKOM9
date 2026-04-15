// Technical utilities: converters, generators, validators

function convertUnits(value, from, to) {
    const v = Number(value);
    if (isNaN(v)) return 'ערך לא תקין';

    const fl = from.toLowerCase().replace(/\./g, '');
    const tl = to.toLowerCase().replace(/\./g, '');

    // Temperature (special)
    const tempNames = { c: 'c', celsius: 'c', f: 'f', fahrenheit: 'f', k: 'k', kelvin: 'k' };
    if (tempNames[fl] && tempNames[tl]) {
        let c;
        if (tempNames[fl] === 'c') c = v;
        else if (tempNames[fl] === 'f') c = (v - 32) * 5 / 9;
        else c = v - 273.15;
        let result;
        if (tempNames[tl] === 'c') result = c;
        else if (tempNames[tl] === 'f') result = c * 9 / 5 + 32;
        else result = c + 273.15;
        return `${v}° ${from.toUpperCase()} = ${result.toFixed(2)}° ${to.toUpperCase()}`;
    }

    const tables = {
        length: { m: 1, km: 1000, cm: 0.01, mm: 0.001, mi: 1609.344, ft: 0.3048, in: 0.0254, inch: 0.0254, yd: 0.9144, nm: 1.852e3 },
        weight: { kg: 1, g: 0.001, mg: 0.000001, lb: 0.453592, oz: 0.028349, t: 1000, ton: 1000 },
        volume: { l: 1, ml: 0.001, gal: 3.78541, cup: 0.236588, floz: 0.029574, m3: 1000, cm3: 0.001 },
        speed: { kmh: 1, mph: 1.60934, ms: 3.6, knot: 1.852 },
        data: { b: 1, kb: 1024, mb: 1048576, gb: 1073741824, tb: 1099511627776 },
        area: { m2: 1, km2: 1e6, cm2: 0.0001, ft2: 0.0929, acre: 4046.86, dunam: 1000 }
    };

    for (const table of Object.values(tables)) {
        if (table[fl] !== undefined && table[tl] !== undefined) {
            const result = v * table[fl] / table[tl];
            const formatted = result % 1 === 0 ? result.toString() : result.toPrecision(6).replace(/\.?0+$/, '');
            return `${v} ${from} = ${formatted} ${to}`;
        }
    }
    return `לא נתמכת המרה בין ${from} ל-${to}`;
}

function generatePassword(length, opts) {
    const len = Math.min(Math.max(parseInt(length) || 16, 4), 64);
    const { upper = true, lower = true, numbers = true, symbols = false } = opts || {};
    let charset = '';
    if (lower) charset += 'abcdefghijklmnopqrstuvwxyz';
    if (upper) charset += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    if (numbers) charset += '0123456789';
    if (symbols) charset += '!@#$%^&*()-_=+';
    if (!charset) charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';

    const crypto = require('crypto');
    const bytes = crypto.randomBytes(len);
    let password = '';
    for (let i = 0; i < len; i++) password += charset[bytes[i] % charset.length];

    const strength = len < 8 ? 'חלשה 🔴' : len < 12 ? 'בינונית 🟡' : len < 16 ? 'טובה 🟢' : 'חזקה מאוד 💪';
    return `🔐 סיסמה חדשה (${len} תווים):\n${password}\nחוזק: ${strength}`;
}

function encodeDecodeBase64(text, direction) {
    try {
        if (direction === 'decode') {
            return `🔡 פענוח Base64:\n${Buffer.from(text.trim(), 'base64').toString('utf8')}`;
        }
        return `🔡 Base64:\n${Buffer.from(text).toString('base64')}`;
    } catch (e) { return `שגיאה: ${e.message}`; }
}

function convertNumber(value, from, to) {
    const bases = { decimal: 10, binary: 2, hex: 16, octal: 8 };
    const fromBase = bases[from?.toLowerCase()] || 10;
    const toBase = bases[to?.toLowerCase()] || 2;
    try {
        const decimal = parseInt(String(value), fromBase);
        if (isNaN(decimal)) return 'ערך לא תקין';
        const result = decimal.toString(toBase).toUpperCase();
        const names = { 10: 'עשרוני', 2: 'בינארי', 16: 'הקסדצימלי', 8: 'אוקטלי' };
        return `${value} (${names[fromBase] || from}) = ${result} (${names[toBase] || to})`;
    } catch (e) { return `שגיאה: ${e.message}`; }
}

function convertColor(color) {
    const trimmed = color.trim();
    if (trimmed.startsWith('#')) {
        const hex = trimmed.replace('#', '');
        if (hex.length !== 6 && hex.length !== 3) return 'פורמט לא תקין. השתמש ב-#RRGGBB';
        const full = hex.length === 3 ? hex.split('').map(c => c + c).join('') : hex;
        const r = parseInt(full.slice(0, 2), 16);
        const g = parseInt(full.slice(2, 4), 16);
        const b = parseInt(full.slice(4, 6), 16);
        return `${trimmed} = rgb(${r}, ${g}, ${b})`;
    }
    const match = trimmed.match(/rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)/i);
    if (!match) return 'פורמט לא נתמך. השתמש ב-#RRGGBB או rgb(R,G,B)';
    const [, r, g, b] = match;
    const hex = '#' + [r, g, b].map(x => parseInt(x).toString(16).padStart(2, '0')).join('').toUpperCase();
    return `rgb(${r}, ${g}, ${b}) = ${hex}`;
}

function numberToRoman(num) {
    const n = parseInt(num);
    if (isNaN(n) || n < 1 || n > 3999) return 'מספר מחוץ לטווח (1-3999)';
    const vals = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1];
    const syms = ['M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I'];
    let result = '', remaining = n;
    for (let i = 0; i < vals.length; i++) {
        while (remaining >= vals[i]) { result += syms[i]; remaining -= vals[i]; }
    }
    return `${n} = ${result}`;
}

function validateIBAN(iban) {
    const clean = iban.replace(/\s/g, '').toUpperCase();
    if (clean.length < 15 || clean.length > 34) return '❌ IBAN לא תקין — אורך שגוי';
    const rearranged = clean.slice(4) + clean.slice(0, 4);
    const numeric = rearranged.split('').map(c => isNaN(c) ? (c.charCodeAt(0) - 55).toString() : c).join('');
    let remainder = 0;
    for (const ch of numeric) remainder = (remainder * 10 + parseInt(ch)) % 97;
    return remainder === 1 ? `✅ IBAN תקין: ${clean}` : '❌ IBAN לא תקין — ספרת ביקורת שגויה';
}

function urlEncodeDecode(text, direction) {
    try {
        if (direction === 'decode') return `🔗 Decoded:\n${decodeURIComponent(text)}`;
        return `🔗 URL Encoded:\n${encodeURIComponent(text)}`;
    } catch (e) { return `שגיאה: ${e.message}`; }
}

function convertTimezone(time, from, to) {
    try {
        const zones = {
            'ישראל': 'Asia/Jerusalem', 'israel': 'Asia/Jerusalem', 'il': 'Asia/Jerusalem',
            'ניו יורק': 'America/New_York', 'new york': 'America/New_York', 'ny': 'America/New_York',
            'לונדון': 'Europe/London', 'london': 'Europe/London',
            'פריז': 'Europe/Paris', 'paris': 'Europe/Paris',
            'טוקיו': 'Asia/Tokyo', 'tokyo': 'Asia/Tokyo',
            'דובאי': 'Asia/Dubai', 'dubai': 'Asia/Dubai',
            'לוס אנג\'לס': 'America/Los_Angeles', 'la': 'America/Los_Angeles',
            'איסטנבול': 'Europe/Istanbul', 'istanbul': 'Europe/Istanbul', 'turkey': 'Europe/Istanbul',
            'ברלין': 'Europe/Berlin', 'berlin': 'Europe/Berlin',
            'utc': 'UTC', 'gmt': 'UTC'
        };
        const fromZone = zones[from.toLowerCase()] || from;
        const toZone = zones[to.toLowerCase()] || to;

        const now = new Date();
        const fromStr = now.toLocaleString('he-IL', { timeZone: fromZone, hour: '2-digit', minute: '2-digit' });
        const toStr = now.toLocaleString('he-IL', { timeZone: toZone, hour: '2-digit', minute: '2-digit' });
        return `🌍 כרגע:\n${from}: ${fromStr}\n${to}: ${toStr}`;
    } catch (e) { return `שגיאה: ${e.message}`; }
}

module.exports = { convertUnits, generatePassword, encodeDecodeBase64, convertNumber, convertColor, numberToRoman, validateIBAN, urlEncodeDecode, convertTimezone };
