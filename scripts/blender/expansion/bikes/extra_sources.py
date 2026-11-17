from collect import *
more={'KuKirin X1':'https://kukirin-escooter.com/products/kukirin-x1-electric-dirt-bike','Arctic Leopard E-16Z':'https://arctic-leopard.sk/products/e-16z','Arctic Leopard E-20Y':'https://arctic-leopard.bike/products/e-20y','Arctic Leopard E-ZPRO':'https://arcticleo.ru/arctic-leopard-snow-leopard-e-xpro','Arctic Leopard XE Pro S Super':'https://arctic-leopard.com/produit/xe-pro-s-super/'}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
 for r in ex.map(process,more.items()):print(r)
