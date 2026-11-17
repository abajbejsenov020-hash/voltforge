import json
from pathlib import Path
A=Path(__file__).resolve().parents[4]/'artifacts/blender/expansion/premium';C={}
black=[.024,.03,.035];grey=[.12,.15,.17];red=[.67,.009,.014];gold=[.75,.42,.025];cyan=[.015,.72,.60];yellow=[.95,.65,.007];blue=[.018,.28,.65]
def add(name,kind,wb,r,dl,dw,dz,h,bar,accent,notes,**kw):
 C[name]=dict(kind=kind,family=kw.pop('family',name+' exterior'),wb=wb,r=r,dl=dl,dw=dw,dz=dz,h=h,bar=bar,body=kw.pop('body',black),accent=accent,notes=notes,**kw)
for model,wb,r,dl,dw,dz,h,note in [
 ('Thunder 2',1.00,.14,.62,.27,.26,1.29,'Wide road tyres, rectangular battery chassis, red rear kickplate and exposed cartridge swingarms.'),
 ('Thunder 3',1.00,.14,.63,.27,.27,1.35,'Twin low round headlamps, cartridge arms, wide road tyres and cyan stem illumination.'),
 ('Ultra',.97,.14,.58,.25,.265,1.24,'Original black cartridge-arm chassis and knobby off-road tyres, no raised performance tail.'),
 ('Ultra 2',1.02,.14,.63,.27,.28,1.30,'Long square chassis, high rear kickplate, knobby tyres and double folding clamp.'),
 ('Victor Luxury',.92,.127,.57,.235,.25,1.27,'Compact dual-motor cartridge chassis with low lamp and open rear carry brace.'),
 ('Victor Luxury Plus',.99,.127,.64,.235,.26,1.30,'Lengthened Luxury deck, yellow neck badge and integrated illuminated rear brace.'),
 ('Eagle Pro',.94,.127,.57,.23,.25,1.20,'Original slender black twin-hinge neck and ten-inch dual hub wheels; no large raised tail.'),
 ('Storm',1.00,.14,.65,.29,.275,1.21,'Deep removable battery chassis with red trim, massive rear controller/kickplate.'),
 ('Storm Limited',1.08,.145,.69,.30,.285,1.24,'Longer deep deck, turquoise cartridge arms and tall rear tail housing.'),
 ('Spider 2',.95,.127,.61,.225,.255,1.23,'Slim light chassis, narrow tyres, skeletal rear footplate and black cartridge arms.'),
 ('City',1.04,.19,.62,.25,.28,1.25,'Distinctive very large fifteen-inch road wheels, long neck and removable battery deck.'),
 ('Togo',.90,.114,.54,.20,.22,1.22,'Compact thin deck, narrow ten-inch road tyres, yellow suspension cover and small rear brace.'),
 ('Popular',.91,.114,.55,.21,.22,1.18,'Compact black deck with white angular top graphic, tall front cowl and slim road tyres.'),
 ('Achilleus',.98,.14,.60,.255,.26,1.24,'Wide eleven-inch road tyres, compact deep chassis and open cast rear brace.'),
 ('Spider',.92,.127,.57,.20,.24,1.17,'Original lightweight narrow black deck, thin road wheels and single slim stem.'),
 ('Forever',.93,.127,.59,.215,.25,1.22,'Slender dual-motor deck with white parallel top rails and cartridge suspension.'),
 ('Mini Special',.90,.114,.59,.21,.235,1.18,'Long-body single-motor Mini Special, cyan side LEDs, rear enclosed motor and exposed twin springs.'),
 ('Victor',.91,.127,.56,.23,.25,1.25,'Short square Victor chassis, low single headlight and twin clamp rings.'),
 ]:
  add('Dualtron '+model,'dualtron',wb,r,dl,dw,dz,h,.61,cyan if model=='Storm Limited' else black,note,rgb=model not in ['Ultra','Eagle Pro'],dual=model not in ['Togo','Mini Special'],tread='block' if 'Ultra' in model else 'street',kick=model not in ['Ultra','Eagle Pro','Spider'],lamp='twin' if model=='Thunder 3' else 'low')
for model,r,wb,h,n in [('X2',.165,1.12,1.45,'Large 13-inch ultra-wide road tyres, sprung front swingarms and tall rectangular auxiliary battery stem.'),('X Limited',.165,1.10,1.40,'Broad tall auxiliary battery column, very wide road tyres, twin headlamps and fully sprung long chassis.')]:
 add('Dualtron '+model,'dualtron-x',wb,r,.70,.31,.29,h,.65,black,n,rgb=True,lamp='twin',wide=.073)
add('Kaabo Mantis King GT','sport',1.00,.127,.59,.23,.25,1.29,.66,red,'Black deck, red neck/arm accents, prominent front and rear hydraulic coils and red locking collar.',rgb=True)
add('Kaabo Mantis 8','sport',.86,.102,.52,.20,.205,1.16,.56,grey,'Very compact eight-inch wheel chassis, rounded deck, black C arms and single folding stem.',kick=False,neck=.39)
add('Kaabo Mantis X','sport',.98,.127,.59,.23,.255,1.28,.66,red,'Gray sculpted C-type swingarms, red hinge details and high adjustable suspension.',body=grey,rgb=True)
add('Kaabo Wolf King GTR','wolf',1.18,.152,.66,.28,.34,1.39,.75,grey,'Long dual telescopic stems and two crown bridges, wide road tyres, high removable battery deck, twin low headlights.',neck=.65,rgb=True)
for model,r,wb,dl,dw,dz,h,col,n in [
 ('8',.102,.86,.52,.20,.21,1.18,[.35,.48,.42],'Sage green compact single rear motor chassis, eight-inch wheels and small offset rear spring.'),
 ('8+',.102,.86,.52,.20,.21,1.18,[.35,.48,.42],'Sage green dual-hub compact chassis with front and rear black enclosed hubs.'),
 ('9',.108,.90,.54,.215,.23,1.23,cyan,'Turquoise nine-inch single-motor chassis, cast front C arm and split folding stem.'),
 ('9+',.108,.90,.54,.215,.23,1.23,cyan,'Turquoise dual-hub nine-inch C arms, matching rim stripes and double spring suspension.'),
 ('10+',.127,1.00,.60,.25,.265,1.30,yellow,'Yellow ten-inch wide C arms, black deck, low dual lamps and split stem.'),
 ('10 Apex',.127,1.01,.62,.26,.26,1.30,grey,'Graphite removable battery deck, sculpted gray arms, tall stem with red latch.'),
 ('11+',.14,1.15,.69,.30,.30,1.33,grey,'Twin fork-like parallel stems, large central round headlamp and broad battery deck.'),
 ('11+ Super 72',.14,1.15,.69,.30,.30,1.33,yellow,'Super 72 parallel twin stems and broad deck; yellow model accents.')]:
 add('Vsett '+model,'wolf' if model.startswith('11') else 'sport',wb,r,dl,dw,dz,h,.66,col,n,dual=model not in ['8','9'],body=grey if model.startswith('8') else black,rgb=True,kick=model not in ['8','8+'])
for model,r,wb,dl,dw,dz,h in [('8',.101,.84,.50,.19,.21,1.17),('9',.114,.88,.52,.19,.22,1.18),('10',.127,.94,.55,.21,.24,1.25),('10X',.127,1.00,.60,.24,.26,1.25),('11X',.14,1.15,.68,.29,.30,1.33)]:
 add('Zero '+model,'wolf' if model=='11X' else 'sport',wb,r,dl,dw,dz,h,.65,red,'ZERO '+model+' black telescopic stem, red markings and '+('twin long stems, red C swingarms and exposed springs.' if model=='11X' else 'red C swingarms, dual motors and rear brace.' if model=='10X' else 'narrow rectangular deck, compact commuter wheels and rear hub motor.'),dual=model in ['10X','11X'],kick=model in ['10X','11X'],fork='telescopic' if model in ['8','9','10'] else None,neck=.40 if model in ['8','9'] else .49)
add('Inokim Quick 4','inokim',.91,.127,.51,.21,.22,1.12,.56,[.45,.75,.02],'Short deck, lime green single-sided front/rear arms, black folding stem, small road wheels.',singleArm=True,dual=False,kick=False)
add('Inokim OX','inokim',1.00,.127,.60,.25,.27,1.30,.58,[.42,.66,.02],'Single-sided lime green monoshock swingarms, low solid deck and long slim gray stem.',body=grey,singleArm=True,dual=False)
add('Inokim OXO','inokim',1.01,.127,.61,.26,.28,1.30,.58,[.65,.85,.005],'2026 OXO photograph: sculpted lime/yellow single-sided C arms, gray body and dual black hubs.',body=grey,singleArm=True)
add('InMotion S1F','inmotion',.96,.127,.59,.18,.18,1.26,.54,[.90,.47,.01],'Tall gray commuter with long narrow deck, telescopic fork and yellow wheel detail.',body=grey,fork='telescopic',dual=False,kick=False,neck=.34,lamp='console')
add('InMotion Climber','inmotion',.91,.127,.55,.18,.18,1.20,.52,[1,.22,.008],'Rigid fork, orange motor/rim stripes and orange grip tips, narrow compact gray deck.',body=grey,fork='rigid',suspension=False,kick=False,neck=.32,lamp='console')
for model,col in [('RS',[1,.54,.005]),('RS Lite',[1,.30,.009])]:
 add('InMotion '+model,'inmotion',1.15,.14,.66,.28,.30,1.47,.71,col,'Tall twin-section stem, orange adjustable swingarms, very long battery deck, wide road tyres and low frame LED lamps.',rgb=True,neck=.57)
add('Yume Hawk','sport',1.00,.127,.60,.235,.27,1.25,.66,black,'Black/slate open sculpted arms, central stem with high single light and compact black kickbrace.',lamp='high',tread='block')
add('Yume Raptor','sport',1.08,.14,.64,.26,.285,1.35,.70,red,'Red twin folding collar and flank badge, black angular C arms, large off-road tyres and ribbed rear kickplate.',tread='block',lamp='high')
add('RoadRunner RS5 Max','rs5',1.00,.133,.60,.24,.255,1.25,.66,blue,'Sapphire blue open sculpted arms and stem trim, removable deck battery, ribbed rear brace and high round light.',rgb=True,lamp='high',tread='block')
add('RoadRunner RX7','rs5',1.12,.14,.69,.28,.30,1.40,.70,cyan,'Turquoise skeletal swingarms, cyan vertical stem and deck light inlays, broad chassis and black road tyres.',rgb=True,lamp='high')
add('EMOVE Cruiser S','sport',.98,.127,.63,.25,.225,1.25,.62,black,'Long black commuter chassis, black telescopic stem, dual front telescopic suspension and rear coil.',dual=False,kick=False,fork='telescopic')
add('EMOVE RoadRunner Pro','seated',1.02,.178,.30,.14,.30,1.05,.68,red,'Red welded diamond moped frame, small 14-inch knobby tyres, black triangular battery and long bench saddle.',body=red,kick=False,tread='block',neck=.66)
add('Varla Pegasus','sport',.94,.114,.60,.22,.24,1.25,.64,blue,'Silver angular deck with yellow top stripe, blue C-type suspension arms, compact wide road wheels.',body=[.45,.49,.54],rgb=False)
add('Varla Eagle One Pro','sport',1.08,.14,.65,.27,.285,1.32,.70,red,'Large road wheel chassis, red hooked swingarms, black tall center stem and wide gray-black deck.',body=[.13,.15,.17])
add('Hiley Tiger 10 Pro','sport',1.02,.127,.60,.23,.27,1.30,.65,gold,'Gold cast C arms, elongated black deck and stem, tiny twin front lamps, multicolor flank lighting.',rgb=True,lamp='twin')
add('Apollo Explore','sport',.95,.127,.58,.20,.24,1.22,.63,blue,'Original Explore narrow deck, blue rear suspension insert, thin telescopic stem and single rear hub motor.',dual=False,kick=False,fork='telescopic')
add('Apollo Phantom','apollo',1.00,.127,.60,.25,.26,1.28,.68,grey,'Original Phantom V1 gray monoblock frame, swept four-spring suspension and high single lamp.',body=grey,lamp='high')
for model,r,wb,dl,dw,dz,h in [('Burn-E',.14,1.08,.66,.28,.29,1.42),('Burn-E 2',.14,1.08,.66,.28,.29,1.42),('Burn-E 2 Max',.14,1.08,.66,.28,.29,1.42),('Klima',.127,1.00,.60,.23,.26,1.36),('Klima Max',.127,1.00,.60,.23,.26,1.36),('Stellar',.114,.96,.56,.22,.24,1.36),('Super Stellar',.114,.96,.56,.22,.24,1.36)]:
 add('NAMI '+model,'nami',wb,r,dl,dw,dz,h,.69,black,'NAMI '+model+' welded tubular perimeter frame with open triangular neck, thin carbon-look stem, external adjustable front/rear shocks, long close fenders and '+('single rear motor.' if model=='Stellar' else 'two enclosed hub motors.'),dual=model!='Stellar',lamp='high',neck=.56 if model.startswith('Burn') else .49)
json.dump(C,open(Path(__file__).with_name('configs.json'),'w'),indent=2)
print('configs',len(C))
