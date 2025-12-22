// shop_data.js

const shopData = {
    // --- 基礎素體與頭髮 (這裡一定要有 hair!) ---
    base: "images/char_base.png",
    hair: "images/char_hair.png",       // 預設長髮
    hair_short: "images/char_hair_short.png", // [新增] 特殊短髮

    // --- 衣服清單 (Shirts) ---
    shirts: [
        { 
            id: 'shirt_default', 
            name: 'White Tank', 
            price: 0, 
            img: 'images/char_base.png' // 正確：縮圖顯示素體
        },
        { 
            id: 'shirt_elsa', 
            name: 'Ice Queen', 
            price: 500, 
            img: 'images/shirt_elsa.png' 
        },
        { 
            id: 'shirt_wizard', 
            name: 'Magic Robe', 
            price: 350, 
            img: 'images/shirt_wizard.png',
            //  [新增這行] 指定這件衣服也要用短髮
            custom_hair: 'images/char_hair_short.png'
        },
        { 
            id: 'shirt_kimono', 
            name: 'Pink Yukata', 
            price: 300, 
            img: 'images/shirt_kimono.png',
            //  [新增這行] 指定這件衣服也要用短髮
            custom_hair: 'images/char_hair_short.png' 
        },
        { 
            id: 'shirt_casual_blue', 
            name: 'Casual Blue', 
            price: 850, 
            img: 'images/shirt_casual_blue.png' 
        },
        { 
            id: 'shirt_yellow_coat', 
            name: 'Yellow Coat', 
            price: 2150, 
            img: 'images/shirt_yellow_coat.png',
            //  [新增這行] 指定這件衣服也要用短髮
            custom_hair: 'images/char_hair_short.png'  
        },
        { 
            id: 'shirt_black_glitter', 
            name: 'Black Glitter', 
            price: 2150, 
            img: 'images/shirt_black_glitter.png',
            //  [新增這行] 指定這件衣服也要用短髮
            custom_hair: 'images/char_hair_short.png'  
        },
        { 
            id: 'shirt_teal_jumpsuit', 
            name: 'Teal Jumpsuit', 
            price: 2150, 
            img: 'images/shirt_teal_jumpsuit.png',
            //  [新增這行] 指定這件衣服也要用短髮
            custom_hair: 'images/char_hair_short.png'  
        },
        { 
            id: 'shirt_kpop_idol', 
            name: 'Idol Stage', 
            price: 1680, // 這套很華麗，賣貴一點！
            img: 'images/shirt_kpop_idol.png',
            //  [新增這行] 指定這件衣服也要用短髮
            custom_hair: 'images/char_hair_short.png'  
        }
    ],

    // --- 帽子清單 (Hats) ---
    hats: [
        { 
            id: 'hat_none', 
            name: 'No Hat', 
            price: 0, 
            img: 'images/char_hair.png' // 正確：縮圖顯示頭髮(無帽)
        },
        { 
            id: 'hat_cap', 
            name: 'Yellow Cap', 
            price: 150, 
            img: 'images/hat_cap.png' 
        },
        { 
            id: 'hat_cap_back', 
            name: 'Cool Cap', 
            price: 200, 
            img: 'images/hat_cap_back.png' 
        },
        { 
            id: 'hat_wizard', 
            name: 'Wizard Hat', 
            price: 300, 
            img: 'images/hat_wizard.png' 
        },
        { 
            id: 'hat_tiara', 
            name: 'Princess Tiara', 
            price: 600, 
            img: 'images/hat_tiara.png' 
        },
        { 
            id: 'hat_crown', 
            name: 'Royal Crown', 
            price: 1000, 
            img: 'images/hat_crown.png' 
        }
    ]
};