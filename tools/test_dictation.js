// 驗證聽寫考試（dictation.js）的純邏輯：抽題比例、比對規則、範圍不足 10 字的行為、逐字元對齊
// 載入真實資料檔 + manifest + dictation.js 後跑一組斷言（寫法沿用 test_dailyplan.js）
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(process.env.HOME, 'Documents/KJ-agent/esl-vocab-practice');

let src = '';
for (const f of fs.readdirSync(ROOT).filter(n => n.endsWith('_data.js')).sort()) {
    src += fs.readFileSync(path.join(ROOT, f), 'utf8') + '\n';
}
src += fs.readFileSync(path.join(ROOT, 'vocab_manifest.js'), 'utf8') + '\n';
src += fs.readFileSync(path.join(ROOT, 'dictation.js'), 'utf8');

const ctx = {};
vm.createContext(ctx);
vm.runInContext(src, ctx);

let pass = 0, fail = 0;
function ok(cond, note) {
    cond ? pass++ : fail++;
    console.log(`${cond ? '✅' : '❌'} ${note}`);
}

const count = (arr, cat) => arr.filter(w => w.category === cat).length;

console.log('=== 旗標：只有 W4-W6 的兩個範圍開聽寫 ===');
const sp2 = ctx.resolveSelection('range:2026-fall:spelling2');
const mockA = ctx.resolveSelection('range:2026-fall:wrong_mockA');
const sp1 = ctx.resolveSelection('range:2026-fall:spelling1');
const w4 = ctx.resolveSelection('2026-fall:4');
ok(sp2.dictation === true, 'Spelling Check 2 (W4-W6) → dictation: true');
ok(mockA.dictation === true, '錯字集中營 → dictation: true');
ok(sp1.dictation === false, 'Spelling Check 1 (W1-W3) → 不開');
ok(w4.dictation === undefined, '單週 W4 → 沒有 dictation 欄位（selection.kind=week）');
ok(sp2.words.length === 30 && count(sp2.words, 'Reading') === 21 && count(sp2.words, 'Science') === 9,
    `W4-W6 共 ${sp2.words.length} 字（Reading ${count(sp2.words, 'Reading')} / Science ${count(sp2.words, 'Science')}）`);

console.log('\n=== 抽題：7 Reading + 3 Science，順序隨機，跑 200 次都要成立 ===');
let allGood = true, orderVaried = false, firstOrder = null;
for (let i = 0; i < 200; i++) {
    const picked = ctx.pickDictationWords(sp2.words);
    const keys = picked.map(w => w.word).join('|');
    if (firstOrder === null) firstOrder = keys; else if (keys !== firstOrder) orderVaried = true;
    const uniq = new Set(picked.map(w => w.word)).size === picked.length;
    if (!(picked.length === 10 && count(picked, 'Reading') === 7 && count(picked, 'Science') === 3 && uniq)) {
        allGood = false;
        console.log('   ✗ 這次抽到', picked.length, '字，Reading', count(picked, 'Reading'), 'Science', count(picked, 'Science'), '不重複', uniq);
        break;
    }
}
ok(allGood, '每次都是 10 題 = 7 Reading + 3 Science，無重複');
ok(orderVaried, '順序有洗牌（200 次不會全部同一個順序）');

console.log('\n=== 範圍不足 10 字：全部出、不補 ===');
const small = ctx.pickDictationWords(mockA.words);
ok(mockA.words.length === 7, `錯字集中營只有 ${mockA.words.length} 字`);
ok(small.length === 7, `抽出 ${small.length} 題（全部出）`);
ok(new Set(small.map(w => w.word)).size === 7 && mockA.words.every(w => small.includes(w)), '7 個字每個都有、沒重複');

console.log('\n=== 某一類別不夠配額時從另一類補到 10（範圍本身 ≥ 10 字才會這樣）===');
const lopsided = sp2.words.filter(w => w.category === 'Reading').slice(0, 12)
    .concat(sp2.words.filter(w => w.category === 'Science').slice(0, 1));
const lp = ctx.pickDictationWords(lopsided);
ok(lp.length === 10 && count(lp, 'Science') === 1 && count(lp, 'Reading') === 9,
    `12 Reading + 1 Science → 抽 ${lp.length} 題（Reading ${count(lp, 'Reading')} / Science ${count(lp, 'Science')}）`);

console.log('\n=== 比對：trim／小寫／連續空白縮一個，其餘必須完全相同 ===');
const C = (a, w) => ctx.isDictationCorrect(a, w);
ok(C('pajamas', 'pajamas'), 'pajamas = pajamas');
ok(C('  Pajamas ', 'pajamas'), '"  Pajamas " → 去頭尾空白、轉小寫後算對');
ok(C('PAJAMAS', 'pajamas'), '全大寫也算對');
ok(!C('pajame', 'pajamas'), 'pajame ≠ pajamas（不容錯）');
ok(!C('pajama', 'pajamas'), 'pajama ≠ pajamas（少一個 s 也不行）');
ok(!C('', 'pajamas'), '空白 ≠ pajamas');
ok(C('take  a   shower', 'take a shower'), '片語：連續空白縮成一個後整個比對');
ok(C('Take A Shower', 'take a shower'), '片語：大小寫不計');
ok(!C('take shower', 'take a shower'), '片語：少一個字就錯');
ok(!C('takeashower', 'take a shower'), '片語：沒打空白就錯');

console.log('\n=== 例句取第一句、剝掉「1. 」 ===');
const pj = sp2.words.find(w => w.word === 'pajamas');
const ex1 = ctx.dictationFirstExample(pj.ex);
ok(!/^\s*\d+\s*\./.test(ex1) && !/<br/i.test(ex1) && ex1.length > 0, `pajamas 第一句：「${ex1}」`);
ok(ctx.dictationFirstExample('1. Hello.<br>2. Bye.') === 'Hello.', '固定格式切得對');
ok(ctx.dictationFirstExample('') === '', '空字串不爆');

console.log('\n=== 逐字元對齊：標出差異字母 ===');
const d1 = ctx.dictationCharDiff('pajame', 'pajamas');
const wrongGot = d1.got.filter(p => !p.ok).map(p => p.ch).join('');
const missWant = d1.want.filter(p => !p.ok).map(p => p.ch).join('');
ok(wrongGot === 'e', `pajame vs pajamas：她多打／打錯的是「${wrongGot}」（應為 e）`);
ok(missWant === 'as', `pajame vs pajamas：正確拼法沒對上的是「${missWant}」（應為 as）`);
const d2 = ctx.dictationCharDiff('', 'larva');
ok(d2.got.length === 0 && d2.want.every(p => !p.ok), '沒寫 vs larva：正確那邊全部標出');
const d3 = ctx.dictationCharDiff('ambulence', 'ambulance');
ok(d3.got.filter(p => !p.ok).map(p => p.ch).join('') === 'e' && d3.want.filter(p => !p.ok).map(p => p.ch).join('') === 'a',
    'ambulence vs ambulance：只標 e / a 一個字母');

console.log('\n=== 批改：每字 7 分 ===');
const items = sp2.words.filter(w => ['pajamas', 'larva', 'ceiling'].includes(w.word));
const g = ctx.gradeDictation(items, items.map(w => w.word === 'larva' ? 'lava' : w.word.toUpperCase()));
ok(g.correct === 2 && g.score === 14 && g.maxScore === 21, `3 題對 2 → ${g.score}/${g.maxScore}`);
const g10 = ctx.gradeDictation(ctx.pickDictationWords(sp2.words), new Array(10).fill(''));
ok(g10.maxScore === 70 && g10.score === 0, '10 題全空 → 0/70');

console.log(`\n通過 ${pass} 項，失敗 ${fail} 項`);
process.exit(fail ? 1 : 0);
