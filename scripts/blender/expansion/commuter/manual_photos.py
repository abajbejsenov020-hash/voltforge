# Confirmed image URLs extracted from exact manufacturer or official regional store pages.
exec(open('scripts/blender/expansion/commuter/add_photos.py').read().split('for name,(dom,handle,idx)')[0])
M={
'Segway Ninebot ES1':('https://support.segway.com/support_product.php?segcatid=34','https://support.segway.com/product_files/20230720021502_Screenshot%202023-07-20%20141424.png'),
'Segway Ninebot ES2':('https://support.segway.com/support_product.php?segcatid=1','https://segway.imgix.net/catalog/product/cache/1be073bb625205c2a3aab025b4fe3368/e/s/es2-n_708x708_3.png'),
'Segway Ninebot ES4':('https://support.segway.com/support_product.php?segcatid=3','https://segway.imgix.net/catalog/product/cache/1be073bb625205c2a3aab025b4fe3368/e/s/es4_708x708_1.png'),
'Kugoo G1':('https://kugoomotors.com/product/kugoo-g1/6','https://kugoomotors.com/upload/thumbs/cat_item_sm/productimage/image/img4225_62d8080a4a267.jpg'),
'Xiaomi M365':('https://www.mi.com/es/mi-electric-scooter/','https://i01.appmifile.com/webfile/globalimg/en/goods/mi-electronic-scooter/scooter-01-1442.jpg'),
'Xiaomi M365 Pro':('https://www.mi.com/es/mi-electric-scooter-pro/','https://i01.appmifile.com/webfile/globalimg/mi-electric-scooter-pro/pc/electricScooter_01.jpg'),
'Xiaomi Essential':('https://www.mi.com/es/mi-electric-scooter-essential/','https://i01.appmifile.com/webfile/globalimg/products/pc/mi-electric-scooter-essential/section01.jpg'),
'Xiaomi 1S':('https://www.mi.com/es/mi-electric-scooter-1S/','https://i01.appmifile.com/webfile/globalimg/products/pc/mi-electric-scooter-1S/section01bg.jpg'),
}
for name,(source,url) in M.items():put(name,source,url,name,'Legacy official product reference; market-specific equipment may vary.')
s=(O/'kugoo-m2-pro-page.html').read_text();u=re.search('<meta property="og:image" content="([^"]+)',s)[1];put('Kugoo M2 Pro','https://www.jlkugoo.com/electric-scooter/m2-pro.html',u,'KUGOO M2 Pro Electric Scooter')
json.dump(list(selected.values()),open(O/'selected.json','w'),indent=2)
