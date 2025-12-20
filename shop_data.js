// shop_data.js

const shopData = {
    // --- 基礎素體與頭髮 ---
    base: "images/char_base.png",

    // --- 衣服清單 (Shirts) ---
    shirts: [
        { 
            id: 'shirt_default', 
            name: 'White Tank', 
            price: 0, 
            img: 'images/char_base.png' // <--- 要指向身體(素體)的圖，因為素體就穿著白背心
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
            img: 'images/shirt_wizard.png' 
        },
        { 
            id: 'shirt_kimono', 
            name: 'Pink Yukata', 
            price: 300, 
            img: 'images/shirt_kimono.png' 
        },
    ],

    // --- 帽子清單 (Hats) ---
    hats: [
        { 
            id: 'hat_none', 
            name: 'No Hat', 
            price: 0, 
            img: 'images/char_hair.png' 
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