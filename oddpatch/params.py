base = dict(

    display_name="macbook-air",
    display_luminance=35,

    fix_radius=.1,

    patch_size=2,  # TODO actually radius
    element_size=2,
    element_tex="saw",
    element_sf=1.5,

    update_rate=2,

    stim_duration=1.5,
    resp_duration=1.5,
    iti_unit=1.5,

    oddball_sf=2,
    oddballs=6,

    drift_rate=.5,

    key="space",

    run_duration=199.5,

    output_template="data/{subject}/{session}/oddpatch_{time}",

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
