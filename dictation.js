// dictation.js — 聽寫考試（Dictation）的純邏輯：抽題、比對、逐字元對齊
// 畫面與播音流程在 index.html；這裡不碰 DOM，tools/test_dictation.js 用 node 直接載入測試。
// 只有 EXAM_RANGES 裡標了 dictation: true 的範圍才會顯示聽寫入口（見 vocab_manifest.js）。

// ─── 可調參數（要改節奏改這裡）────────────────────────────
const DICTATION = {
    total: 10,           // 一次考幾個字；範圍不足就全部出，不補
    readingCount: 7,     // 其中 Reading 幾個
    scienceCount: 3,     // 其中 Science 幾個
    pauseMs: 20000,      // 每題唸完後留多久給她打字（2026-10-11 從 8 秒改 20 秒）
    stepGapMs: 400,      // 「Number N」→ 單字 → 例句 → 單字，每段之間停多久
    reviewGapMs: 1500,   // 最後快速重唸一輪時，每題之間停多久
    stepMaxMs: 12000,    // 單段播音最多等多久（音檔壞掉或 TTS 沒回 end 事件時不會卡死）
    wordRate: 0.85,      // 單字唸慢一點（音檔 playbackRate／TTS rate）
    pointsPerWord: 7,    // 每字幾分（10 字 = 70 分，照 Spelling Check 的算法）
    coins: 10,           // 每個答對的字給幾金幣（每字每天只給一次，沿用 recordAnswer）
};

// 洗牌：沿用站內既有寫法（sort + random）
function dictShuffle(arr, rng) {
    const r = rng || Math.random;
    return arr.slice().sort(() => r() - 0.5);
}

// 抽題：7 Reading + 3 Science，順序隨機。
//   範圍總數 ≤ total → 全部出（錯字集中營只有 7 個字就考 7 題）
//   某一類別不夠配額（例如 Science 只有 2 個）→ 先拿該類全部，再從剩下的字補到 total
function pickDictationWords(words, rng) {
    if (words.length <= DICTATION.total) return dictShuffle(words, rng);

    const reading = dictShuffle(words.filter(w => w.category === 'Reading'), rng);
    const science = dictShuffle(words.filter(w => w.category === 'Science'), rng);
    let picked = reading.slice(0, DICTATION.readingCount)
        .concat(science.slice(0, DICTATION.scienceCount));

    if (picked.length < DICTATION.total) {
        const rest = dictShuffle(words.filter(w => !picked.includes(w)), rng);
        picked = picked.concat(rest.slice(0, DICTATION.total - picked.length));
    }
    return dictShuffle(picked, rng);
}

// 比對前的正規化：去頭尾空白、轉小寫、連續空白縮成一個。其餘必須完全相同（不容錯）。
function normalizeDictation(s) {
    return String(s == null ? '' : s).trim().toLowerCase().replace(/\s+/g, ' ');
}

function isDictationCorrect(answer, word) {
    return normalizeDictation(answer) === normalizeDictation(word);
}

// 例句取 ex 欄位 <br> 前的第一句，剝掉開頭的「1. 」（規則與 index.html 的 splitExamples 一致）
function dictationFirstExample(ex) {
    const first = String(ex || '').split(/<br\s*\/?>/i)[0] || '';
    return first.replace(/^\s*\d+\s*\.\s*/, '').trim();
}

// 逐字元對齊（LCS）：回傳兩邊每個字元是否「對上了」，沒對上的就是要標紅的差異
//   got  = 她寫的（正規化後）    want = 正確拼法（正規化後）
//   例：got 'pajame' vs want 'pajamas' → got 的 e 沒對上、want 的 a、s 沒對上
function dictationCharDiff(got, want) {
    const a = Array.from(got), b = Array.from(want);
    const n = a.length, m = b.length;
    const dp = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));
    for (let i = n - 1; i >= 0; i--) {
        for (let j = m - 1; j >= 0; j--) {
            dp[i][j] = a[i] === b[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
        }
    }
    const gotOut = a.map(ch => ({ ch, ok: false }));
    const wantOut = b.map(ch => ({ ch, ok: false }));
    let i = 0, j = 0;
    while (i < n && j < m) {
        if (a[i] === b[j]) { gotOut[i].ok = true; wantOut[j].ok = true; i++; j++; }
        else if (dp[i + 1][j] >= dp[i][j + 1]) i++;
        else j++;
    }
    return { got: gotOut, want: wantOut };
}

// 整份批改：回傳每題結果與總分
function gradeDictation(items, answers) {
    const rows = items.map((item, i) => {
        const got = normalizeDictation(answers[i]);
        const want = normalizeDictation(item.word);
        const ok = got === want;
        return { item, got, want, ok, diff: ok ? null : dictationCharDiff(got, want) };
    });
    const correct = rows.filter(r => r.ok).length;
    return {
        rows,
        correct,
        score: correct * DICTATION.pointsPerWord,
        maxScore: items.length * DICTATION.pointsPerWord,
    };
}
