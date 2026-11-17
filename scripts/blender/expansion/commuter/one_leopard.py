exec(open('scripts/blender/expansion/commuter/add_photos.py').read().split('for name,(dom,handle,idx)')[0])
put('Ausom Leopard','https://ausomstore.com/blogs/electric-scooter-guide/ausom-leopard-unleashing-the-pinnacle-of-off-road-electric-scooters','https://cdn.shopify.com/s/files/1/0703/6944/4119/files/1645_1024x1024.jpg?v=1698742101','Ausom Leopard','Legacy Leopard 1000W single-motor reference from manufacturer article; not DT1 or DT1 Pro.')
json.dump(list(selected.values()),open(O/'selected.json','w'),indent=2)
