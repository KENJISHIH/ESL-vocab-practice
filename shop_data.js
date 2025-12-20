// shop_data.js
const shopData = {
    // 身體素體 (Base Character)
    base: "images/base_char.png",

    // 衣服清單
    shirts: [
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
        }
    ],

    // 帽子清單
    hats: [
        { 
            id: 'hat_none', 
            name: 'No Hat', 
            price: 0, 
            img: '' // 空字串代表沒戴帽子
        },
        { 
            id: 'hat_cap', 
            name: 'Baseball Cap', 
            price: 150, 
            img: 'images/hat_cap.png' 
        },
        { 
            id: 'hat_crown', 
            name: 'Golden Crown', 
            price: 1000, 
            img: 'images/hat_crown.png' 
        }
    ]
};