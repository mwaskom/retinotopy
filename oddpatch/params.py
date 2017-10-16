base = dict(

    display_name="macbook-air",
    display_luminance=35,

    fix_radius=.1,

    patch_size=3,
    element_size=2,
    element_tex="saw",
    element_sf=1.5,

    update_rate=2,

    oddball_sf=2,
    oddball_prob=.2,

    drift_rate=.5,

    key="space",

    output_template="data/{subject}/{session}/oddpatch_{time}",

)

train = base.copy()
train.update(

    display_name="kianilab-ps1",
)


scan = base.copy()
scan.update(

    display_name="nyu-cbi-propixx",
    eye_host_address="192.168.1.5",
    key="1",
    monitor_eye=True,

)

