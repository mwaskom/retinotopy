
base = dict(

    display_name="laptop",
    display_luminance=0,

    field_size=24,

    bar_width=1.5,
    bar_segment_gap=1,

    key_names=["left", "down", "right"],

    traversal_duration=24,
    traversal_steps=18,

    monitor_eye=True,

    dot_size=.1,
    dot_color=1,
    dot_density=50,
    dot_speed=5,
    dot_interval=3,

    stair_n_up=1,
    stair_n_down=3,
    stair_step=.02,  # Note steps are done in log space

    wait_accept_resp = .25,

    perform_coh_target=.3,

    show_response_feedback=True,
    show_fixation_feedback=True,

)
