// 驗證 DAILY_PLAN 的週次／日期運算：載入真實資料檔 + manifest 後跑一組斷言
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(process.env.HOME, 'Documents/KJ-agent/esl-vocab-practice');

let src = '';
for (const f of fs.readdirSync(ROOT).filter(n => n.endsWith('_data.js')).sort()) {
    src += fs.readFileSync(path.join(ROOT, f), 'utf8') + '\n';
}
src += fs.readFileSync(path.join(ROOT, 'vocab_manifest.js'), 'utf8');

const ctx = {};
vm.createContext(ctx);
vm.runInContext(src, ctx);

const DAYS = ['日', '一', '二', '三', '四', '五', '六'];
const plan = iso => ctx.getTodayPlan(new Date(iso + 'T12:00:00'));

let pass = 0, fail = 0;
function check(iso, expWeek, expDay, note = '') {
    const p = plan(iso);
    const d = new Date(iso + 'T12:00:00');
    const got = `W${p.weekNo} Day${p.dayInWeek}`;
    const exp = `W${expWeek} Day${expDay}`;
    const flags = [p.isHoliday && '放假', p.isWeekend && '週末'].filter(Boolean).join('/');
    const ok = got === exp;
    ok ? pass++ : fail++;
    console.log(`${ok ? '✅' : '❌'} ${iso}(${DAYS[d.getDay()]}) → ${got.padEnd(10)}` +
        `${ok ? '' : ` 應為 ${exp}`}  ${flags ? '[' + flags + ']' : ''} ${note}`);
}

console.log('=== 每週起訖與跨週 ===');
check('2026-08-31', 1, 1, '學期第一天');
check('2026-09-04', 1, 5);
check('2026-09-05', 1, 5, '週六');
check('2026-09-06', 1, 5, '週日');
check('2026-09-07', 2, 1, '跨到 W2');

console.log('\n=== 國定假日不可以讓週次偏移（本次修正重點）===');
check('2026-09-25', 4, 5, '中秋節放假');
check('2026-09-28', 5, 1, '★ 假日隔週一必須是 W5 Day1');
check('2026-10-09', 6, 5, '國慶補假');
check('2026-10-12', 7, 1, '★ 仍須是 W7 Day1');
check('2027-01-01', 18, 5, '元旦');
check('2027-01-04', 19, 1, '★ 仍須是 W19 Day1');

console.log('\n=== 複習週／考試週照常計數，之後接得回來 ===');
check('2026-10-26', 9, 1);
check('2026-11-02', 10, 1, 'Review 週');
check('2026-11-09', 11, 1, '期中考週');
check('2026-11-16', 12, 1, '★ 必須接回 W12');
check('2027-01-11', 20, 1, 'Review 週');
check('2027-01-18', 21, 1, '期末考週');
check('2027-01-25', 22, 1, '★ 最後一週');

console.log('\n=== 中午換日（老師下午才教新字）===');
function checkAt(iso, hhmm, expWeek, expDay, note = '') {
    const d = new Date(`${iso}T${hhmm}:00`);
    const p = ctx.getTodayPlan(d);
    const got = `W${p.weekNo} Day${p.dayInWeek}`;
    const exp = `W${expWeek} Day${expDay}`;
    const ok = got === exp;
    ok ? pass++ : fail++;
    console.log(`${ok ? '✅' : '❌'} ${iso} ${hhmm} → ${got.padEnd(10)}${ok ? '' : ` 應為 ${exp}`}  ${note}`);
}
checkAt('2026-09-01', '07:30', 1, 1, '上學前 → 還是昨天教的字');
checkAt('2026-09-01', '11:59', 1, 1, '中午前一分鐘');
checkAt('2026-09-01', '12:00', 1, 2, '★ 中午整點換成今天新教的');
checkAt('2026-09-01', '19:00', 1, 2, '晚上寫作業');
checkAt('2026-09-02', '08:00', 1, 2, '隔天早上 → 仍是昨天的字');
checkAt('2026-09-02', '13:00', 1, 3, '隔天下午 → 換 Day3');
checkAt('2026-09-07', '09:00', 1, 5, '週一早上 → 還在上週複習');
checkAt('2026-09-07', '15:00', 2, 1, '★ 週一下午 → 才進 W2 Day1');

console.log('\n=== 邊界 ===');
const before = plan('2026-08-30');
console.log(`${before.status === 'not-started' ? '✅' : '❌'} 2026-08-30(日) → status=${before.status}（學期未開始）`);
before.status === 'not-started' ? pass++ : fail++;

const w10 = plan('2026-11-02');
console.log(`${w10.status === 'no-data' ? '✅' : '❌'} 2026-11-02 W10 → status=${w10.status}（尚無單字，預期 no-data）`);
w10.status === 'no-data' ? pass++ : fail++;

console.log(`\n通過 ${pass} 項，失敗 ${fail} 項`);
process.exit(fail ? 1 : 0);
