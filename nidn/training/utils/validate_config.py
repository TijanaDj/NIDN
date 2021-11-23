from dotmap import DotMap


def _validate_config(cfg: DotMap):
    """This function validates that all required entries are in the config.

    Args:
        cfg (DotMap): Run config you intend to use.
    """

    # Check that all required entries are in the config
    required_keys = [
        "name",
        "seed",
        "eps_oversampling",
        "real_min_eps",
        "real_max_eps",
        "imag_min_eps",
        "imag_max_eps",
        "Nx",
        "Ny",
        "N_layers",
        "physical_wavelength_range",
        "N_freq",
        "model_type",
        "encoding_dim",
        "siren_omega",
        "n_neurons",
        "hidden_layers",
        "learning_rate",
        "iterations",
        "L",
        "absorption_loss",
        "type",
        "use_regularization_loss",
        "reg_loss_weight",
        "add_noise",
        "noise_scale",
        "TRCWA_L_grid",
        "TRCWA_NG",
        "target_reflectance_spectrum",
        "target_transmittance_spectrum",
        "freq_distribution",
        "use_gpu",
        "avoid_zero_eps",
    ]

    for key in required_keys:
        if key not in cfg:
            raise ValueError(f"Missing required key: {key}")

    # Check that all values are of correct type
    integer_keys = [
        "Nx",
        "Ny",
        "N_layers",
        "N_freq",
        "encoding_dim",
        "n_neurons",
        "eps_oversampling",
        "seed",
        "TRCWA_NG",
    ]
    float_keys = [
        "L",
        "real_min_eps",
        "real_max_eps",
        "imag_min_eps",
        "imag_max_eps",
        "siren_omega",
        "noise_scale",
        "reg_loss_weight",
    ]
    boolean_keys = ["use_regularization_loss", "add_noise", "use_gpu", "avoid_zero_eps"]
    string_keys = ["model_type", "type", "name", "freq_distribution"]
    list_keys = [
        "TRCWA_PER_LAYER_THICKNESS",
        "TRCWA_L_grid",
        "target_reflectance_spectrum",
        "target_transmittance_spectrum",
        "physical_wavelength_range",
    ]

    for key in integer_keys:
        if not isinstance(cfg[key], int):
            raise ValueError(f"{key} must be an integer")

    for key in float_keys:
        if not isinstance(cfg[key], float):
            raise ValueError(f"{key} must be a float")

    for key in boolean_keys:
        if not isinstance(cfg[key], bool):
            raise ValueError(f"{key} must be a boolean")

    for key in string_keys:
        if not isinstance(cfg[key], str):
            raise ValueError(f"{key} must be a string")

    for key in list_keys:
        if not isinstance(cfg[key], list):
            raise ValueError(f"{key} must be a list")

    # Check that all values are within the correct ranges
    if not (cfg.real_min_eps <= cfg.real_max_eps):
        raise ValueError(f"real_min_eps must be less than or equal to real_max_eps")

    if not (cfg.imag_min_eps <= cfg.imag_max_eps):
        raise ValueError(f"imag_min_eps must be less than or equal to imag_max_eps")

    if not (cfg.physical_wavelength_range[0] < cfg.physical_wavelength_range[1]):
        raise ValueError(f"physical_wavelength_range must be ordered from low to high")

    positive_value_keys = [
        "L",
        "n_neurons",
        "Nx",
        "Ny",
        "N_layers",
        "N_freq",
        "learning_rate",
        "iterations",
        "eps_oversampling",
        "noise_scale",
        "TRCWA_NG",
        "reg_loss_weight",
    ]
    for key in positive_value_keys:
        if not (cfg[key] > 0):
            raise ValueError(f"{key} must be a positive integer")

    if not cfg.Nx % cfg.eps_oversampling == 0:
        raise ValueError(f"Nx must be a multiple of eps_oversampling")
    if not cfg.Ny % cfg.eps_oversampling == 0:
        raise ValueError(f"Ny must be a multiple of eps_oversampling")

    if cfg.type != "classification" and cfg.type != "regression":
        raise ValueError(f"type must be either 'classification' or 'regression'")

    if not cfg.TRCWA_L_grid[1][0] < cfg.TRCWA_L_grid[1][1]:
        raise ValueError(f"TRCWA_L_grid dim1 must be ordered from low to high")
    if not cfg.TRCWA_L_grid[0][0] > cfg.TRCWA_L_grid[0][1]:
        raise ValueError(f"TRCWA_L_grid dim0 must be ordered from high to low")

    if not all(cfg.TRCWA_L_grid) >= 0:
        raise ValueError(f"TRCWA_L_grid must be positive")

    if not all(cfg.target_transmittance_spectrum) >= 0:
        raise ValueError(f"target_transmittance_spectrum must be positive")

    if not all(cfg.target_reflectance_spectrum) >= 0:
        raise ValueError(f"target_reflectance_spectrum must be positive")

    if not len(cfg.target_transmittance_spectrum) == cfg.N_freq:
        raise ValueError(f"target_transmittance_spectrum must have length N_freq")

    if not len(cfg.target_reflectance_spectrum) == cfg.N_freq:
        raise ValueError(f"target_reflectance_spectrum must have length N_freq")

    if not (all(cfg.TRCWA_PER_LAYER_THICKNESS) > 0.0):
        raise ValueError(f"thickness must a positive number.")

    if not (
        len(cfg.TRCWA_PER_LAYER_THICKNESS) == cfg.N_layers
        or len(cfg.TRCWA_PER_LAYER_THICKNESS) == 1
    ):
        raise ValueError(f"TRCWA_PER_LAYER_THICKNESS must have length 1 or N_layers")

    if not (cfg.freq_distribution == "linear" or cfg.freq_distribution == "log"):
        raise ValueError(f"freq_distribution must be either 'linear' or 'log'")
