import torch

from nidn.utils.global_constants import EPS_0, PI, SPEED_OF_LIGHT

from ..fdtd_integration.init_fdtd import init_fdtd
from ..materials.layer_builder import LayerBuilder
from ..trcwa.compute_target_frequencies import compute_target_frequencies
from ..utils.load_default_cfg import load_default_cfg
from ..utils.compute_spectrum import compute_spectrum


def test_fdtd_grid_creation():
    """Test that the simulation is created in the right way, with the correct objects and correct relative placement of them"""
    # Create grid with multiple uniform layer
    cfg = load_default_cfg()
    cfg.N_layers = 4
    cfg.PER_LAYER_THICKNESS = [1.0, 2.0, 1.5, 1.2]
    cfg.N_freq = 1
    eps_grid = torch.zeros(1, 1, cfg.N_layers, cfg.N_freq, dtype=torch.cfloat)
    cfg.Nx = 1
    cfg.Ny = 1
    cfg.target_frequencies = compute_target_frequencies(
        cfg.physical_wavelength_range[0],
        cfg.physical_wavelength_range[1],
        cfg.N_freq,
        "linear",
    )
    layer_builder = LayerBuilder(cfg)
    eps_grid[:, :, 0, :] = layer_builder.build_uniform_layer("titanium_oxide")
    eps_grid[:, :, 1, :] = layer_builder.build_uniform_layer("zirconium")
    eps_grid[:, :, 2, :] = layer_builder.build_uniform_layer("gallium_arsenide")
    eps_grid[:, :, 3, :] = layer_builder.build_uniform_layer("silicon_nitride")
    grid, transmission_detector, reflection_detetctor = init_fdtd(
        cfg,
        include_object=True,
        wavelength=cfg.physical_wavelength_range[0],
        permittivity=eps_grid,
    )
    # Check that it was made properly
    assert len(grid.objects) == 4
    for i in range(len(grid.objects)):
        assert grid.objects[i].permittivity == eps_grid[0, 0, i, 0].real
        assert (
            grid.objects[i].conductivity[0][0][0][0]
            - (
                eps_grid[0, 0, i, 0].imag
                * SPEED_OF_LIGHT
                / cfg.physical_wavelength_range[0]
                * 2
                * PI
                * EPS_0
            )
            < 1e-16
        )

    assert len(grid.detectors) == 2
    # Check that the reflection detector is placed before the first layer, and the transmission detector is placed after the last layer
    assert transmission_detector.x[0] >= grid.objects[-1].x.stop
    assert reflection_detetctor.x[0] <= grid.objects[0].x.start

    assert len(grid.sources) == 1
    # If periodic boundaries in both x and y, it is two, if pml in x and periodic in y there is 3 and 4 if pml in both directions (I think)
    assert len(grid.boundaries) >= 2


def test_fdtd_simulation_single_layer():
    """Test that checks that the calculate_spectrum function returns the correct spectrum for a single layer"""
    # Create grid with uniform layer
    cfg = load_default_cfg()
    cfg.N_freq = 5
    cfg.N_layers = 1
    cfg.physical_wavelength_range[0] = 1e-6
    cfg.physical_wavelength_range[1] = 1e-5
    eps_grid = torch.zeros(1, 1, cfg.N_layers, cfg.N_freq, dtype=torch.cfloat)
    cfg.target_frequencies = compute_target_frequencies(
        cfg.physical_wavelength_range[0],
        cfg.physical_wavelength_range[1],
        cfg.N_freq,
        "linear",
    )
    cfg.FDTD_niter = 300
    cfg.solver = "FDTD"
    layer_builder = LayerBuilder(cfg)
    eps_grid[:, :, 0, :] = layer_builder.build_uniform_layer("titanium_oxide")
    reflection_spectrum, transmission_spectrum = compute_spectrum(eps_grid, cfg)
    validated_reflection_spectrum = torch.tensor(
        [
            0.01996015,
            0.39330551,
            0.44639092,
            0.18894569,
            0.43341999,
        ]
    )
    validated_transmission_spectrum = torch.tensor(
        [
            0.80365908,
            0.58930942,
            0.54395288,
            0.72771733,
            0.49183103,
        ]
    )
    assert all(
        torch.abs(torch.tensor(transmission_spectrum) - validated_transmission_spectrum)
        < 1e-8
    )
    assert all(
        torch.abs(torch.tensor(reflection_spectrum) - validated_reflection_spectrum)
        < 1e-8
    )
    assert all(e <= 1 for e in transmission_spectrum)
    assert all(e <= 1 for e in reflection_spectrum)
    assert all(e >= 0 for e in transmission_spectrum)
    assert all(e >= 0 for e in reflection_spectrum)


def test_fdtd_simulation_four_layers():
    """Test that checks that the calculate_spectrum function returns the correct spectrum for a simulation with four layers"""
    # Create grid with four uniform layer
    cfg = load_default_cfg()
    cfg.N_layers = 4
    cfg.FDTD_niter = 600
    cfg.N_freq = 5
    cfg.PER_LAYER_THICKNESS = [1.0, 1.0, 1.0, 1.0]
    cfg.physical_wavelength_range[0] = 1e-6
    cfg.physical_wavelength_range[1] = 1e-5
    eps_grid = torch.zeros(1, 1, cfg.N_layers, cfg.N_freq, dtype=torch.cfloat)
    cfg.target_frequencies = compute_target_frequencies(
        cfg.physical_wavelength_range[0],
        cfg.physical_wavelength_range[1],
        cfg.N_freq,
        "linear",
    )
    cfg.solver = "FDTD"
    layer_builder = LayerBuilder(cfg)
    eps_grid[:, :, 0, :] = layer_builder.build_uniform_layer("titanium_oxide")
    eps_grid[:, :, 1, :] = layer_builder.build_uniform_layer("zinc_oxide")
    eps_grid[:, :, 2, :] = layer_builder.build_uniform_layer("gallium_arsenide")
    eps_grid[:, :, 3, :] = layer_builder.build_uniform_layer("silicon_nitride")
    reflection_spectrum, transmission_spectrum = compute_spectrum(eps_grid, cfg)
    validated_reflection_spectrum = torch.tensor(
        [
            0.08163995,
            0.21881801,
            0.11293128,
            0.08326362,
            0.76207314,
        ]
    )
    validated_transmission_spectrum = torch.tensor(
        [
            0.14337483,
            0.63959249,
            0.48796375,
            0.21393022,
            0.00167027,
        ]
    )
    assert all(
        torch.abs(torch.tensor(transmission_spectrum) - validated_transmission_spectrum)
        < 1e-8
    )
    assert all(
        torch.abs(torch.tensor(reflection_spectrum) - validated_reflection_spectrum)
        < 1e-8
    )
    assert all(e <= 1 for e in transmission_spectrum)
    assert all(e <= 1 for e in reflection_spectrum)
    assert all(e >= 0 for e in transmission_spectrum)
    assert all(e >= 0 for e in reflection_spectrum)


def test_single_patterned_layer():
    """Test that a pattern layer returns teh correct spectrum"""
    # TODO: Test patterned layer, must be implemented first
    pass


if __name__ == "__main__":
    test_fdtd_grid_creation()
    test_fdtd_simulation_single_layer()
    test_fdtd_simulation_four_layers()
    test_single_patterned_layer()