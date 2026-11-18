"""Exterior proportions read from the exact catalog reference photos.

Dimensions are in meters. Wheelbase and smaller features are image estimates.
Shape variants that share a factory platform retain the common casting.
"""
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Model:
    platform: str
    length: float
    height: float
    bar_width: float
    radius: float
    tire_width: float
    deck_width: float
    deck_top: float
    shell_height: float
    deck_start: float
    deck_end: float
    rake: float
    paint: str
    accent: str
    front: str = "rigid"
    rear: str = "fixed"
    motor: str = "rear"
    brakes: str = "front-drum"
    indicators: bool = False
    rear_plate: bool = True
    accent_ring: bool = False
    exterior_pack: bool = False
    underglow: bool = False


max_g30 = Model("g30", 1.167, 1.203, .472, .127, .057, .181, .169, .063,
                -.370, .248, .196, "34393d", "e7a828", accent_ring=True)
max_g2 = Model("g2", 1.210, 1.258, .570, .127, .059, .184, .193, .065,
               -.383, .238, .186, "43494d", "e8b428",
               "single-hydraulic", "twin-spring", indicators=True, accent_ring=True)
max_g3 = Model("g3", 1.218, 1.299, .590, .140, .072, .200, .207, .062,
               -.363, .222, .171, "2d3031", "ba423a",
               "dual-hydraulic", "twin-hydraulic", brakes="both-disc", indicators=True)
f2 = Model("f2", 1.143, 1.214, .570, .127, .058, .167, .166, .041,
           -.376, .230, .177, "292e30", "e88c32", brakes="front-disc", indicators=True)
f3 = Model("f3", 1.152, 1.262, .590, .127, .060, .187, .181, .053,
           -.369, .234, .176, "373a3b", "bf4e43", "dual-hydraulic", "elastomer",
           brakes="front-disc", indicators=True)
e2 = Model("e2", 1.070, 1.140, .445, .103, .044, .155, .154, .070,
           -.336, .199, .194, "3a4145", "d5a152", motor="front", brakes="rear-drum")
es = Model("es", 1.020, 1.126, .430, .101, .040, .139, .121, .025,
           -.341, .218, .195, "363a3d", "bd3b35", "es-spring", "fixed", "front",
           "fender", rear_plate=False)

MODELS = {
    "Max G30": max_g30,
    "Max G30D": replace(max_g30, paint="33393d", accent="32a5cc"),
    "Max G30LP": replace(max_g30, length=1.103, height=1.168, deck_start=-.344,
                         deck_end=.218, deck_width=.170, paint="b2b7ba", rear_plate=False),
    "Max G2": max_g2,
    "Max G3": max_g3,
    "F2": f2,
    "F2 Plus": replace(f2, shell_height=.048),
    "F2 Pro": replace(f2, height=1.258, deck_top=.178, front="single-spring"),
    "F3": f3,
    "F3 Pro": replace(f3, paint="363a3f", brakes="both-disc"),
    "E2": e2,
    "E2 Plus": replace(e2, shell_height=.073, accent="eb8a30"),
    "E2 Pro": replace(e2, length=1.167, height=1.238, bar_width=.539, radius=.127,
                      tire_width=.056, deck_width=.181, deck_top=.166, shell_height=.075,
                      deck_start=-.387, deck_end=.242, motor="rear", brakes="front-drum",
                      indicators=True),
    "ES1": es,
    "ES2": replace(es, rear="elastomer", underglow=True),
    "ES4": replace(es, rear="elastomer", exterior_pack=True, underglow=True),
}

PLATFORMS = {
    "g30": "Ninebot MAX cast rigid unibody",
    "g2": "Ninebot MAX G2 capsulated front spring and twin rear dampers",
    "g3": "Ninebot MAX G3 twin hydraulic stanchions and box-section deck",
    "f2": "Ninebot F2 low-profile swept deck",
    "f3": "Ninebot F3 die-cast locking neck and rear elastomer",
    "e2": "Ninebot E2 curved chassis and round hand controls",
    "es": "Ninebot ES thin deck and stem-mounted battery",
}


def appearance_note(name, spec):
    detail = {
        "g30": "Swept rigid cast neck, tapered deck, hub cover and regional rim trim.",
        "g2": "Covered front hydraulic damper, rear twin spring assembly and deep MAX deck.",
        "g3": "Twin front stanchions, dual rear spring assemblies, integral locking loop and wide TFT cockpit.",
        "f2": "Low casting, molded fenders, disc-braked front hub and bar-end indicators.",
        "f3": "Die-cast headstock, twin fork, rear elastomer, narrow swept deck and wide TFT cockpit.",
        "e2": "Rounded shell, swept steering tube and distinct factory wheel and brake layout.",
        "es": "Slim deck, compact solid wheels, internal stem battery and step-fold mechanism.",
    }[spec.platform]
    variant = {
        "Max G30D": "German-market G30D with cyan rim stripes and rear plate hardware.",
        "Max G30LP": "US G30LP with a pale chassis and dark steering tube.",
        "E2 Pro": "Vented front drum wheel and driven rear hub.",
        "ES4": "Exterior second battery pack.",
        "F2 Pro": "Covered front spring suspension.",
        "F3 Pro": "Rear disc and caliper.",
    }.get(name)
    return " ".join(filter(None, (detail, variant, "Photo-guided exterior with inferred hidden geometry.")))
