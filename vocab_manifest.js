// vocab_manifest.js
// 統一登記所有單字資料：每筆 { semester, semesterLabel, week, dataVar, scriptSrc }
// 新增一週只要在這裡加一行，並在 index.html 載入對應的 _data.js
// 這份 manifest 會自動驅動週數下拉選單與 ALL 模式切換。

// VOCAB_MANIFEST:START
const VOCAB_MANIFEST = [
    // ─── 2025 Fall ───
    { semester: '2025-fall', semesterLabel: '2025 Fall', week: 12, dataVar: 'week12Data', scriptSrc: 'week12_data.js' },
    { semester: '2025-fall', semesterLabel: '2025 Fall', week: 13, dataVar: 'week13Data', scriptSrc: 'week13_data.js' },
    { semester: '2025-fall', semesterLabel: '2025 Fall', week: 14, dataVar: 'week14Data', scriptSrc: 'week14_data.js' },
    { semester: '2025-fall', semesterLabel: '2025 Fall', week: 15, dataVar: 'week15Data', scriptSrc: 'week15_data.js' },
    { semester: '2025-fall', semesterLabel: '2025 Fall', week: 16, dataVar: 'week16Data', scriptSrc: 'week16_data.js' },
    { semester: '2025-fall', semesterLabel: '2025 Fall', week: 17, dataVar: 'week17Data', scriptSrc: 'week17_data.js' },
    { semester: '2025-fall', semesterLabel: '2025 Fall', week: 18, dataVar: 'week18Data', scriptSrc: 'week18_data.js' },
    { semester: '2025-fall', semesterLabel: '2025 Fall', week: 19, dataVar: 'week19Data', scriptSrc: 'week19_data.js' },
    // ─── 2026 Spring ───
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 1, dataVar: 'spring2026Week1Data', scriptSrc: 'spring2026_week01_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 2, dataVar: 'spring2026Week2Data', scriptSrc: 'spring2026_week02_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 3, dataVar: 'spring2026Week3Data', scriptSrc: 'spring2026_week03_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 4, dataVar: 'spring2026Week4Data', scriptSrc: 'spring2026_week04_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 5, dataVar: 'spring2026Week5Data', scriptSrc: 'spring2026_week05_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 6, dataVar: 'spring2026Week6Data', scriptSrc: 'spring2026_week06_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 7, dataVar: 'spring2026Week7Data', scriptSrc: 'spring2026_week07_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 8, dataVar: 'spring2026Week8Data', scriptSrc: 'spring2026_week08_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 9, dataVar: 'spring2026Week9Data', scriptSrc: 'spring2026_week09_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 12, dataVar: 'spring2026Week12Data', scriptSrc: 'spring2026_week12_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 13, dataVar: 'spring2026Week13Data', scriptSrc: 'spring2026_week13_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 14, dataVar: 'spring2026Week14Data', scriptSrc: 'spring2026_week14_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 15, dataVar: 'spring2026Week15Data', scriptSrc: 'spring2026_week15_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 16, dataVar: 'spring2026Week16Data', scriptSrc: 'spring2026_week16_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 17, dataVar: 'spring2026Week17Data', scriptSrc: 'spring2026_week17_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 19, dataVar: 'spring2026Week19Data', scriptSrc: 'spring2026_week19_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 20, dataVar: 'spring2026Week20Data', scriptSrc: 'spring2026_week20_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 21, dataVar: 'spring2026Week21Data', scriptSrc: 'spring2026_week21_data.js' },
    // ─── 2026 Fall ───
    { semester: '2026-fall', semesterLabel: '2026 Fall', week: 1, dataVar: 'fall2026Week1Data', scriptSrc: 'fall2026_week01_data.js' },
    { semester: '2026-fall', semesterLabel: '2026 Fall', week: 2, dataVar: 'fall2026Week2Data', scriptSrc: 'fall2026_week02_data.js' },
];
// VOCAB_MANIFEST:END

// 考試範圍登記：將某個 semester 的若干週合併成一個快選選項
// 新增考試範圍只要在這裡加一行；buildWeekSelector 會自動長出選項
const EXAM_RANGES = [
    { semester: '2026-spring', id: 'midterm', label: '📝 期中考範圍 (W1-W9)',  weeks: [1, 2, 3, 4, 5, 6, 7, 8, 9] },
    { semester: '2026-spring', id: 'final',   label: '🎯 期末考範圍 (W12-W21)', weeks: [12, 13, 14, 15, 16, 17, 19, 20, 21] },
    { semester: '2026-spring', id: 'review1316', label: '📘 複習 (W13-W16)', weeks: [13, 14, 15, 16] },
];

// VOCAB_DATA:START
// 顯式 registry：頂層 const 不會自動掛上 window，要列名稱抓進來
const VOCAB_DATA = {
    // 2025 Fall
    week12Data,
    week13Data,
    week14Data,
    week15Data,
    week16Data,
    week17Data,
    week18Data,
    week19Data,
    // 2026 Spring
    spring2026Week1Data,
    spring2026Week2Data,
    spring2026Week3Data,
    spring2026Week4Data,
    spring2026Week5Data,
    spring2026Week6Data,
    spring2026Week7Data,
    spring2026Week8Data,
    spring2026Week9Data,
    spring2026Week12Data,
    spring2026Week13Data,
    spring2026Week14Data,
    spring2026Week15Data,
    spring2026Week16Data,
    spring2026Week17Data,
    spring2026Week19Data,
    spring2026Week20Data,
    spring2026Week21Data,
    // 2026 Fall
    fall2026Week1Data,
    fall2026Week2Data,
};
// VOCAB_DATA:END

// ─── 每日進度計畫 ────────────────────────────────────────
// 老師規定每天背 2 個字，照該週單字表的順序切：
//   Day1 = 第 1-2 個字、Day2 = 第 3-4 個字 … Day5 = 第 9-10 個字
// 錨點：2026-08-31（一）＝ 2026 Fall W1 Day1
// 換學期只要改 semester 與 startDate（startDate 必須是該學期 W1 的星期一）
const DAILY_PLAN = {
    semester: '2026-fall',
    startDate: '2026-08-31',
    wordsPerDay: 2,
    daysPerWeek: 5,   // Day1=週一 … Day5=週五；週末不推進，當成該週的複習日
    // 幾點才換成新的一天（0–23）。老師下午才上 ESL 課教新字，所以中午以前還停在
    // 前一天那兩個字（早上正好複習昨天教的），過了這個鐘點才換成今天新教的。
    // 設 0 就是午夜換日。ESL 課的時間有變就改這個數字。
    dayStartsAtHour: 12,
    // 放假的平日（國定假日、颱風假…）。純標示用：那天改成複習整週、不催她背新字。
    // 週次是照日曆週算的，所以填不填都「不會」影響 W?/Day? 的對齊，可以安心留空。
    // 2026 Fall 學期內落在平日的國定假日（皆為星期五）：
    skipDates: [
        '2026-09-25',   // 中秋節
        '2026-10-09',   // 國慶連假補假
        '2027-01-01',   // 元旦
    ],
};

// 本地時區的 YYYY-MM-DD（不能用 toISOString，那是 UTC 會差一天）
function localISODate(d) {
    const p = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

// 「學習日」＝往前推 dayStartsAtHour 小時之後的那一天。
// 老師下午才教新字，所以中午以前算前一天：早上打開看到的是昨天教的兩個字（正好複習），
// 過了中午才換成今天新教的。整個 App 的「今天」一律走這個，不要直接用 new Date()。
function studyDate(now) {
    const d = new Date(now || new Date());
    d.setHours(d.getHours() - (DAILY_PLAN.dayStartsAtHour || 0));
    return d;
}

function studyDateISO(now) {
    return localISODate(studyDate(now));
}

// 算出今天屬於第幾週、星期幾（回傳 null 代表學期還沒開始）
//
// ⚠️ 一定要用「日曆週」算，不能用「累計上課日 ÷ 5」：
// 老師的 W1/W2/W3 是照日曆週編號的，放假不會讓週次順延（例如 2026-09-25 中秋節
// 放假，下週一還是 W5 Day1，不會變成 W4 Day5）。用累計上課日的話，只要遇到一天
// 國定假日，之後整學期的週次就全部偏掉，而且畫面上看不出來。
function weekAndDay(startISO, today) {
    const start = new Date(startISO + 'T00:00:00');   // 必須是 W1 的星期一
    const cur = new Date(localISODate(today) + 'T00:00:00');
    if (cur < start) return null;

    // 回推到 cur 所屬那一週的星期一（週日算成該週最後一天）
    const dow = cur.getDay();                      // 0=日 1=一 … 6=六
    const monday = new Date(cur);
    monday.setDate(monday.getDate() - (dow === 0 ? 6 : dow - 1));

    const weekNo = Math.round((monday - start) / (7 * 86400000)) + 1;
    // 平日 Day1–Day5；週末不推進，停在 Day5
    const dayInWeek = (dow >= 1 && dow <= 5) ? dow : DAILY_PLAN.daysPerWeek;
    return { weekNo, dayInWeek };
}

// 算出今天該背哪兩個字
// 回傳 status: 'not-started' 學期未開始 / 'no-data' 該週單字還沒匯入 / 'ok'
function getTodayPlan(now) {
    // 一律用「學習日」而不是牆上的日期：中午前算前一天
    const eff = studyDate(now);
    const effISO = localISODate(eff);
    const dow = eff.getDay();
    const isWeekend = (dow === 0 || dow === 6);
    const isHoliday = (DAILY_PLAN.skipDates || []).includes(effISO);
    const isRestDay = isWeekend || isHoliday;   // 不加新字、改複習的日子

    const wd = weekAndDay(DAILY_PLAN.startDate, eff);
    if (!wd) return { status: 'not-started', isWeekend, isHoliday, isRestDay };

    const { weekNo, dayInWeek } = wd;
    const base = { weekNo, dayInWeek, isWeekend, isHoliday, isRestDay, dateISO: effISO };

    const entry = VOCAB_MANIFEST.find(e => e.semester === DAILY_PLAN.semester && e.week === weekNo);
    const all = entry ? VOCAB_DATA[entry.dataVar] : null;
    if (!Array.isArray(all)) return { ...base, status: 'no-data' };

    const from = (dayInWeek - 1) * DAILY_PLAN.wordsPerDay;
    return {
        ...base,
        status: 'ok',
        words: all.slice(from, from + DAILY_PLAN.wordsPerDay),   // 今天的新字
        soFar: all.slice(0, from + DAILY_PLAN.wordsPerDay),      // 本週到今天累積（週末複習用）
        weekWords: all,                                          // 整週，給 Quiz 當誘答選項池
    };
}

// 全站所有單字攤平（給「複習錯過的字」用）
function allWordsFlat() {
    let out = [];
    VOCAB_MANIFEST.forEach(e => {
        const arr = VOCAB_DATA[e.dataVar];
        if (Array.isArray(arr)) out = out.concat(arr);
    });
    return out;
}

// 取出每個 semester 的標籤（保持登記順序）
function getSemesters() {
    const seen = new Set();
    const out = [];
    VOCAB_MANIFEST.forEach(e => {
        if (!seen.has(e.semester)) {
            seen.add(e.semester);
            out.push({ semester: e.semester, label: e.semesterLabel });
        }
    });
    return out;
}

// 依 select 的 value 查資料：
//   "2026-spring:5"        → 單一週
//   "all:2026-spring"      → 該 semester 全部週
//   "range:2026-spring:midterm" → 該 semester 預定義的考試範圍
function resolveSelection(value) {
    if (value.startsWith('all:')) {
        const sem = value.slice(4);
        const entries = VOCAB_MANIFEST.filter(e => e.semester === sem);
        let words = [];
        entries.forEach(e => {
            const arr = VOCAB_DATA[e.dataVar];
            if (Array.isArray(arr)) words = words.concat(arr);
        });
        return { kind: 'all', semester: sem, words };
    }
    if (value.startsWith('range:')) {
        const [, sem, rangeId] = value.split(':');
        const range = EXAM_RANGES.find(r => r.semester === sem && r.id === rangeId);
        if (!range) return null;
        let words = [];
        range.weeks.forEach(w => {
            const entry = VOCAB_MANIFEST.find(e => e.semester === sem && e.week === w);
            if (!entry) return;
            const arr = VOCAB_DATA[entry.dataVar];
            if (Array.isArray(arr)) words = words.concat(arr);
        });
        return { kind: 'range', semester: sem, rangeId, label: range.label, words };
    }
    const [sem, weekStr] = value.split(':');
    const entry = VOCAB_MANIFEST.find(e => e.semester === sem && e.week === Number(weekStr));
    if (!entry) return null;
    const arr = VOCAB_DATA[entry.dataVar];
    return Array.isArray(arr) ? { kind: 'week', semester: sem, week: entry.week, words: arr } : null;
}
