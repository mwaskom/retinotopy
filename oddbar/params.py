base = dict(

    display_name="macbook-air",
    display_luminance=35,

    monitor_eye=True,

    fix_radius=.1,

    fix_bar_color=(.8, .6, -.8),
    fix_fix_color=(.8, .6, -.8),
    fix_odd_color=(.45, .28, -.85),

    field_size=20,
    step_duration=1.5,

    bar_width=1.5,

    element_size=2,
    element_tex="saw",
    element_sf=1.5,

    update_rate=2,

    oddball_sf=2,
    oddball_prob=.1,
    oddball_refract=3,

    drift_rate=.5,

    wait_blank=12,

    key="space",

    output_template="data/{subject}/{session}/oddbar_{time}",

)
