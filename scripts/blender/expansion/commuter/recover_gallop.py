exec(open('scripts/blender/expansion/commuter/add_photos.py').read().split('for name,(dom,handle,idx)')[0])
put('Ausom Gallop','https://www.prnewswire.com/news-releases/ausom-unveils-gallop-embracing-the-super-power-from-a-dual-motor-off-road-electric-scooter-301972640.html','https://mma.prnewswire.com/media/2261932/ausom_gallop.jpg?p=medium','Ausom Gallop','Manufacturer-supplied original Gallop launch photo, 2023; not SR1 or DT1.')
json.dump(list(selected.values()),open(O/'selected.json','w'),indent=2)
a=json.load(open(O/'unresolved-audit.json'));a=[e for e in a if e['name']!='Ausom Gallop'];json.dump(a,open(O/'unresolved-audit.json','w'),indent=2)
