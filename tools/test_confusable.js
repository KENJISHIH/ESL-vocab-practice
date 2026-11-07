// 驗證「🔀 易混淆練習區」（confusable.js＋confusable_data.js）的純邏輯
// 載入真實單字資料檔 + manifest + dictation.js + confusable_sets.js + confusable.js 後跑一組斷言
// （寫法沿用 test_dictation.js）。用法：node tools/test_confusable.js
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '..');

let src = '';
for (const f of fs.readdirSync(ROOT).filter(n => n.endsWith('_data.js') && n !== 'shop_data.js').sort()) {
    src += fs.readFileSync(path.join(ROOT, f), 'utf8') + '\n';
}
for (const f of ['vocab_manifest.js', 'dictation.js', 'confusable_sets.js', 'confusable.js']) {
    src += fs.readFileSync(path.join(ROOT, f), 'utf8') + '\n';
}
// 注意：題庫檔刻意不叫 *_data.js，否則 tools/sync_manifest.py 會把它當成週次單字資料

const ctx = {};
vm.createContext(ctx);
vm.runInContext(src + '\nthis.__sets = CONFUSABLE_SETS;', ctx);
const SETS = ctx.__sets;

let pass = 0, fail = 0;
function ok(cond, note) {
    cond ? pass++ : fail++;
    console.log(`${cond ? '✅' : '❌'} ${note}`);
}

// 可重現的亂數（mulberry32），測試要穩定
function rngOf(seed) {
    let a = seed >>> 0;
    return () => {
        a = (a + 0x6D2B79F5) >>> 0;
        let t = a;
        t = Math.imul(t ^ (t >>> 15), t | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
}

console.log('=== 題庫格式 ===');
const wordSet = new Set(vm.runInContext('allWordsFlat().map(w => w.word.toLowerCase())', ctx));
const issues = vm.runInContext('confValidateSets(CONFUSABLE_SETS, new Set(allWordsFlat().map(w => w.word.toLowerCase())))', ctx);
ok(issues.length === 0, `題庫格式檢查沒有問題${issues.length ? '：\n   ' + issues.join('\n   ') : ''}`);

const byId = Object.fromEntries(SETS.map(s => [s.id, s]));
ok(byId['scratch-stretchy'].questions.length >= 8, `scratch／stretchy ${byId['scratch-stretchy'].questions.length} 題（要求 ≥8）`);
ok(byId['protect-predator'].questions.length >= 6, `protect／predator ${byId['protect-predator'].questions.length} 題（要求 ≥6）`);
ok(byId['giggle-shiver'].questions.length >= 6, `giggle／shiver／snuggle ${byId['giggle-shiver'].questions.length} 題（要求 ≥6）`);
ok(byId['giggle-shiver'].questions.some(q => q.o.length === 3), 'giggle／shiver 有三選一的題');
ok(SETS.length >= 5, `共 ${SETS.length} 組字對（指定 3 組＋至少 2 組自選）`);

console.log('\n=== 題目品質（機器能查的部分；語意唯一性已人工逐題審過）===');
let nonUniq = 0, ansNotInOpts = 0, noBase = 0;
const baseWords = new Set();
for (const s of SETS) {
    for (const q of s.questions) {
        if (!q.o.includes(q.a)) ansNotInOpts++;
        if (!wordSet.has(q.base)) noBase++;
        baseWords.add(q.base);
        // 其他選項不可等於正解
        if (q.o.filter(x => x === q.a).length !== 1) nonUniq++;
    }
}
ok(ansNotInOpts === 0, '每題選項都含正解');
ok(nonUniq === 0, '每題正解在選項中剛好出現一次');
ok(noBase === 0, `每題 base 都是單字資料裡的字（${[...baseWords].join('、')}）→ 答錯時能進「🔁 複習錯過的字」`);
// 每組的 words 都在 W1–W9（fall 2026）出現過
const w19 = new Set();
for (let w = 1; w <= 9; w++) {
    const arr = vm.runInContext(`fall2026Week${w}Data.map(x => x.word.toLowerCase())`, ctx);
    arr.forEach(x => w19.add(x));
}
const outside = SETS.flatMap(s => s.words.map(w => w.w)).filter(w => !w19.has(w));
ok(outside.length === 0, `所有字對單字都在 2026 Fall W1–W9 範圍內${outside.length ? '（不在：' + outside.join(',') + '）' : ''}`);

console.log('\n=== 填入正解的完整句子 ===');
const f1 = ctx.confFilledSentence(byId['scratch-stretchy'].questions[0]);
ok(f1 === 'The cat scratched my hand with its sharp claws.', `提示括號被拿掉：「${f1}」`);
const f2 = ctx.confFilledSentence(byId['scratch-stretchy'].questions[1]);
ok(f2 === 'You can pull a stretchy rubber band to make it longer.', `沒有提示的句子：「${f2}」`);
const sp = ctx.confSplitSentence(byId['scratch-stretchy'].questions[0]);
ok(sp.before === 'The cat ' && sp.hint === '(ed)' && sp.after.startsWith(' my hand'), `句子拆成 before／hint／after（hint=${sp.hint}）`);
const sp2 = ctx.confSplitSentence(byId['scratch-stretchy'].questions[1]);
ok(sp2.hint === '', '沒有提示的句子 hint 為空字串');

console.log('\n=== 出題 ===');
const one = ctx.confBuildRound(SETS, 'scratch-stretchy', rngOf(1));
ok(one.length === byId['scratch-stretchy'].questions.length, `單一字對：全部 ${one.length} 題都出`);
ok(new Set(one.map(q => q.s)).size === one.length, '單一字對：題目不重複');
ok(one.every(q => q.setId === 'scratch-stretchy' && q.retry === false), '題目帶 setId、retry=false');

const all = ctx.confBuildRound(SETS, 'all', rngOf(2));
ok(all.length === 10, `全部混合：${all.length} 題（上限 10）`);
ok(new Set(all.map(q => q.setId)).size === Math.min(SETS.length, 10), `全部混合：每組字對都有出題（${new Set(all.map(q => q.setId)).size}/${SETS.length} 組）`);
ok(new Set(all.map(q => q.s)).size === all.length, '全部混合：題目不重複');
let maxRun = 1, run = 1;
for (let i = 1; i < all.length; i++) { run = all[i].base === all[i - 1].base ? run + 1 : 1; maxRun = Math.max(maxRun, run); }
ok(maxRun <= 2, `全部混合：同一個單字最多連續 ${maxRun} 題（≤2）`);

console.log('\n=== 選項洗牌：不洩答案位置（跑 300 輪統計）===');
const posCount = { 2: [0, 0], 3: [0, 0, 0] };
for (let i = 0; i < 300; i++) {
    const r = ctx.confBuildRound(SETS, 'giggle-shiver', rngOf(100 + i));
    for (const q of r) {
        if (q.options.length === 3 || q.options.length === 2) posCount[q.options.length][q.options.indexOf(q.a)]++;
    }
    ok.__noop = 0;
}
const pc2 = posCount[2], pc3 = posCount[3];
const tot2 = pc2[0] + pc2[1], tot3 = pc3[0] + pc3[1] + pc3[2];
ok(Math.min(...pc2) / tot2 > 0.4, `二選一：正解在第 1／2 個的比例 ${(pc2[0] / tot2 * 100).toFixed(0)}% / ${(pc2[1] / tot2 * 100).toFixed(0)}%（各約 50%）`);
ok(Math.min(...pc3) / tot3 > 0.27, `三選一：正解在第 1／2／3 個的比例 ${pc3.map(x => (x / tot3 * 100).toFixed(0) + '%').join(' / ')}（各約 33%）`);
// 洗牌後選項集合不變、原題庫不被改動
const before = JSON.stringify(SETS);
const r1 = ctx.confBuildRound(SETS, 'all', rngOf(7));
ok(JSON.stringify(SETS) === before, '出題不會改動題庫原資料');
ok(r1.every(q => [...q.options].sort().join() === [...q.o].sort().join()), '洗牌後選項集合與原題庫相同');

console.log('\n=== 答錯重現（retry 複本）===');
const rc = ctx.confRetryCopy(one[0], rngOf(3));
ok(rc.retry === true && rc.a === one[0].a && [...rc.options].sort().join() === [...one[0].o].sort().join(), 'retry 複本：標記 retry、同一正解、選項集合不變');
ok(one[0].retry === false, '原題不受影響');

console.log('\n=== 拼字批改（不容錯，只忽略大小寫與頭尾空白）===');
const qs = byId['scratch-stretchy'].questions[0];   // 正解 scratched
ok(ctx.confCheckSpelling('scratched', qs).ok, 'scratched ✓');
ok(ctx.confCheckSpelling('  Scratched ', qs).ok, '大小寫與頭尾空白不計');
ok(!ctx.confCheckSpelling('scratch', qs).ok, 'scratch（少 ed）✗');
ok(!ctx.confCheckSpelling('scrached', qs).ok, 'scrached（少 t）✗');
ok(!ctx.confCheckSpelling('stretchy', qs).ok, 'stretchy（另一個字）✗');
ok(!ctx.confCheckSpelling('', qs).ok, '空白 ✗');
const dd = ctx.confCheckSpelling('scrached', qs).diff;
ok(dd && dd.want.filter(c => !c.ok).length === 1 && dd.want.filter(c => !c.ok)[0].ch === 't', 'scrached vs scratched：差異只有漏掉的 t');

console.log('\n=== 對照卡差異字母 ===');
const cd = ctx.confCardDiff('scratched', 'stretchy');
ok(cd.got.length === 9 && cd.want.length === 8, 'scratched／stretchy 逐字元對齊');
ok(cd.got.some(c => !c.ok) && cd.want.some(c => !c.ok), '兩邊都有沒對上（要標色）的字母');
const cd2 = ctx.confCardDiff('scratch', 'scratch');
ok(cd2.got.every(c => c.ok), '相同的字沒有差異');

console.log('\n=== 成績 ===');
const sc = ctx.confScore([{ ok: true }, { ok: false }, { ok: true }]);
ok(sc.right === 2 && sc.total === 3, '成績 2/3');

console.log(`\n通過 ${pass} 項，失敗 ${fail} 項`);
process.exit(fail ? 1 : 0);
