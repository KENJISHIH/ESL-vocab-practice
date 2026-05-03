// vocab_manifest.js
// 統一登記所有單字資料：每筆 { semester, semesterLabel, week, dataVar, scriptSrc }
// 新增一週只要在這裡加一行，並在 index.html 載入對應的 _data.js
// 這份 manifest 會自動驅動週數下拉選單與 ALL 模式切換。

const VOCAB_MANIFEST = [
    // ─── 2025 Fall（沿用既有檔案）─────────────────────────
    { semester: '2025-fall',   semesterLabel: '2025 Fall',   week: 12, dataVar: 'week12Data', scriptSrc: 'week12_data.js' },
    { semester: '2025-fall',   semesterLabel: '2025 Fall',   week: 13, dataVar: 'week13Data', scriptSrc: 'week13_data.js' },
    { semester: '2025-fall',   semesterLabel: '2025 Fall',   week: 14, dataVar: 'week14Data', scriptSrc: 'week14_data.js' },
    { semester: '2025-fall',   semesterLabel: '2025 Fall',   week: 15, dataVar: 'week15Data', scriptSrc: 'week15_data.js' },
    { semester: '2025-fall',   semesterLabel: '2025 Fall',   week: 16, dataVar: 'week16Data', scriptSrc: 'week16_data.js' },
    { semester: '2025-fall',   semesterLabel: '2025 Fall',   week: 17, dataVar: 'week17Data', scriptSrc: 'week17_data.js' },
    { semester: '2025-fall',   semesterLabel: '2025 Fall',   week: 18, dataVar: 'week18Data', scriptSrc: 'week18_data.js' },
    { semester: '2025-fall',   semesterLabel: '2025 Fall',   week: 19, dataVar: 'week19Data', scriptSrc: 'week19_data.js' },

    // ─── 2026 Spring（由 tools/pdf_to_vocab.py + json_to_js.py 產出）──
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 1,  dataVar: 'spring2026Week1Data',  scriptSrc: 'spring2026_week01_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 2,  dataVar: 'spring2026Week2Data',  scriptSrc: 'spring2026_week02_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 3,  dataVar: 'spring2026Week3Data',  scriptSrc: 'spring2026_week03_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 4,  dataVar: 'spring2026Week4Data',  scriptSrc: 'spring2026_week04_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 5,  dataVar: 'spring2026Week5Data',  scriptSrc: 'spring2026_week05_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 6,  dataVar: 'spring2026Week6Data',  scriptSrc: 'spring2026_week06_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 7,  dataVar: 'spring2026Week7Data',  scriptSrc: 'spring2026_week07_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 8,  dataVar: 'spring2026Week8Data',  scriptSrc: 'spring2026_week08_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 9,  dataVar: 'spring2026Week9Data',  scriptSrc: 'spring2026_week09_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 12, dataVar: 'spring2026Week12Data', scriptSrc: 'spring2026_week12_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 13, dataVar: 'spring2026Week13Data', scriptSrc: 'spring2026_week13_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 14, dataVar: 'spring2026Week14Data', scriptSrc: 'spring2026_week14_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 15, dataVar: 'spring2026Week15Data', scriptSrc: 'spring2026_week15_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 16, dataVar: 'spring2026Week16Data', scriptSrc: 'spring2026_week16_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 17, dataVar: 'spring2026Week17Data', scriptSrc: 'spring2026_week17_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 19, dataVar: 'spring2026Week19Data', scriptSrc: 'spring2026_week19_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 20, dataVar: 'spring2026Week20Data', scriptSrc: 'spring2026_week20_data.js' },
    { semester: '2026-spring', semesterLabel: '2026 Spring', week: 21, dataVar: 'spring2026Week21Data', scriptSrc: 'spring2026_week21_data.js' },
];

// 考試範圍登記：將某個 semester 的若干週合併成一個快選選項
// 新增考試範圍只要在這裡加一行；buildWeekSelector 會自動長出選項
const EXAM_RANGES = [
    { semester: '2026-spring', id: 'midterm', label: '📝 期中考範圍 (W1-W9)',  weeks: [1, 2, 3, 4, 5, 6, 7, 8, 9] },
    { semester: '2026-spring', id: 'final',   label: '🎯 期末考範圍 (W12-W21)', weeks: [12, 13, 14, 15, 16, 17, 19, 20, 21] },
];

// 顯式 registry：頂層 const 不會自動掛上 window，要列名稱抓進來
const VOCAB_DATA = {
    // 2025 Fall
    week12Data, week13Data, week14Data, week15Data,
    week16Data, week17Data, week18Data, week19Data,
    // 2026 Spring
    spring2026Week1Data, spring2026Week2Data, spring2026Week3Data,
    spring2026Week4Data, spring2026Week5Data, spring2026Week6Data,
    spring2026Week7Data, spring2026Week8Data, spring2026Week9Data,
    spring2026Week12Data, spring2026Week13Data, spring2026Week14Data,
    spring2026Week15Data, spring2026Week16Data, spring2026Week17Data,
    spring2026Week19Data, spring2026Week20Data, spring2026Week21Data,
};

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
