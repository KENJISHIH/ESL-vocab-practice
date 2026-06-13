// shop_data.js

const shopData = {
    // --- 基礎素體 (預設 outfit_default 用) ---
    base: "images/char_base.png",
    base_short: "images/char_base_short.png",

    // --- 整套穿搭 (Outfits) — 取代既有 shirts + bottoms ---
    // 每件 outfit 是一張「角色穿好整套」的全身合成圖，視覺最自然
    outfits: [
        { id: 'outfit_default',     name: 'White Tank',      price: 0,     img: '' },  // 用 base 預設
        { id: 'outfit_casual',      name: 'Casual Jeans',    price: 350,   img: 'images/outfit_casual.png',     isNew: true },
        { id: 'outfit_yukata',      name: 'Pink Yukata',     price: 600,   img: 'images/outfit_yukata.png',     isNew: true, coversShoes: true },
        { id: 'outfit_school',      name: 'School Uniform',  price: 800,   img: 'images/outfit_school.png',     isNew: true },
        { id: 'outfit_ballet',      name: 'Ballet Dancer',   price: 1200,  img: 'images/outfit_ballet.png',     isNew: true },
        { id: 'outfit_wizard',      name: 'Magic Wizard',    price: 1500,  img: 'images/outfit_wizard.png',     isNew: true, coversShoes: true },
        { id: 'outfit_cat',         name: 'Cat Onesie',      price: 1500,  img: 'images/outfit_cat.png',        isNew: true },
        { id: 'outfit_princess',    name: 'Princess Pink',   price: 1800,  img: 'images/outfit_princess.png',   isNew: true, coversShoes: true },
        { id: 'outfit_galaxy',      name: 'Galaxy Star',     price: 2500,  img: 'images/outfit_galaxy.png',     isNew: true },
        { id: 'outfit_astronaut',   name: 'Astronaut',       price: 5000,  img: 'images/outfit_astronaut.png',  isNew: true, tier: 'dream', coversShoes: true }
    ],

    // --- 帽子清單 (Hats) ---
    hats: [
        { id: 'hat_none',           name: 'No Hat',           price: 0,    img: '' },
        { id: 'hat_cap',            name: 'Yellow Cap',       price: 150,  img: 'images/hat_cap.png' },
        { id: 'hat_cap_back',       name: 'Cool Cap',         price: 200,  img: 'images/hat_cap_back.png' },
        { id: 'hat_wizard',         name: 'Wizard Hat',       price: 300,  img: 'images/hat_wizard.png' },
        { id: 'hat_tiara',          name: 'Princess Tiara',   price: 600,  img: 'images/hat_tiara.png' },
        { id: 'hat_crown',          name: 'Royal Crown',      price: 1000, img: 'images/hat_crown.png' },
        { id: 'hat_cat_ears',       name: 'Cat Ears',         price: 400,  img: 'images/hat_cat_ears.png',       isNew: true },
        { id: 'hat_bunny_ears',     name: 'Bunny Ears',       price: 400,  img: 'images/hat_bunny_ears.png',     isNew: true },
        { id: 'hat_flower_crown',   name: 'Flower Crown',     price: 700,  img: 'images/hat_flower_crown.png',   isNew: true },
        { id: 'hat_astronaut',      name: 'Astronaut Helmet', price: 1500, img: 'images/hat_astronaut.png',      isNew: true }
    ],

    // --- 鞋子 (Shoes) ---
    shoes: [
        { id: 'shoes_none',         name: 'Bare Feet',       price: 0,    img: '' },
        { id: 'shoes_sneakers',     name: 'Pink Sneakers',   price: 250,  img: 'images/shoes_sneakers.png',      isNew: true },
        { id: 'shoes_glass_slipper',name: 'Glass Slippers',  price: 1500, img: 'images/shoes_glass_slipper.png', isNew: true },
        { id: 'shoes_magic_boots',  name: 'Magic Boots',     price: 1800, img: 'images/shoes_magic_boots.png',   isNew: true },
        { id: 'shoes_roller',       name: 'Roller Skates',   price: 2200, img: 'images/shoes_roller.png',        isNew: true }
    ],

    // --- 配件 (Accessories) ---
    accessories: [
        { id: 'acc_none',           name: 'None',            price: 0,    img: '' },
        { id: 'acc_round_glasses',  name: 'Round Glasses',   price: 300,  img: 'images/acc_round_glasses.png',   isNew: true },
        { id: 'acc_heart_sun',      name: 'Heart Shades',    price: 500,  img: 'images/acc_heart_sun.png',       isNew: true },
        { id: 'acc_pearl_necklace', name: 'Pearl Necklace',  price: 800,  img: 'images/acc_pearl_necklace.png',  isNew: true },
        { id: 'acc_angel_halo',     name: 'Angel Halo',      price: 1500, img: 'images/acc_angel_halo.png',      isNew: true },
        { id: 'acc_butterfly_mask', name: 'Butterfly Mask',  price: 1800, img: 'images/acc_butterfly_mask.png',  isNew: true },
        { id: 'acc_fairy_wings',    name: 'Fairy Wings',     price: 2500, img: 'images/acc_fairy_wings.png',     isNew: true }
    ],

    // --- 背景場景 (Backgrounds) - DREAM TIER ---
    backgrounds: [
        { id: 'bg_default',         name: 'Sky Blue',        price: 0,     img: '' },
        { id: 'bg_beach_sunset',    name: 'Beach Sunset',    price: 5000,  img: 'images/bg_beach_sunset.png',    isNew: true, tier: 'dream' },
        { id: 'bg_forest',          name: 'Magic Forest',    price: 6000,  img: 'images/bg_forest.png',          isNew: true, tier: 'dream' },
        { id: 'bg_castle',          name: 'Princess Castle', price: 8000,  img: 'images/bg_castle.png',          isNew: true, tier: 'dream' },
        { id: 'bg_space',           name: 'Outer Space',     price: 10000, img: 'images/bg_space.png',           isNew: true, tier: 'dream' }
    ],

    // --- 寵物 (Pets) - DREAM TIER ---
    pets: [
        { id: 'pet_none',           name: 'No Pet',          price: 0,     img: '' },
        { id: 'pet_puppy',          name: 'Puppy',           price: 4000,  img: 'images/pet_puppy.png',          isNew: true, tier: 'dream' },
        { id: 'pet_kitten',         name: 'Kitten',          price: 4000,  img: 'images/pet_kitten.png',         isNew: true, tier: 'dream' },
        { id: 'pet_dragon',         name: 'Baby Dragon',     price: 12000, img: 'images/pet_dragon.png',         isNew: true, tier: 'dream' },
        { id: 'pet_unicorn',        name: 'Unicorn',         price: 15000, img: 'images/pet_unicorn.png',        isNew: true, tier: 'dream' }
    ]
};
