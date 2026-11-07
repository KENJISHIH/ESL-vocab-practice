// confusable.js — 「🔀 易混淆練習區」的純邏輯：驗證題庫、出題、選項洗牌、對照卡差異字母、拼字批改
// 資料在 confusable_sets.js；畫面與進度（金幣、錯題）在 index.html；這裡不碰 DOM。
// 需要先載入 dictation.js（拼字批改與逐字元對齊共用 isDictationCorrect／dictationCharDiff）。
// tools/test_confusable.js 用 node 直接載入測試。

const CONFUSABLE = {
    roundMax: 10,        // 「全部混合」一輪最多幾題
    maxSameRun: 2,       // 同一個正解單字最多連續出現幾題（避免連續猜同一個字）
    coins: 10,           // 選對一題的金幣（每個單字每天一次，沿用 recordAnswer）
};

const CONF_BLANK_RE = /____(?:\s*\([^)]*\))?/;   // 空格＋可選的 (ed) 這類提示

// Fisher–Yates 洗牌（rng 預設 Math.random，測試可傳固定亂數）
function confShuffle(arr, rng) {
    const r = rng || Math.random;
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(r() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
}

// 把空格換成正解（連同 (ed) 提示一起拿掉）→ 完整句子，用來播句子音檔、結果頁顯示
function confFilledSentence(q) {
    return q.s.replace(CONF_BLANK_RE, q.a);
}

// 句子拆成 {before, hint, after}，畫面在中間放空格
function confSplitSentence(q) {
    const m = q.s.match(CONF_BLANK_RE);
    if (!m) return { before: q.s, hint: '', after: '' };
    return {
        before: q.s.slice(0, m.index),
        hint: m[0].replace(/^_+\s*/, '').trim(),     // 例如 "(ed)"，沒有就是 ""
        after: q.s.slice(m.index + m[0].length),
    };
}

// 檢查題庫格式；回傳問題清單（空陣列＝沒問題）。wordSet 傳單字資料的小寫單字集合可檢查單字存在
function confValidateSets(sets, wordSet) {
    const issues = [];
    const ids = new Set();
    const sentences = new Set();
    sets.forEach(set => {
        if (!set.id || ids.has(set.id)) issues.push(`字對 id 缺少或重複：${set.id}`);
        ids.add(set.id);
        if (!Array.isArray(set.words) || set.words.length < 2) issues.push(`${set.id}：words 至少要 2 個`);
        (set.words || []).forEach(w => {
            ['w', 'show', 'pos', 'zh', 'tip'].forEach(k => { if (!w[k]) issues.push(`${set.id}/${w.w}：缺 ${k}`); });
            if (wordSet && !wordSet.has(String(w.w).toLowerCase())) issues.push(`${set.id}：單字 ${w.w} 不在單字資料裡`);
        });
        const bases = new Set((set.words || []).map(w => w.w));
        (set.questions || []).forEach((q, i) => {
            const tag = `${set.id}#${i + 1}`;
            const blanks = (q.s.match(/____/g) || []).length;
            if (blanks !== 1) issues.push(`${tag}：句子要剛好 1 個空格（現在 ${blanks}）`);
            if (!Array.isArray(q.o) || q.o.length < 2 || q.o.length > 3) issues.push(`${tag}：選項要 2～3 個`);
            else {
                if (new Set(q.o).size !== q.o.length) issues.push(`${tag}：選項重複`);
                if (q.o.filter(x => x === q.a).length !== 1) issues.push(`${tag}：選項裡要剛好有一個正解`);
            }
            if (!q.base || !bases.has(q.base)) issues.push(`${tag}：base 必須是這組字對的單字之一（${q.base}）`);
            if (!q.zh) issues.push(`${tag}：缺 zh（整句中文）`);
            if (!q.why) issues.push(`${tag}：缺 why（理由）`);
            if (sentences.has(q.s)) issues.push(`${tag}：句子重複`);
            sentences.add(q.s);
            if (/\(ed\)|\(ing\)|\(s\)/.test(confFilledSentence(q))) issues.push(`${tag}：填入正解後還殘留提示括號`);
        });
    });
    return issues;
}

// 單題選項洗牌；回傳新物件，不改動題庫原物件
function confPrepareQuestion(q, setId, rng) {
    return Object.assign({}, q, { setId, options: confShuffle(q.o, rng), retry: false });
}

// 同一個正解單字最多連續 maxSameRun 題；洗牌後試最多 30 次，仍不行就接受（題數少時可能無解）
function confSpreadRuns(list, rng) {
    let best = list;
    for (let t = 0; t < 30; t++) {
        const cand = t === 0 ? list : confShuffle(list, rng);
        let run = 1, bad = false;
        for (let i = 1; i < cand.length; i++) {
            run = cand[i].base === cand[i - 1].base ? run + 1 : 1;
            if (run > CONFUSABLE.maxSameRun) { bad = true; break; }
        }
        best = cand;
        if (!bad) break;
    }
    return best;
}

// 出一輪題：setId 指定字對＝該組全部題目；'all'＝每組輪流各抽，湊到 roundMax 題
function confBuildRound(sets, setId, rng) {
    if (setId !== 'all') {
        const set = sets.find(s => s.id === setId);
        if (!set) return [];
        const list = confShuffle(set.questions, rng).map(q => confPrepareQuestion(q, set.id, rng));
        return confSpreadRuns(list, rng);
    }
    const pools = sets.map(s => confShuffle(s.questions, rng).map(q => confPrepareQuestion(q, s.id, rng)));
    const out = [];
    let i = 0;
    while (out.length < CONFUSABLE.roundMax && pools.some(p => p.length)) {
        const p = pools[i % pools.length];
        if (p.length) out.push(p.shift());
        i++;
    }
    return confSpreadRuns(out, rng);
}

// 答錯的題稍後重現：另開一份（選項重新洗牌、標記 retry），不計入成績
function confRetryCopy(q, rng) {
    return Object.assign({}, q, { options: confShuffle(q.o, rng), retry: true });
}

// 對照卡兩個字的差異字母：沒對上的字元 ok=false（畫面標色）。只在剛好 2 個字時使用
function confCardDiff(a, b) {
    return dictationCharDiff(normalizeDictation(a), normalizeDictation(b));
}

// 拼字批改：不容錯，只忽略大小寫與頭尾空白（跟聽寫考試同一把尺）
function confCheckSpelling(typed, q) {
    const ok = isDictationCorrect(typed, q.a);
    return { ok, diff: ok ? null : dictationCharDiff(normalizeDictation(typed), normalizeDictation(q.a)) };
}

// 一輪的成績：results = [{ok}]（只含首次作答，不含重現題）
function confScore(results) {
    const right = results.filter(r => r.ok).length;
    return { right, total: results.length };
}
