"""A stand alone (from other MLS libraries) package for generating kernel plots
in MLS quality document

Note, this same module also produces summaries of each of the vertical and
horizontal resolutions for each kernel file. (This is to retain something of the
backwards capability of the old IDL code.)

This uses xarray, netcdf, matplotlib etc., but attempts to be genuinely portable
and future proof, so eschews some existing MLS libraries (though it does borrow
from them), so it can live in Overleaf and/or github relatively simply.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast, Optional

from numpy.typing import NDArray
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from matplotlib.axes import Axes
from matplotlib.ticker import MultipleLocator
from matplotlib.gridspec import SubplotSpec
from matplotlib.ticker import ScalarFormatter, FuncFormatter

SOURCE_PATH = Path("../data")
DESTINATION_PATH = Path("../new_kernel_figures")
ALONG_TRACK_SPACING = 165.0


def setup_figures() -> dict[str, BaseKernelFigure]:
    """Creates all the figures"""
    kernels = read_kernels()
    figures: dict[str, BaseKernelFigure] = {
        "BrO": HorizontalOnlyKernelFigure(
            product="BrO",
            kernels=kernels,
            pressure_range=slice(10, 0.1),
        ),
        "CH3Cl": StandardKernelFigure(
            product="CH3Cl",
            kernels=kernels,
            pressure_range=slice(1000, 0.1),
        ),
        "CH3CN": StandardKernelFigure(
            product="CH3CN",
            kernels=kernels,
            pressure_range=slice(1000, 0.1),
        ),
        "CH3OH": StandardKernelFigure(
            product="CH3OH",
            kernels=kernels,
            pressure_range=slice(1000, 0.1),
        ),
        "ClO": StandardKernelFigure(
            product="ClO",
            kernels=kernels,
            pressure_range=slice(1000, 0.01),
        ),
        "CO": StandardKernelFigure(
            product="CO",
            kernels=kernels,
            pressure_range=slice(1000, 0.000_46),
        ),
        "H2O_HR": StandardKernelFigure(
            product="H2O",
            kernels=kernels,
            pressure_range=slice(1000, 0.000_01),
        ),
        "HCl": StandardKernelFigure(
            product="HCl",
            kernels=kernels,
            pressure_range=slice(200, 0.1),
        ),
        "HCN": StandardKernelFigure(
            product="HCN",
            kernels=kernels,
            pressure_range=slice(100, 0.1),
        ),
        "HNO3": StandardKernelFigure(
            product="HNO3",
            kernels=kernels,
            pressure_range=slice(1000, 0.1),
        ),
        "HO2": HorizontalOnlyKernelFigure(
            product="HO2",
            kernels=kernels,
            pressure_range=slice(100, 0.1),
        ),
        "HOCl": HorizontalOnlyKernelFigure(
            product="HOCl",
            kernels=kernels,
            pressure_range=slice(100, 0.1),
        ),
        "N2O": StandardKernelFigure(
            product="N2O",
            kernels=kernels,
            pressure_range=slice(100, 0.1),
        ),
        "N2O-640": StandardKernelFigure(
            product="N2O_640",
            kernels=kernels,
            pressure_range=slice(100, 0.1),
        ),
        "O3_HR-UTLS": StandardKernelFigure(
            product="O3",
            kernels=kernels,
            pressure_range=slice(1000, 10),
        ),
        "O3_HR": StandardKernelFigure(
            product="O3",
            kernels=kernels,
            pressure_range=slice(1000, 0.000_46),
        ),
        "OH": DayNightKernelFigure(
            product="OH",
            kernels=kernels,
            pressure_range=slice(100, 0.001),
        ),
        "SO2": StandardKernelFigure(
            product="SO2",
            kernels=kernels,
            pressure_range=slice(1000, 1),
        ),
        "Temperature_HR": StandardKernelFigure(
            product="Temperature",
            kernels=kernels,
            pressure_range=slice(1000, 0.000_1),
        ),
    }
    # Copy the key into the name
    for name, figure in figures.items():
        figure.name = name
    # OK, done
    return figures


def read_kernels() -> xr.DataTree:
    """Read all the 1D averaging kernel NetCDF files into a DataTree"""
    # Find all the files
    netcdf_files = list(SOURCE_PATH.glob("*1D*.nc4"))
    result = xr.DataTree()
    for netcdf_file in netcdf_files:
        key = netcdf_file.stem.split("_")[-1]
        result[key] = xr.open_datatree(netcdf_file).load()
    return result


def draw_figures(
    figures: dict[str, BaseKernelFigure],
    **kwargs,
):
    """Draw all the figures"""
    # Set up some plot defaults that apply to the indented block beneath
    with plt.rc_context(
        {
            "xtick.minor.visible": True,
            "ytick.minor.visible": True,
            "font.family": "Times New Roman",
            "xtick.direction": "in",
            "ytick.direction": "in",
        }
    ):
        print("Doing averaging kernel plots: ", end="")
        # Loop over the figures and draw them.
        for key, figure in figures.items():
            print(f"{key}, ", end="")
            figure.draw(**kwargs)
        print("done.")


@dataclass
class BaseKernelFigure:
    """This defines a generic Averaging Kernel figure in the MLS quality document

    Attributes:
    -----------
    name : str
        The name for the figure (used for filenames etc.)
    n_rows : int
        The number of rows in the figure
    n_columns : int
        The number of columns in the figure
    panels : list[KernelPanel]
        The information on each specific panel in the figure
    panel_titles : list[str]
        The titles to give each row in the figure
    """

    name: str
    n_rows: int
    n_columns: int
    panels: list[KernelPanel]
    panel_titles: list[str]

    def draw(self, **kwargs):
        """Draw the averaging kernel figure

        kwargs are passed onto the drawing code."""
        # Work out how big the figure is going to be, the size in cm is drawn
        # from the predecessor IDL code
        figsize_cm = [16, 2 + self.n_rows * 8]
        figsize_inches = [s / 2.54 for s in figsize_cm]
        # Set up the figure
        figure, axes = plt.subplots(
            nrows=self.n_rows,
            ncols=self.n_columns,
            figsize=figsize_inches,
            layout="constrained",
        )

        # Draw the panels
        for ax, panel in zip(axes.ravel(), self.panels):
            # Draw the panel
            panel.draw(ax=ax, **kwargs)
            # Suppress the y axes for all but the first columns
            assert isinstance(ax, Axes)
            if cast(SubplotSpec, ax.get_subplotspec()).colspan.start != 0:
                ax.tick_params(labelleft=False)
                ax.set_ylabel("")

        # First pass establishes constrained layout
        figure.canvas.draw()
        # Build up the annotations
        annotations = []
        for row_title, ax in zip(self.panel_titles, axes.ravel()):
            if not row_title:
                continue
            bbox = ax.get_tightbbox()
            bbox_fig = bbox.transformed(figure.transFigure.inverted())
            annotations.append((bbox_fig.x0 + 0.01, bbox_fig.y1 + 0.015, row_title))
        # Now geometry is settled. Add figure-level text LAST.
        for x, y, row_title in annotations:
            figure.text(
                x,
                y,
                row_title,
                ha="left",
                va="bottom",
                fontsize=12,
                bbox={
                    "boxstyle": "square,pad=0.3",
                    "facecolor": "lightgrey",
                    "edgecolor": "black",
                },
            )
        # Save the figure to a PDF file
        figure.savefig(
            DESTINATION_PATH / f"avk-{self.name}.pdf",
            metadata={
                "CreationDate": None,
                "ModDate": None,
            },
        )
        plt.close()


class TwoRowKernelFigure(BaseKernelFigure):
    """A very typical kernel figure layout

    Being a 2x2 array of plots, with rows showing for various bins, and the
    columns showing vertical and horizontal kernels.
    """

    def __init__(
        self,
        product: str,
        kernels: xr.DataTree,
        pressure_range: slice,
        bin_labels: dict[str, str],
        name: Optional[str] = None,
    ):
        # Create a suitable BaseKernelFigure entry.
        # bin_labels: dict[str, str] = {
        #     "EQ": "Equator",
        #     "70N": "70ºN",
        # }
        n_rows = 2
        n_columns = 2
        panels: list[KernelPanel] = []
        panel_titles = []
        for bin, bin_label in bin_labels.items():
            # Append the row title
            panel_titles.append(bin_label)
            # Append the relevant vertical kernel plot
            panels.append(
                KernelPanel(
                    flavor="vertical",
                    kernel=kernels[f"{bin}/{product}"].data_vars["avkv"],
                    pressure_range=pressure_range,
                )
            )
            # Now the relevant horizontal kernel plot (no title here)
            panel_titles.append("")
            panels.append(
                KernelPanel(
                    flavor="horizontal",
                    kernel=kernels[f"{bin}/{product}"].data_vars["avkh"],
                    pressure_range=pressure_range,
                )
            )
        # If we don't have a name, use our product name as such.
        if name is None:
            name = product
        # OK, now populate the BaseKernelFigure entry.
        super().__init__(
            n_rows=n_rows,
            n_columns=n_columns,
            panels=panels,
            panel_titles=panel_titles,
            name=name,
        )


class StandardKernelFigure(TwoRowKernelFigure):
    """The most common kind of averaging kernel figure

    Being a 2x2 array of plots, with rows showing the kernel for the equator and
    70N, and the columns showing vertical and horizontal kernels.
    """

    def __init__(
        self,
        product: str,
        kernels: xr.DataTree,
        pressure_range: slice,
        name: Optional[str] = None,
    ):
        bin_labels: dict[str, str] = {
            "EQ": "Equator",
            "70N": "70ºN",
        }
        super().__init__(
            product=product,
            kernels=kernels,
            pressure_range=pressure_range,
            name=name,
            bin_labels=bin_labels,
        )


class DayNightKernelFigure(TwoRowKernelFigure):
    """The most common kind of averaging kernel figure

    Being a 2x2 array of plots, with rows showing the kernel day and night, and
    the columns showing vertical and horizontal kernels.
    """

    def __init__(
        self,
        product: str,
        kernels: xr.DataTree,
        pressure_range: slice,
        name: Optional[str] = None,
    ):
        bin_labels: dict[str, str] = {
            "EQ": "Day",
            "78N-night": "Night",
        }
        super().__init__(
            product=product,
            kernels=kernels,
            pressure_range=pressure_range,
            name=name,
            bin_labels=bin_labels,
        )


class HorizontalOnlyKernelFigure(BaseKernelFigure):
    """The most common kind of averaging kernel figure

    Being a 2x2 array of plots, with rows showing the kernel for the equator and
    70N, and the columns showing vertical and horizontal kernels.
    """

    def __init__(
        self,
        product: str,
        kernels: xr.DataTree,
        pressure_range: slice,
    ):
        # Create a suitable BaseKernelFigure entry.
        bin_labels: dict[str, str] = {
            "EQ": "Equator",
            "70N": "70ºN",
        }
        n_rows = 1
        n_columns = 2
        panels: list[KernelPanel] = []
        panel_titles = []
        for bin, bin_label in bin_labels.items():
            # Append the row title
            panel_titles.append(bin_label)
            # Append the relevant vertical kernel plot
            panels.append(
                KernelPanel(
                    flavor="vertical",
                    kernel=kernels[f"{bin}/{product}"].data_vars["avkv"],
                    pressure_range=pressure_range,
                )
            )
        # OK, now populate the BaseKernelFigure entry.
        super().__init__(
            name=product,
            n_rows=n_rows,
            n_columns=n_columns,
            panels=panels,
            panel_titles=panel_titles,
        )


@dataclass
class KernelPanel:
    """Describes a single panel in an averaging kernel figure

    Attributes:
    -----------
    flavor: str; Literal["horizontal", "vertical"]
        Whether this panel is to contain a horizontal or vertical averaging
        kernel
    kernel: xr.DataArray
        The averaging kernel information itself (drawn from the 1D NetCDF files
        attached to the quality document).
    pressure_range: slice
        The pressure range (in hPa, bottom to top) over which to show the panel
    """

    flavor: Literal["horizontal", "vertical"]
    kernel: xr.DataArray
    pressure_range: slice

    def draw(
        self,
        ax: Axes,
        **kwargs: dict[str, Any],
    ):
        """Do the work to populate a panel in the averaging kernel figure

        Parameters
        ----------
        ax : Axes
            The matplotlib axes (aka panel itself) to populate
        **kwargs : dict[str, Any]
            Passed on to the drawing routine
        """
        if self.flavor == "vertical":
            draw_vertical_kernel(
                ax=ax,
                kernel=self.kernel,
                pressure_range=self.pressure_range,
                **kwargs,
            )
        elif self.flavor == "horizontal":
            draw_horizontal_kernel(
                ax=ax,
                kernel=self.kernel,
                pressure_range=self.pressure_range,
                **kwargs,
            )
        else:
            raise ValueError(
                f"Invalid panel flavor ({self.flavor!r}), "
                'expected "horizontal" or "vertical"'
            )


def draw_vertical_kernel(ax: Axes, kernel: xr.DataArray, pressure_range: slice):
    """Draw a vertical averaging kernel panel

    Parameters
    ----------
    ax : Axes
        The matplotlib Axes in which to render the kernel
    kernel : xr.DataArray
        The kernel information itself
    pressure_range : slice
        The pressure range over which to show the kernel
    """
    # Set up the bottom x axis range/label
    ax.set_xlim(-0.2, 1.2)
    ax.xaxis.set_major_locator(MultipleLocator(0.2))
    ax.set_xlabel("Kernel, Integrated kernel")
    # Setup the the top (vertical resolution axis)
    top_axis = ax.twiny()
    top_axis.xaxis.set_major_locator(MultipleLocator(2))
    top_axis.set_xlim(-2, 12)
    top_axis.set_xlabel("FWHM / km")
    # Setup the y axis
    setup_y_axis(ax=ax, pressure_range=pressure_range)
    # Now subset the kernel information appropriately (don't forget pressure
    # runs backwards, hence the specifics of the <= and >=).
    relevant = (
        (kernel["RetrievalLevel"] <= pressure_range.start)
        & (kernel["RetrievalLevel"] >= pressure_range.stop)
        & (kernel["TruthLevel"] <= pressure_range.start)
        & (kernel["TruthLevel"] >= pressure_range.stop)
    )
    data = kernel.where(relevant, drop=True)
    # Pick colors
    n_levels = data.sizes["RetrievalLevel"]
    colors = plt.colormaps["rainbow"](np.linspace(0, 1, n_levels))
    # Now show the lines and the symbol at the "peak" (old-style loop is simplest).
    for i_level in range(n_levels):
        # Show the line
        ax.plot(
            data.isel({"RetrievalLevel": i_level}),
            data["TruthLevel"],
            color=colors[i_level],
            linewidth=1.0,
        )
        # Put a plus sign at the home level
        ax.plot(
            data.isel({"RetrievalLevel": i_level, "TruthLevel": i_level}),
            data["TruthLevel"].isel({"TruthLevel": i_level}),
            marker="+",
            color=colors[i_level],
        )
    # Show the integrated kernel (xarray makes this so simple!)
    ax.plot(
        kernel.sum(dim="TruthLevel"),
        kernel["RetrievalLevel"],
        color="black",
        linewidth=2,
    )
    # Compute the vertical resolution
    vertical_resolution = compute_vertical_resolution(kernel)
    ax.plot(
        vertical_resolution.values / 10,
        vertical_resolution["RetrievalLevel"],
        linestyle="dashed",
        color="black",
        linewidth=2,
    )


def draw_horizontal_kernel(ax: Axes, kernel: xr.DataArray, pressure_range: slice):
    """Draw a horizontal averaging kernel panel

    Parameters
    ----------
    ax : Axes
        The matplotlib Axes in which to render the kernel
    kernel : xr.DataArray
        The kernel information itself
    pressure_range : slice
        The pressure range over which to show the kernel
    """
    # Set up the bottom x axis range/label
    profile_span = 8
    assert (profile_span % 2) == 0, "Must have even number of profiles"
    x_lim = [-profile_span // 2, profile_span // 2]
    ax.set_xlim(*x_lim)
    ax.set_xlabel("Profile number")
    # Setup the the top (vertical resolution axis)
    top_axis = ax.twiny()
    top_axis.set_xlabel("FWHM / km")
    # The range for this is scaled to match the 165-km along-track profile scaling
    top_axis.set_xlim(0, (x_lim[1] - x_lim[0]) * ALONG_TRACK_SPACING)
    top_axis.xaxis.set_major_locator(MultipleLocator(200))
    # Setup the y axis (note that this might later be suppressed by the calling
    # code, as the axis is shared with the plot to the left)
    setup_y_axis(ax=ax, pressure_range=pressure_range)
    # Now subset the kernel information appropriately (don't forget pressure runs backwards).
    relevant = (kernel["RetrievalLevel"] <= pressure_range.start) & (
        kernel["RetrievalLevel"] >= pressure_range.stop
    )
    data = kernel.where(relevant, drop=True)
    # Pick colors
    n_levels = data.sizes["RetrievalLevel"]
    colors = plt.colormaps["rainbow"](np.linspace(0, 1, n_levels))
    # Now show the lines (old-style loop for now).
    x = np.linspace(x_lim[0], x_lim[1], profile_span + 1, endpoint=True)
    n_profiles = data.sizes["TruthPhi"]
    center_profile = n_profiles // 2
    profile_selector = {
        "TruthPhi": slice(center_profile + x_lim[0], center_profile + x_lim[1] + 1)
    }
    # Now show the lines and the symbol at the peak.
    for i_level in range(n_levels):
        level_selector = {"RetrievalLevel": i_level}
        # Show the line
        y = data["RetrievalLevel"].isel({"RetrievalLevel": i_level})
        a = data.isel(level_selector | profile_selector)
        a0 = data.isel(level_selector | {"TruthPhi": center_profile})
        y = y * 10 ** (a0 - a)
        ax.plot(
            x,
            y,
            color=colors[i_level],
            linewidth=1.0,
        )
        # Put a plus sign at the home level
        ax.plot(
            x[profile_span // 2],
            y[profile_span // 2],
            marker="+",
            color=colors[i_level],
        )
    # Show the horizontal resolution
    horizontal_resolution = compute_horizontal_resolution(data)
    ax.plot(
        horizontal_resolution + x_lim[0],
        horizontal_resolution["RetrievalLevel"],
        linestyle="dashed",
        color="black",
        linewidth=2,
    )


def setup_y_axis(ax: Axes, pressure_range: slice):
    """Generic y (pressure) axis setup"""
    ax.set_yscale("log")
    ax.set_ylim(pressure_range.start, pressure_range.stop)
    ax.set_ylabel("Pressure / hPa")
    formatter = ScalarFormatter()
    formatter.set_scientific(False)
    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda x, _: f"{x:.10f}".rstrip("0").rstrip("."))
    )


def compute_vertical_resolution(avkv: xr.DataArray) -> xr.DataArray:
    """Given a vertical kernel, compute the FWHM-based resolution"""
    z = 16.0 * (3.0 - np.log10(avkv["RetrievalLevel"]))
    return xr.DataArray(
        fwhm(z, avkv.values),
        coords={"RetrievalLevel": avkv["RetrievalLevel"]},
    )


def compute_horizontal_resolution(avkh: xr.DataArray) -> xr.DataArray:
    """Given a horizontal kernel, compute the FWHM-based resolution"""
    # Generate an x coordinate for the fwhm routine
    x = np.arange(avkh.sizes["TruthPhi"])
    return xr.DataArray(
        fwhm(x, avkh.values.T),
        coords={"RetrievalLevel": avkh["RetrievalLevel"]},
    )


def generate_ascii_summary_file(kernel: xr.Dataset, filename: str | Path, product: str):
    """Generates an ascii file from a given 1D averaging kernel"""
    # Compute the widths

    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"Averaging kernel etc. information for: {product}\n")
        vertical_resolution = compute_vertical_resolution(kernel.data_vars["avkv"])
        horizontal_resolution = (
            compute_horizontal_resolution(kernel.data_vars["avkh"])
            * ALONG_TRACK_SPACING
        )
        integrated_kernel = kernel.data_vars["avkv"].sum(dim="TruthLevel")
        # Setup the column widths
        titles = ["p/hPa", "VR/km", "HR/km"]
        widths = [12, 10, 10]
        # Now loop over the levels and print out the resolutions where they make sense
        file.write(" ".join([f"{t:>{w}}" for t, w in zip(titles, widths)]) + "\n")
        for i_level in range(kernel.sizes["RetrievalLevel"]):
            if integrated_kernel[i_level] < 1e-3:
                continue
            values = [
                kernel["RetrievalLevel"][i_level],
                vertical_resolution[i_level],
                horizontal_resolution[i_level],
            ]
            file.write(" ".join([f"{v:{w}g}" for v, w in zip(values, widths)]) + "\n")


def generate_all_ascii_summary_files(kernels: xr.DataTree):
    """Generate all the ASCII summary files"""
    destination = DESTINATION_PATH / "ascii-summaries"
    destination.mkdir(parents=True, exist_ok=True)
    for bin_name, bin in kernels.children.items():
        for product, kernel in bin.children.items():
            filename = destination / f"avk-{product}-{bin_name}-summary.txt"
            generate_ascii_summary_file(
                kernel=kernel,
                filename=filename,
                product=product,
            )


def fwhm(z: NDArray, A: NDArray) -> NDArray:
    """Compute a set of FWHMs for an averaging kernel"""
    m = A.shape[0]
    result = np.zeros(shape=[m])
    for i in range(m):
        result[i] = fwhm_vector(z, A[i, :])
    return result


def fwhm_vector(z: NDArray, a: NDArray) -> float:
    """Compute the FWHM for a row of the averaging kernel"""
    # Locate the maximum
    max_i = np.argmax(a)
    max_a = a[max_i]
    half_max = max_a / 2
    # Check that there is actually a maximum
    if max_a == np.min(a):
        return np.nan
    # Now search forward from the maximum to the first place where it goes below half
    # max
    try:
        i1 = max_i + np.nonzero(a[max_i:] < half_max)[0][0]
        i0 = i1 - 1
        z_upper = li(a[i1], a[i0], z[i1], z[i0], half_max)
    except IndexError:
        z_upper = z[-1]
    try:
        i0 = max_i - np.nonzero(a[max_i::-1] < half_max)[0][0]
        i1 = i0 + 1
        z_lower = li(a[i1], a[i0], z[i1], z[i0], half_max)
    except IndexError:
        z_lower = z[0]
    return float(z_upper - z_lower)


def li(a1, a0, z1, z0, a):
    """A very quick linear interpolator"""
    return z0 + (z1 - z0) / (a1 - a0) * (a - a0)


if __name__ == "__main__":
    """If we're just run on the command line, do all the work"""
    figures = setup_figures()
    draw_figures(figures)


# cspell: words avkh
# cspell: words avkv
# cspell: words boxstyle
# cspell: words colormaps
# cspell: words edgecolor
# cspell: words facecolor
# cspell: words figsize
# cspell: words fontsize
# cspell: words FWHM
# cspell: words gridspec
# cspell: words labelleft
# cspell: words linestyle
# cspell: words subplotspec
# cspell: words textcoords
# cspell: words tightbbox
# cspell: words UTLS
# cspell: words xlabel
# cspell: words xlim
# cspell: words xtick
# cspell: words xycoords
# cspell: words xytext
# cspell: words ylabel
# cspell: words ylim
# cspell: words yscale
# cspell: words ytick
# cspell: words zorder
