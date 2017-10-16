base = dict(

    display_name="macbook-air",
    display_luminance=35,

    fix_radius=.1,

    fix_bar_color=(.8, .6, -.8),
    fix_fix_color=(.8, .6, -.8),
    fix_odd_color=(.45, .28, -.85),

    field_size=24,
    step_duration=1.5,

    bar_width=1.5,

    element_size=2,
    element_tex="saw",
    element_sf=1.5,

    update_rate=2,

    oddball_sf=2,
    oddball_prob=.1,
    oddball_refract=3,

    response_window=1,

    drift_rate=.5,

    key="space",

    output_template="data/{subject}/{session}/oddbar_{time}",

)

train = base.copy()
train.update(

    display_name="kianilab-ps1",
    monitor_eye=True,
)


scan = base.copy()
scan.update(

    display_name="nyu-cbi-propixx",
    eye_host_address="192.168.1.5",
    key="1",
    monitor_eye=True,
    trigger=["5"],
    pre_trigger_stim="fix",

)
