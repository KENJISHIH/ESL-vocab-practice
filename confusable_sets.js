// confusable_sets.js — 「🔀 易混淆練習區」的字對資料
// 要加新字對：照下面格式在 CONFUSABLE_SETS 陣列末尾加一組，然後
//   1) node tools/test_confusable.js          （檢查題目格式：空格、選項、base 單字都存在）
//   2) /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 tools/gen_confusable_tts.py    （補變化形單字與例句音檔，沒音檔 iPad 會無聲）
//   3) sw.js 的 CACHE 跳版
//
// 格式：
//   id      字對代號（英文，唯一）
//   title   列表上顯示的標題
//   why     為什麼容易混淆（給家長看，寫在對照卡上）
//   words   每個字一筆：w 原形（要在 W1–W9 單字資料裡，音檔 audio/<w>.m4a）、pos、zh、tip、
//           show 對照卡上的大字（可以是變化形，像 scratched）、forms 對照卡上可按 🔈 的變化形
//   questions 每題一筆：
//     s     句子，空格寫 ____，需要變化形時空格後面接 (ed)／(ing)／(s) 提示
//     a     正解（空格要填的完整形式）
//     o     選項（含正解；會在畫面上洗牌）。**其他選項代進空格後，語意或文法都要不通**，只留唯一答案
//     base  這題考的單字原形（答錯時記進「🔁 複習錯過的字」）
//     zh    整句中文意思（答完才顯示，不先洩答案）
//     why   答對／答錯後顯示的理由（中文）
//
// ⚠️ 檔名刻意不叫 *_data.js：tools/sync_manifest.py 會把 *_data.js 全當週次單字資料接進前端。
// 例句一律自編，不抄課本或老師考卷（這是公開站，見 README 版權註記）。

const CONFUSABLE_SETS = [
    // ① Kenji 指定：2026-11-07 複習時發現心心常把這兩個字搞混（長得像：s‧tr/scr ＋ tch）
    {
        id: 'scratch-stretchy',
        title: 'scratch ／ stretchy',
        why: '兩個字都有 s、t、r、tch，連我們大人都看花眼。差別：scratch 是「動作」（抓），stretchy 是「形容詞」（有彈性）。',
        words: [
            { w: 'scratch', show: 'scratched', pos: 'v.', zh: '抓（癢）；刮出痕跡', tip: '動作：用指甲或爪子抓。scr‧a‧tch，中間是 a。', forms: ['scratch', 'scratched', 'scratching'] },
            { w: 'stretchy', show: 'stretchy', pos: 'adj.', zh: '有彈性的；可以拉長的', tip: '形容東西：像橡皮筋能拉長。str‧e‧tch‧y，中間是 e，結尾 y，不加 ed／ing。', forms: ['stretchy'] },
        ],
        questions: [
            { s: 'The cat ____ (ed) my hand with its sharp claws.', a: 'scratched', o: ['scratched', 'stretchy'], base: 'scratch',
              zh: '貓用尖尖的爪子抓了我的手。', why: '這裡要「動詞過去式」。貓用爪子抓 → scratched；stretchy 是形容詞，不能當動作。' },
            { s: 'You can pull a ____ rubber band to make it longer.', a: 'stretchy', o: ['scratched', 'stretchy'], base: 'stretchy',
              zh: '你可以把有彈性的橡皮筋拉長。', why: '拉長 → 有彈性 → stretchy（形容 rubber band）。scratched 是「被抓過」，不能拉長。' },
            { s: 'Please do not ____ the table with your fork.', a: 'scratch', o: ['scratch', 'stretchy'], base: 'scratch',
              zh: '請不要用叉子刮傷桌子。', why: 'do not 後面要接「動詞原形」→ scratch（刮出痕跡）。' },
            { s: 'My dog is ____ (ing) its ear because it itches.', a: 'scratching', o: ['scratching', 'stretchy'], base: 'scratch',
              zh: '我的狗在抓牠的耳朵，因為很癢。', why: 'is 後面是進行式 -ing；癢了才會抓 → scratching。' },
            { s: 'I wear ____ pants when I dance, so I can move easily.', a: 'stretchy', o: ['scratching', 'stretchy'], base: 'stretchy',
              zh: '我跳舞時穿有彈性的褲子，這樣動作才方便。', why: '褲子要「能拉長、好活動」→ stretchy，放在名詞 pants 前面當形容詞。' },
            { s: 'Gum is sticky and ____. You can pull it very long.', a: 'stretchy', o: ['scratched', 'stretchy'], base: 'stretchy',
              zh: '口香糖黏黏的又有彈性，你可以把它拉得很長。', why: '後面說「可以拉很長」→ stretchy。' },
            { s: 'My brother fell down and ____ (ed) his knee.', a: 'scratched', o: ['scratched', 'stretchy'], base: 'scratch',
              zh: '我弟弟跌倒了，刮傷了膝蓋。', why: '跌倒、膝蓋被刮傷是「動作」且已經發生 → 過去式 scratched。' },
            { s: 'The sweater is ____, so it fits both big and small kids.', a: 'stretchy', o: ['scratched', 'stretchy'], base: 'stretchy',
              zh: '這件毛衣很有彈性，所以大孩子和小孩子都穿得下。', why: '大小孩都穿得下，是因為會被拉長 → stretchy。' },
            { s: 'The kitten likes to ____ the sofa.', a: 'scratch', o: ['scratch', 'stretchy'], base: 'scratch',
              zh: '小貓喜歡抓沙發。', why: 'likes to 後面要接「動詞原形」→ scratch。' },
        ],
    },

    // ② 她 11/4 Reading 複習卷把 protect 寫成 predator（聽寫＋填空都錯）
    {
        id: 'protect-predator',
        title: 'protect ／ predator',
        why: '兩個字都是 pr 開頭、有 t，聽起來也像。protect 是動詞「保護」，predator 是名詞「掠食者」（會抓別的動物來吃）。',
        words: [
            { w: 'protect', show: 'protect', pos: 'v.', zh: '保護', tip: '動詞：不讓人或東西受傷。pro‧tect。', forms: ['protect', 'protects'] },
            { w: 'predator', show: 'predator', pos: 'n.', zh: '掠食者（會獵捕其他動物）', tip: '名詞：像獅子、鯊魚、老鷹。pred‧a‧tor，有 d。', forms: ['predator'] },
        ],
        questions: [
            { s: 'Sunglasses ____ your eyes from strong sunlight.', a: 'protect', o: ['protect', 'predator'], base: 'protect',
              zh: '太陽眼鏡保護你的眼睛不被強烈陽光傷害。', why: 'Sunglasses 後面要放「動詞」（複數主詞，不加 s）→ protect。predator 是名詞。' },
            { s: 'A lion is a ____. It hunts other animals for food.', a: 'predator', o: ['protect', 'predator'], base: 'predator',
              zh: '獅子是掠食者，牠獵捕其他動物當食物。', why: 'A lion is a ＋名詞；會獵捕別的動物 → predator。' },
            { s: 'A hard shell can ____ a turtle from danger.', a: 'protect', o: ['protect', 'predator'], base: 'protect',
              zh: '堅硬的殼可以保護烏龜遠離危險。', why: 'can 後面要接動詞原形 → protect。' },
            { s: 'The hawk is a ____ that hunts mice.', a: 'predator', o: ['protect', 'predator'], base: 'predator',
              zh: '老鷹是會獵捕老鼠的掠食者。', why: 'The hawk is a ＋名詞 → predator；protect 是動詞，放這裡不通。' },
            { s: 'I wear a helmet to ____ my head when I ride a bike.', a: 'protect', o: ['protect', 'predator'], base: 'protect',
              zh: '我騎腳踏車時戴安全帽來保護頭。', why: 'to 後面要接動詞原形 → protect。' },
            { s: 'A shark is a sea ____.', a: 'predator', o: ['protect', 'predator'], base: 'predator',
              zh: '鯊魚是海裡的掠食者。', why: 'sea 後面接名詞；鯊魚會獵捕魚 → predator。' },
            { s: 'This coat ____ (s) me from the cold wind.', a: 'protects', o: ['protects', 'predator'], base: 'protect',
              zh: '這件外套保護我不被冷風吹。', why: 'This coat 是單數主詞，動詞加 s → protects（保護）。' },
            { s: 'Mom said, “I will ____ you from the rain with my umbrella.”', a: 'protect', o: ['protect', 'predator'], base: 'protect',
              zh: '媽媽說：「我會用我的傘保護你不被雨淋到。」', why: 'will 後面要接動詞原形 → protect。' },
            { s: 'A frog should hide from a ____ like a snake.', a: 'predator', o: ['protect', 'predator'], base: 'predator',
              zh: '青蛙應該躲避像蛇這樣的掠食者。', why: 'a 後面要名詞；蛇會抓青蛙來吃 → predator。' },
        ],
    },

    // ③ 她 11/4 Reading 複習卷：joke 的句子填成 shivered、warm water 的句子填成 snuggleing
    {
        id: 'giggle-shiver',
        title: 'giggle ／ shiver ／ snuggle',
        why: '三個都是 -le／-er 結尾、很像的動作字。giggle＝好笑而笑，shiver＝冷或怕而發抖，snuggle＝舒服地靠在一起。看「為什麼」就能分。',
        words: [
            { w: 'giggle', show: 'giggle', pos: 'v.', zh: '咯咯地笑', tip: '因為好笑、開心。g‧ig‧gle。變化：giggled、giggling。', forms: ['giggle', 'giggled'] },
            { w: 'shiver', show: 'shiver', pos: 'v.', zh: '（因為冷或害怕）發抖', tip: '身體因為冷或怕在抖。變化：shivered、shivering。', forms: ['shiver', 'shivered', 'shivering'] },
            { w: 'snuggle', show: 'snuggle', pos: 'v.', zh: '舒服地依偎；縮成一團', tip: '抱著、靠著很舒服。去 e 加 ing：snuggling；加 ed：snuggled。', forms: ['snuggle', 'snuggled'] },
        ],
        questions: [
            { s: 'Mary ____ (ed) when her friend told her a funny joke.', a: 'giggled', o: ['giggled', 'shivered', 'snuggled'], base: 'giggle',
              zh: '朋友講了一個好笑的笑話，Mary 咯咯笑了起來。', why: 'funny joke（好笑的笑話）→ 笑 → giggled。shivered 是冷或怕發抖。' },
            { s: 'The boy stopped ____ (ing) after he put on a warm coat.', a: 'shivering', o: ['shivering', 'giggling', 'snuggling'], base: 'shiver',
              zh: '男孩穿上暖和的外套之後，就不再發抖了。', why: '穿暖外套，是因為剛才冷到發抖 → shivering。' },
            { s: 'It was so cold that Tom ____ (ed) all over.', a: 'shivered', o: ['shivered', 'giggled', 'snuggled'], base: 'shiver',
              zh: '天氣冷到 Tom 全身發抖。', why: 'so cold（好冷）→ 發抖 → shivered。' },
            { s: 'The happy baby ____ (ed) when I made a funny face.', a: 'giggled', o: ['giggled', 'shivered'], base: 'giggle',
              zh: '我扮鬼臉的時候，開心的寶寶咯咯地笑。', why: 'happy（開心）、funny face（好笑的鬼臉）→ giggled。' },
            { s: 'She hugged her teddy bear and ____ (ed) up in bed.', a: 'snuggled', o: ['snuggled', 'giggled', 'shivered'], base: 'snuggle',
              zh: '她抱著泰迪熊，舒服地縮在床上。', why: 'snuggle up 是固定說法：舒服地縮成一團、靠在一起。' },
            { s: 'Everyone ____ (ed) at the clown’s silly tricks.', a: 'giggled', o: ['giggled', 'shivered'], base: 'giggle',
              zh: '大家被小丑的傻把戲逗得咯咯笑。', why: 'silly tricks（傻把戲）→ 好笑 → giggled。' },
            { s: 'When I am scared of the dark, my hands ____.', a: 'shiver', o: ['shiver', 'giggle'], base: 'shiver',
              zh: '我怕黑的時候，雙手會發抖。', why: '主詞 my hands 是複數，動詞原形；怕 → 發抖 → shiver。手不會咯咯笑。' },
        ],
    },

    // ④ 字形像：cr____ch／cr____sh，都是「聲音很大」的動作字（單字本 W2 crunch、W6 crash）
    {
        id: 'crunch-crash',
        title: 'crunch ／ crash',
        why: 'cr 開頭、結尾只差 -unch／-ash。crunch＝咬或踩出「喀滋」聲，crash＝「碰」一聲撞上去。',
        words: [
            { w: 'crunch', show: 'crunch', pos: 'v.', zh: '嚼出喀滋聲；踩出沙沙聲', tip: '脆脆的東西被咬或被踩。cr‧unch，u 在中間。', forms: ['crunch', 'crunched'] },
            { w: 'crash', show: 'crash', pos: 'v.', zh: '猛烈撞上；撞毀', tip: '用力撞到東西，很大聲。cr‧ash，a 在中間。', forms: ['crash', 'crashed'] },
        ],
        questions: [
            { s: 'The squirrel ____ (ed) the nuts with its teeth.', a: 'crunched', o: ['crunched', 'crashed'], base: 'crunch',
              zh: '松鼠用牙齒把堅果咬得喀滋喀滋響。', why: '用牙齒咬脆的東西 → crunched；crash 是撞上去。' },
            { s: 'The car ____ (ed) into a tree.', a: 'crashed', o: ['crunched', 'crashed'], base: 'crash',
              zh: '車子撞上了一棵樹。', why: 'into a tree（撞進樹裡）→ crashed。' },
            { s: 'I love to ____ on crispy apples.', a: 'crunch', o: ['crunch', 'crash'], base: 'crunch',
              zh: '我愛咬脆脆的蘋果。', why: 'crispy（脆的）apples → 咬起來喀滋響 → crunch。' },
            { s: 'Be careful! The two bikes will ____ if you do not stop.', a: 'crash', o: ['crunch', 'crash'], base: 'crash',
              zh: '小心！你再不停下來，兩輛腳踏車會撞在一起。', why: 'will ＋原形；不停下來會撞 → crash。' },
            { s: 'Dry leaves ____ (ed) under my shoes.', a: 'crunched', o: ['crunched', 'crashed'], base: 'crunch',
              zh: '乾枯的葉子在我鞋子底下發出沙沙的脆響。', why: '踩乾葉子的「沙沙」聲 → crunched。leaves 不會「撞」。' },
            { s: 'The plane could ____ because of the storm.', a: 'crash', o: ['crunch', 'crash'], base: 'crash',
              zh: '因為暴風雨，飛機可能會墜毀。', why: 'could ＋原形；飛機出事 → crash。' },
        ],
    },

    // ⑤ 語意常搞混（Science，W5）：她的 Science 複習卷 A-10／B-2 就考 pupa 和 larva
    {
        id: 'larva-pupa',
        title: 'larva ／ pupa',
        why: '兩個都是昆蟲長大的「階段」，長得都不像大人。larva＝剛孵出來的小蟲（一直吃），pupa＝穿上硬殼不吃不動、裡面在變身。',
        words: [
            { w: 'larva', show: 'larva', pos: 'n.', zh: '幼蟲', tip: '剛孵出來，像小蟲（毛毛蟲）。一直吃東西長大。', forms: ['larva'] },
            { w: 'pupa', show: 'pupa', pos: 'n.', zh: '蛹', tip: '外面有硬殼，不吃不動，裡面正在變成成蟲。', forms: ['pupa'] },
        ],
        questions: [
            { s: 'A caterpillar is a butterfly ____.', a: 'larva', o: ['larva', 'pupa'], base: 'larva',
              zh: '毛毛蟲是蝴蝶的幼蟲。', why: 'caterpillar（毛毛蟲）就是剛孵出來、會一直吃的幼蟲 → larva。' },
            { s: 'The ____ is a hard case. The caterpillar changes inside it.', a: 'pupa', o: ['larva', 'pupa'], base: 'pupa',
              zh: '蛹是一個硬殼，毛毛蟲在裡面變身。', why: 'hard case（硬殼）→ pupa。' },
            { s: 'A butterfly egg hatches into a ____. It eats leaves all day.', a: 'larva', o: ['larva', 'pupa'], base: 'larva',
              zh: '蝴蝶的卵孵化成幼蟲，牠整天吃葉子。', why: '卵孵出來、一直吃葉子 → larva。' },
            { s: 'The caterpillar stops eating and makes a hard case. Now it is a ____.', a: 'pupa', o: ['larva', 'pupa'], base: 'pupa',
              zh: '毛毛蟲不吃東西了，做出一個硬殼，現在牠是蛹。', why: '停止進食、做出硬殼 → pupa。' },
            { s: 'Inside the case, the ____ slowly becomes an adult butterfly.', a: 'pupa', o: ['larva', 'pupa'], base: 'pupa',
              zh: '在硬殼裡面，蛹慢慢變成成年的蝴蝶。', why: 'Inside the case（在硬殼裡）→ pupa。' },
            { s: 'A ____ looks like a small worm and has no wings.', a: 'larva', o: ['larva', 'pupa'], base: 'larva',
              zh: '幼蟲看起來像一條小蟲，沒有翅膀。', why: '像小蟲、沒翅膀、會動會吃 → larva。' },
        ],
    },

    // ⑥ 語意常搞混（Science，W2/W3）：花的兩個部分，Science 複習卷 E 題「Pollen is made by this part of the flower」
    {
        id: 'petal-pollen',
        title: 'petal ／ pollen',
        why: '兩個都以 pe／po 開頭、都跟花有關。petal＝軟軟有顏色的「花瓣」，pollen＝花裡的黃色「花粉」，蜜蜂會帶走它。',
        words: [
            { w: 'petal', show: 'petal', pos: 'n.', zh: '花瓣', tip: '花朵外圈軟軟、有顏色的那一片。可以數：a petal、many petals。', forms: ['petal', 'petals'] },
            { w: 'pollen', show: 'pollen', pos: 'n.', zh: '花粉', tip: '花裡面的黃色粉末，用來做種子。是粉，不能數，不加 s。', forms: ['pollen'] },
        ],
        questions: [
            { s: 'The soft, colorful part of a flower is a ____.', a: 'petal', o: ['petal', 'pollen'], base: 'petal',
              zh: '花朵上柔軟又有顏色的部分是花瓣。', why: '柔軟、有顏色的部分 → 花瓣 petal。' },
            { s: 'Bees carry yellow powder called ____ from flower to flower.', a: 'pollen', o: ['petal', 'pollen'], base: 'pollen',
              zh: '蜜蜂把叫做花粉的黃色粉末，從一朵花帶到另一朵花。', why: 'yellow powder（黃色粉末）→ 花粉 pollen。' },
            { s: 'A rose has many red ____ (s).', a: 'petals', o: ['petals', 'pollen'], base: 'petal',
              zh: '玫瑰有很多紅色的花瓣。', why: 'many ＋可數的複數；花瓣一片一片 → petals。pollen 是粉，不加 s。' },
            { s: 'The yellow dust from a flower can make some people sneeze. It is ____.', a: 'pollen', o: ['petal', 'pollen'], base: 'pollen',
              zh: '花上的黃色粉末會讓有些人打噴嚏，那是花粉。', why: 'yellow dust（黃色粉末）會讓人打噴嚏 → pollen。' },
            { s: 'A pink ____ fell off the flower and landed on my hand.', a: 'petal', o: ['petal', 'pollen'], base: 'petal',
              zh: '一片粉紅色的花瓣從花上掉下來，落在我的手上。', why: 'A pink ____ ＝一片可數的東西 → petal；pollen 是粉，不能說 a pollen。' },
            { s: 'A flower needs ____ to make seeds.', a: 'pollen', o: ['petal', 'pollen'], base: 'pollen',
              zh: '花需要花粉才能做出種子。', why: '做種子需要的是花粉 pollen，花瓣 petal 不能做種子。' },
        ],
    },
];
