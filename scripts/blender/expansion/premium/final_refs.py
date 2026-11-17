import sys,json
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).parent));import curate as q
from prepare_refs import dl
r={e['name']:e for e in json.load(open(q.A/'references.json'))}
rows=[
('Dualtron Thunder','https://dualtron.uk/collections/dualtron-thunder','https://cdn.shopify.com/s/files/1/0012/2640/8024/products/Dualtron-Thunder-60V-35AH-Minimotors-1619985541_600x.jpg?v=1631978742','Dualtron UK official distributor','Original Thunder 60V35Ah product photograph, not Thunder2 or Thunder3.'),
('Dualtron X','https://minimotors-ca.com/tienda/sin-categorizar/dualtron-x/','https://minimotors-ca.com/wp-content/uploads/2021/03/DT-X.jpg','Minimotors Guatemala','Original Dualtron X 60V49Ah distributor photograph; not X2 or X Limited.'),
('Inokim Light 2','https://www.maxblinker.com/en/electric-scooters/inokim-light-2','https://www.maxblinker.com/137-panda_thickbox_default/inokim-light-2.jpg','Max Blinker','Light2 original compact 36V10.4Ah product reference, not Light2Max.'),
('EMOVE Touring','https://www.voromotors.com/pages/ultimate-beginners-guide','https://i.shgcdn.com/434c169c-6c00-4a94-b783-bc77949229cb/-/format/auto/-/preview/3000x3000/-/quality/lighter/','Voro Motors','Manufacturer guide exact EMOVE Touring purple photograph.'),
('Apollo City','https://electroheads.com/products/apollo-city-2022-electric-scooter','https://electroheads.com/cdn/shop/files/apollo-apollo-city-2022-electric-scooter-commuter-city-scooter-31013659181169.png?v=1705665529','Electroheads','City2022 single-motor product reference; not CityPro or City2.0.'),
('Varla Eagle One','https://varlascooter.com/blogs/buying-tips/best-electric-scooter-for-heavy-adults-2021/','https://cdn.shopifycdn.net/s/files/1/0429/1995/2537/files/varlaBox_1320x.png?v=1628479367','Varla Scooter','Original EagleOne manufacturer 2021 package photograph; not V2.0 or Pro.'),
('Kaabo Wolf King','https://www.electrickicks.com.au/products/kaabo-wolf-king-11-72v-electric-scooter','https://cdn.shopify.com/s/files/1/0034/7504/6445/products/kaabo-wolf-king-electric-scooter-gold-side_900x.jpg?v=1615796962','Electric Kicks','Original WolfKing11 72V28Ah gold reference; not WolfKingGT/GTR.'),
('Kaabo Wolf Warrior X','https://scooterhut.com.au/products/kaabo-electric-scooter-wolf-warrior-x-black','https://scooterhut.com.au/cdn/shop/files/9350759089070_KAABO_Wolf_WarriorX__Black_02_fedb8026-b375-492d-9648-1d565307c536.jpg?v=1708643791&width=2048','Scooter Hut','WolfWarriorX family shown in explicitly identified Plus60V21Ah distributor trim. GT/Max exterior not substituted.'),
]
for n,src,img,credit,note in rows:
 e=dict(name=n,key=q.key(n),source=src,imageSource=img,credit=credit,variantNote=note,productTitle=n);e,err=dl(e);print(n,err,flush=True)
 if not err:r[n]=e
# The manufacturer explicitly identifies BladeGT II as generation2 of BladeGT.
# Use this exact disclosed generation for the broad BladeGT family entry.
n='Teverun Blade GT';k=q.key(n);page=8;im=Image.open(q.A/f'teverun-page-{page:02}.jpg');w,h=im.size;im=im.crop((int(w*.51),int(h*.07),int(w*.985),int(h*.70)));f=q.P/(k+'.webp');im.save(f,'WEBP',quality=92);url='https://teverun.com/wp-content/uploads/2024/04/4.TEVERUN-CATALOG-202404.pdf';r[n]=dict(name=n,key=k,type='scooter',subtype='scooter',source=url+'#page=2',imageSource=url+'#page=8',credit='Teverun manufacturer catalog2024',variantNote='Unspecified BladeGT family shown as manufacturer BladeGTII2024, explicitly documented on catalogpage2 as second generation of BladeGT. Original2022 geometry is not claimed.',productTitle='Teverun Blade GT II 2024',image='/assets/vehicles/expansion/premium/'+f.name,dimensions=list(im.size),bytes=f.stat().st_size,license='Manufacturer reference photograph; no open license asserted',referenceKind='manufacturer-catalog-reference')
json.dump(list(r.values()),open(q.A/'references.json','w'),indent=2);print('TOTAL',len(r))
