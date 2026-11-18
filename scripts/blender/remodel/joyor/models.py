"""Exterior proportions transcribed from the linked variant-specific Joyor references."""

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Scooter:
    family: str
    wheelbase: float = 0.970
    tire_radius: float = 0.127
    tire_width: float = 0.071
    deck_length: float = 0.520
    deck_width: float = 0.205
    deck_top: float = 0.207
    deck_depth: float = 0.078
    height: float = 1.226
    bars: float = 0.610
    rake: float = 0.140
    mast_base: float = 0.392
    front_pivot: float = 0.151
    rear_pivot: float = 0.172
    swingarm: str = "finned"
    arm_color: str = "ec571e"
    body: str = "292b2e"
    trim: str = "35373a"
    tires: str = "allterrain"
    hinge: str = "lattice"
    foot_rest: str = "wedge"
    guard: str = "separate"
    lamps: str = "corner"
    cable_color: str = "2e2c30"
    motor_count: int = 1
    display: str = "side"
    reflectors: bool = True


S = Scooter("Joyor S cast-arm")
SZ = replace(S, hinge="covered", display="center", lamps="signals", swingarm="vented", deck_depth=0.084)
Y = Scooter(
    "Joyor Y dual telescopic",
    wheelbase=0.955, tire_width=0.059, deck_length=0.587, deck_width=0.197,
    deck_top=0.188, deck_depth=0.069, height=1.192, bars=0.564,
    rake=0.144, mast_base=0.361, swingarm="telescopic", arm_color="6b6e74",
    body="303338", trim="43454a", tires="road", foot_rest="arch",
    guard="full", hinge="compact", lamps="corner",
)
T = replace(
    SZ, family="Joyor T rubber-cartridge rocker",
    wheelbase=0.976, deck_length=0.536, deck_width=0.211,
    deck_top=0.214, height=1.300, bars=0.630, deck_depth=0.079,
    rake=0.169, mast_base=0.423, hinge="truss", foot_rest="hook",
    swingarm="windowed", cable_color="aa3823",
)

MODELS = {
    "s5": replace(S, family="Joyor S5 ABE black stem and orange twin rocker", swingarm="rebated",
                  arm_color="d65726", cable_color="a03428", wheelbase=0.964,
                  deck_width=0.200, height=1.225, lamps="abe", reflectors=False),
    "s8": replace(SZ, family="Joyor S8 EU single drive and stepped battery deck", wheelbase=0.974,
                  deck_depth=0.090, deck_width=0.209, cable_color="a03d26", height=1.232,
                  guard="lip", display="side", hinge="lattice", swingarm="finned"),
    "s10-s": replace(S, family="Joyor S10-S original open neck and V1 controls", motor_count=2,
                     wheelbase=0.978, deck_length=0.524, cable_color="992d21",
                     swingarm="finned", display="side", foot_rest="hook", height=1.232,
                     deck_width=0.206, deck_depth=0.080, reflectors=False),
    "y8-s": replace(Y, family="Joyor Y8-S ABE telescopic fork and wide body",
                    deck_width=0.212, deck_depth=0.087, body="262b33", trim="41484f",
                    arm_color="40494e", lamps="abe", height=1.200),
    "s5-z": replace(SZ, family="Joyor S5-Z orange rockers and signal enclosure",
                    deck_width=0.202, cable_color="b33d25", display="center", guard="lip",
                    swingarm="rebated", wheelbase=0.962, deck_depth=0.075),
    "s8-s-z": replace(SZ, family="Joyor S8-S-Z dual hubs and thick 26Ah enclosure",
                       motor_count=2, deck_width=0.211, deck_depth=0.089, guard="lip",
                       wheelbase=0.972, deck_length=0.525, arm_color="ef561c"),
    "s10-s-z": replace(SZ, family="Joyor S10-S-Z channel swingarms and revised hinge",
                        motor_count=2, wheelbase=0.978, deck_depth=0.083, deck_width=0.207,
                        deck_length=0.528, arm_color="d54824", guard="full", front_pivot=0.146,
                        rear_pivot=0.168, rake=0.135),
    "y6-s": replace(Y, family="Joyor Y6-S twin sliders and rear split hub", wheelbase=0.978,
                    display="center", deck_width=0.206, height=1.203, arm_color="777a7d",
                    trim="5a5d61"),
    "y10": replace(Y, family="Joyor Y10 long-range Y chassis", deck_width=0.208,
                   deck_depth=0.086, deck_top=0.197, deck_length=0.567,
                   height=1.187, body="2b3137", trim="485058", lamps="signals"),
    "t6": replace(T, family="Joyor T6 single drive and orange open-window rockers",
                  tire_width=0.066, deck_width=0.202, deck_depth=0.076,
                  deck_length=0.528, rake=0.158, display="side"),
    "t10": replace(T, family="Joyor T10 NFC dual-drive cast T chassis", motor_count=2,
                   deck_length=0.544, deck_width=0.214, front_pivot=0.161, rear_pivot=0.182,
                   tire_width=0.077, guard="lip", lamps="signals", display="nfc"),
    "t12-ultra": Scooter(
        "Joyor T12 Ultra 12-inch tires and silver forged arms",
        wheelbase=1.010, tire_radius=0.152, tire_width=0.090, deck_length=0.566,
        deck_width=0.234, deck_top=0.260, deck_depth=0.091, height=1.341,
        bars=0.632, rake=0.158, mast_base=0.491, front_pivot=0.185, rear_pivot=0.187,
        swingarm="silver", arm_color="9a9ca3", hinge="truss", foot_rest="wedge",
        guard="full", lamps="bar", motor_count=2, display="nfc", tires="block",
    ),
    "c10": Scooter(
        "Joyor C10 removable battery and contoured turquoise chassis",
        wheelbase=0.929, tire_width=0.053, deck_length=0.613, deck_width=0.175,
        deck_top=0.162, deck_depth=0.064, height=1.245, bars=0.558,
        rake=0.203, mast_base=0.350, swingarm="commuter", arm_color="242b30",
        body="353a3e", trim="484e54", tires="road", hinge="lean",
        foot_rest="molded", guard="molded", lamps="turquoise", display="nfc",
    ),
    "f5": Scooter(
        "Joyor F5 compact drum brake and orange front spring",
        wheelbase=0.777, tire_radius=0.1016, tire_width=0.050, deck_length=0.543,
        deck_width=0.142, deck_top=0.135, deck_depth=0.061, height=1.169,
        bars=0.539, rake=0.224, mast_base=0.275, swingarm="shortcoil",
        body="24252a", trim="40414a", tires="slick", hinge="lever",
        foot_rest="none", guard="compact", lamps="low", display="side", reflectors=False,
    ),
}
