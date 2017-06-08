
base = dict(

    display_name="laptop",
    display_luminance=0,

    initialize_trial_generator=True,

    field_size=24,

    bar_width=1.5,
    bar_segment_gap=1,

    key_names=["left", "down", "right"],

    traversal_duration=24,
    traversal_steps=16,

    iti_dur=0,

    blank_interval=2,
    blank_dur=12,

    monitor_eye=True,
    fix_window=1.5,

    dot_size=.1,
    dot_color=1,
    dot_density=50,
    dot_speed=5,
    dot_interval=3,

    stair_n_up=1,
    stair_n_down=2,
    stair_step=.02,  # Note steps are done in log space

    wait_accept_resp = .25,

    perform_coh_target=.2,

    show_response_feedback=True,
    show_fixation_feedback=True,
    play_fixation_feedback=False,

    wait_pre_run=4,
    run_duration=None,

)

scan = base.copy()
scan.update(

    display_name="cbi-propixx",

    key_names=["1", "2", "3"],

    trigger=["5"],

    wait_pre_run=0,
    draw_pre_run="fix",

    run_duration=240,

)
