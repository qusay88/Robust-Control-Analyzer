import customtkinter as ctk
import control as ct
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox, filedialog


# ============================================================
# ROBUST CONTROL ANALYZER V4
# ============================================================
#
# Classical Stability + Disk Margin + Robustness
#
# ============================================================


# ============================================================
# APPLICATION
# ============================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()

app.title(
    "Robust Control Analyzer V4"
)

app.geometry(
    "1600x950"
)

app.minsize(
    1250,
    800
)

app.configure(
    fg_color="#0B1120"
)


# ============================================================
# COLORS
# ============================================================

BG = "#0B1120"
PANEL = "#111827"
PANEL2 = "#1E293B"

BLUE = "#2563EB"
BLUE_HOVER = "#1D4ED8"

PURPLE = "#7C3AED"
PURPLE_HOVER = "#6D28D9"

GREEN = "#22C55E"
RED = "#EF4444"
YELLOW = "#F59E0B"

WHITE = "#F8FAFC"
GRAY = "#94A3B8"

BORDER = "#334155"


# ============================================================
# GLOBAL RESULT
# ============================================================

current_result = None
current_figures = {}


# ============================================================
# BASIC FUNCTIONS
# ============================================================

def fmt(value, digits=5):

    try:

        value = float(value)

        if np.isnan(value):
            return "N/A"

        if np.isinf(value):
            return "∞"

        return f"{value:.{digits}f}"

    except:

        return "N/A"


# ------------------------------------------------------------

def parse_coefficients(text):

    text = text.strip()

    if not text:
        raise ValueError(
            "Coefficient field cannot be empty."
        )

    text = text.replace(
        ";",
        ","
    )

    parts = text.split(",")

    result = []

    for item in parts:

        item = item.strip()

        if item:
            result.append(
                float(item)
            )

    if not result:
        raise ValueError(
            "Invalid coefficients."
        )

    return result


# ------------------------------------------------------------

def frequency_vector():

    fmin = float(
        freq_min.get()
    )

    fmax = float(
        freq_max.get()
    )

    if fmin <= 0:
        raise ValueError(
            "Minimum frequency must be > 0."
        )

    if fmax <= fmin:
        raise ValueError(
            "Maximum frequency must be greater than minimum."
        )

    return np.logspace(
        np.log10(fmin),
        np.log10(fmax),
        2000
    )


# ============================================================
# POLYNOMIAL TEXT
# ============================================================

def polynomial_to_string(
    coefficients,
    variable="s"
):

    coefficients = np.asarray(
        coefficients,
        dtype=float
    )

    degree = len(coefficients) - 1

    terms = []

    for i, coeff in enumerate(coefficients):

        power = degree - i

        if abs(coeff) < 1e-12:
            continue

        sign = "+" if coeff > 0 else "-"

        value = abs(coeff)

        if power == 0:

            term = f"{value:g}"

        elif power == 1:

            if abs(value - 1) < 1e-12:
                term = variable
            else:
                term = f"{value:g}{variable}"

        else:

            if abs(value - 1) < 1e-12:
                term = f"{variable}^{power}"
            else:
                term = f"{value:g}{variable}^{power}"

        if not terms:

            if coeff < 0:
                terms.append(
                    "-" + term
                )
            else:
                terms.append(
                    term
                )

        else:

            terms.append(
                f" {sign} {term}"
            )

    return "".join(terms) or "0"


# ------------------------------------------------------------

def transfer_function_string(
    numerator,
    denominator
):

    n = polynomial_to_string(
        numerator
    )

    d = polynomial_to_string(
        denominator
    )

    return (
        f"G(s) = ({n}) / ({d})"
    )


# ============================================================
# ROUGH TIME VECTOR
# ============================================================

def make_time_vector(system):

    try:

        poles = np.asarray(
            ct.poles(system)
        )

        stable_poles = poles[
            np.real(poles) < -1e-8
        ]

        if len(stable_poles) > 0:

            slowest = np.min(
                np.abs(
                    np.real(
                        stable_poles
                    )
                )
            )

            tfinal = max(
                10 / slowest,
                10
            )

        else:

            tfinal = 20

    except:

        tfinal = 20

    return np.linspace(
        0,
        min(tfinal, 10000),
        2000
    )


# ============================================================
# CLEAR FRAME
# ============================================================

def clear_frame(frame):

    for widget in frame.winfo_children():
        widget.destroy()


# ============================================================
# FIGURE DISPLAY
# ============================================================

def display_figure(
    frame,
    fig,
    key
):

    clear_frame(
        frame
    )

    canvas = FigureCanvasTkAgg(
        fig,
        master=frame
    )

    canvas.draw()

    canvas.get_tk_widget().pack(
        fill="both",
        expand=True
    )

    current_figures[key] = fig


# ============================================================
# HEADER
# ============================================================

header = ctk.CTkFrame(
    app,
    fg_color=PANEL,
    corner_radius=0
)

header.pack(
    fill="x"
)


ctk.CTkLabel(
    header,
    text="ROBUST CONTROL ANALYZER V4",
    text_color=WHITE,
    font=ctk.CTkFont(
        size=29,
        weight="bold"
    )
).pack(
    pady=(16, 2)
)


ctk.CTkLabel(
    header,
    text=(
        "Classical Stability • Routh-Hurwitz • "
        "Disk Margin • Robustness"
    ),
    text_color=GRAY,
    font=ctk.CTkFont(
        size=14
    )
).pack(
    pady=(0, 15)
)


# ============================================================
# MAIN
# ============================================================

main = ctk.CTkFrame(
    app,
    fg_color=BG
)

main.pack(
    fill="both",
    expand=True,
    padx=12,
    pady=12
)


# ============================================================
# LEFT SCROLLABLE PANEL
# ============================================================

left = ctk.CTkScrollableFrame(
    main,
    width=350,
    fg_color=PANEL,
    corner_radius=15
)

left.pack(
    side="left",
    fill="y",
    padx=(0, 12)
)


# ============================================================
# INPUT TITLE
# ============================================================

ctk.CTkLabel(
    left,
    text="SYSTEM INPUT",
    text_color=WHITE,
    font=ctk.CTkFont(
        size=19,
        weight="bold"
    )
).pack(
    pady=(15, 18)
)


# ============================================================
# NUMERATOR
# ============================================================

ctk.CTkLabel(
    left,
    text="Numerator coefficients",
    text_color=GRAY
).pack(
    anchor="w",
    padx=12
)


num_entry = ctk.CTkEntry(
    left,
    height=42,
    placeholder_text="Example: 1, 3"
)

num_entry.pack(
    fill="x",
    padx=12,
    pady=(5, 15)
)


# ============================================================
# DENOMINATOR
# ============================================================

ctk.CTkLabel(
    left,
    text="Denominator coefficients",
    text_color=GRAY
).pack(
    anchor="w",
    padx=12
)


den_entry = ctk.CTkEntry(
    left,
    height=42,
    placeholder_text="Example: 1, 2, 5"
)

den_entry.pack(
    fill="x",
    padx=12,
    pady=(5, 15)
)


# ============================================================
# FEEDBACK
# ============================================================

ctk.CTkLabel(
    left,
    text="Feedback configuration",
    text_color=GRAY
).pack(
    anchor="w",
    padx=12
)


feedback = ctk.CTkComboBox(
    left,
    values=[
        "Negative Feedback",
        "Positive Feedback"
    ],
    height=40
)

feedback.set(
    "Negative Feedback"
)

feedback.pack(
    fill="x",
    padx=12,
    pady=(5, 15)
)


# ============================================================
# FREQUENCY
# ============================================================

ctk.CTkLabel(
    left,
    text="Frequency range (rad/s)",
    text_color=GRAY
).pack(
    anchor="w",
    padx=12
)


freq_frame = ctk.CTkFrame(
    left,
    fg_color="transparent"
)

freq_frame.pack(
    fill="x",
    padx=12,
    pady=(5, 15)
)


freq_min = ctk.CTkEntry(
    freq_frame,
    height=38
)

freq_min.insert(
    0,
    "0.001"
)

freq_min.pack(
    side="left",
    fill="x",
    expand=True,
    padx=(0, 3)
)


freq_max = ctk.CTkEntry(
    freq_frame,
    height=38
)

freq_max.insert(
    0,
    "10000"
)

freq_max.pack(
    side="left",
    fill="x",
    expand=True,
    padx=(3, 0)
)


# ============================================================
# ROBUSTNESS
# ============================================================

ctk.CTkLabel(
    left,
    text="ROBUSTNESS TEST",
    text_color=WHITE,
    font=ctk.CTkFont(
        size=15,
        weight="bold"
    )
).pack(
    anchor="w",
    padx=12,
    pady=(10, 5)
)


ctk.CTkLabel(
    left,
    text="Gain uncertainty (%)",
    text_color=GRAY
).pack(
    anchor="w",
    padx=12
)


gain_uncertainty = ctk.CTkEntry(
    left,
    height=38
)

gain_uncertainty.insert(
    0,
    "10"
)

gain_uncertainty.pack(
    fill="x",
    padx=12,
    pady=(5, 10)
)


ctk.CTkLabel(
    left,
    text="Phase uncertainty (deg)",
    text_color=GRAY
).pack(
    anchor="w",
    padx=12
)


phase_uncertainty = ctk.CTkEntry(
    left,
    height=38
)

phase_uncertainty.insert(
    0,
    "10"
)

phase_uncertainty.pack(
    fill="x",
    padx=12,
    pady=(5, 15)
)


# ============================================================
# BUTTONS
# ============================================================

analyze_button = ctk.CTkButton(
    left,
    text="ANALYZE SYSTEM",
    height=50,
    fg_color=BLUE,
    hover_color=BLUE_HOVER,
    font=ctk.CTkFont(
        size=15,
        weight="bold"
    )
)

analyze_button.pack(
    fill="x",
    padx=12,
    pady=4
)


compare_button = ctk.CTkButton(
    left,
    text="COMPARE CLASSICAL vs DISK",
    height=42,
    fg_color=PANEL2,
    hover_color="#475569"
)

compare_button.pack(
    fill="x",
    padx=12,
    pady=4
)


robustness_button = ctk.CTkButton(
    left,
    text="RUN ROBUSTNESS TEST",
    height=42,
    fg_color=PURPLE,
    hover_color=PURPLE_HOVER
)

robustness_button.pack(
    fill="x",
    padx=12,
    pady=4
)


export_button = ctk.CTkButton(
    left,
    text="EXPORT REPORT",
    height=40,
    fg_color=PANEL2,
    hover_color="#475569"
)

export_button.pack(
    fill="x",
    padx=12,
    pady=4
)


export_figures_button = ctk.CTkButton(
    left,
    text="EXPORT FIGURES",
    height=40,
    fg_color="#0F766E",
    hover_color="#115E59"
)

export_figures_button.pack(
    fill="x",
    padx=12,
    pady=4
)


critical_button = ctk.CTkButton(
    left,
    text="CRITICAL DISTURBANCE",
    height=42,
    fg_color="#B45309",
    hover_color="#92400E"
)

critical_button.pack(
    fill="x",
    padx=12,
    pady=4
)


reset_button = ctk.CTkButton(
    left,
    text="RESET",
    height=40,
    fg_color="#1F2937",
    hover_color="#374151"
)

reset_button.pack(
    fill="x",
    padx=12,
    pady=4
)


# ============================================================
# SYSTEM INFORMATION
# ============================================================

system_info = ctk.CTkLabel(
    left,
    text=(
        "INPUT FORMAT\n\n"
        "Numerator:\n"
        "1, 3\n\n"
        "Denominator:\n"
        "0.5, 2, 1, 3\n\n"
        "Example:\n"
        "(s + 3) /\n"
        "(0.5s³ + 2s² + s + 3)"
    ),
    text_color=GRAY,
    justify="left",
    font=ctk.CTkFont(
        size=12
    )
)

system_info.pack(
    anchor="w",
    padx=12,
    pady=20
)


# ============================================================
# RIGHT AREA
# ============================================================

right = ctk.CTkFrame(
    main,
    fg_color=BG
)

right.pack(
    side="right",
    fill="both",
    expand=True
)


# ============================================================
# STATUS BAR
# ============================================================

status_bar = ctk.CTkFrame(
    right,
    fg_color=PANEL,
    corner_radius=12
)

status_bar.pack(
    fill="x",
    pady=(0, 10)
)


status_label = ctk.CTkLabel(
    status_bar,
    text="READY — Enter a system and press ANALYZE SYSTEM",
    text_color=GRAY,
    font=ctk.CTkFont(
        size=13,
        weight="bold"
    )
)

status_label.pack(
    anchor="w",
    padx=18,
    pady=9
)


# ============================================================
# DASHBOARD
# ============================================================

dashboard = ctk.CTkFrame(
    right,
    fg_color=BG
)

dashboard.pack(
    fill="x",
    pady=(0, 10)
)


def create_card(
    parent,
    title
):

    card = ctk.CTkFrame(
        parent,
        fg_color=PANEL,
        corner_radius=12
    )

    card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=3
    )


    ctk.CTkLabel(
        card,
        text=title,
        text_color=GRAY,
        font=ctk.CTkFont(
            size=11,
            weight="bold"
        )
    ).pack(
        pady=(9, 2)
    )


    value = ctk.CTkLabel(
        card,
        text="—",
        text_color=WHITE,
        font=ctk.CTkFont(
            size=18,
            weight="bold"
        )
    )

    value.pack(
        pady=(2, 9)
    )

    return value


gm_card = create_card(
    dashboard,
    "GAIN MARGIN"
)

pm_card = create_card(
    dashboard,
    "PHASE MARGIN"
)

dm_card = create_card(
    dashboard,
    "BALANCED DISK MARGIN"
)

stability_card = create_card(
    dashboard,
    "NOMINAL STABILITY"
)

robust_card = create_card(
    dashboard,
    "ROBUSTNESS"
)


# ============================================================
# EQUATION DISPLAY
# ============================================================

equation_frame = ctk.CTkFrame(
    right,
    fg_color=PANEL,
    corner_radius=12
)

equation_frame.pack(
    fill="x",
    pady=(0, 10)
)


equation_label = ctk.CTkLabel(
    equation_frame,
    text="G(s) = —",
    text_color=WHITE,
    font=ctk.CTkFont(
        size=15,
        weight="bold"
    )
)

equation_label.pack(
    anchor="w",
    padx=18,
    pady=(8, 2)
)


closed_loop_label = ctk.CTkLabel(
    equation_frame,
    text="Closed-loop: —",
    text_color=GRAY,
    font=ctk.CTkFont(
        size=13
    )
)

closed_loop_label.pack(
    anchor="w",
    padx=18,
    pady=(2, 8)
)


# ============================================================
# TABS
# ============================================================

tabs = ctk.CTkTabview(
    right,
    fg_color=PANEL
)

tabs.pack(
    fill="both",
    expand=True
)


tab_names = [
    "Overview",
    "Bode",
    "Nyquist",
    "Disk Margin",
    "Critical Disturbance",
    "Pole-Zero",
    "Step Response",
    "Routh-Hurwitz",
    "Comparison",
    "Robustness",
    "Uncertainty Map",
    "Report"
]

for name in tab_names:
    tabs.add(name)


# ============================================================
# TAB REFERENCES
# ============================================================

overview_tab = tabs.tab("Overview")
bode_tab = tabs.tab("Bode")
nyquist_tab = tabs.tab("Nyquist")
disk_tab = tabs.tab("Disk Margin")
critical_tab = tabs.tab("Critical Disturbance")
pole_tab = tabs.tab("Pole-Zero")
step_tab = tabs.tab("Step Response")
routh_tab = tabs.tab("Routh-Hurwitz")
comparison_tab = tabs.tab("Comparison")
robustness_tab = tabs.tab("Robustness")
uncertainty_tab = tabs.tab("Uncertainty Map")
report_tab = tabs.tab("Report")


# ============================================================
# OVERVIEW
# ============================================================

overview_box = ctk.CTkTextbox(
    overview_tab,
    font=ctk.CTkFont(
        size=14
    )
)

overview_box.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=15
)


# ============================================================
# TEXT BOXES
# ============================================================

comparison_box = ctk.CTkTextbox(
    comparison_tab,
    font=ctk.CTkFont(
        size=14
    )
)

comparison_box.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=15
)


robustness_box = ctk.CTkTextbox(
    robustness_tab,
    font=ctk.CTkFont(
        size=14
    )
)

robustness_box.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=15
)


report_box = ctk.CTkTextbox(
    report_tab,
    font=ctk.CTkFont(
        size=13
    )
)

report_box.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=15
)


# ============================================================
# ROUTH-HURWITZ
# ============================================================

routh_box = ctk.CTkTextbox(
    routh_tab,
    font=ctk.CTkFont(
        size=14
    )
)

routh_box.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=15
)


# ============================================================
# ROUTH TABLE
# ============================================================

def routh_table(
    coefficients
):

    coeff = np.asarray(
        coefficients,
        dtype=float
    )

    n = len(coeff)

    m = int(
        np.ceil(n / 2)
    )

    rows = n

    table = np.zeros(
        (rows, m)
    )


    # First row
    table[0, :len(
        coeff[::2]
    )] = coeff[::2]


    # Second row
    if rows > 1:

        table[1, :len(
            coeff[1::2]
        )] = coeff[1::2]


    eps = 1e-9


    for i in range(
        2,
        rows
    ):

        if np.all(
            np.abs(
                table[i - 1]
            ) < eps
        ):

            table[i - 1, 0] = eps


        for j in range(
            m - 1
        ):

            a = table[i - 2, 0]

            b = table[i - 2, j + 1]

            c = table[i - 1, 0]

            d = table[i - 1, j + 1]


            if abs(c) < eps:
                c = eps


            table[i, j] = (
                (
                    c * b
                )
                -
                (
                    a * d
                )
            ) / c


    return table


# ============================================================
# ROUTH ANALYSIS
# ============================================================

def analyze_routh(
    coefficients
):

    table = routh_table(
        coefficients
    )


    first_column = table[
        :,
        0
    ]


    signs = []

    for value in first_column:

        if abs(value) < 1e-9:

            signs.append(
                0
            )

        else:

            signs.append(
                1 if value > 0 else -1
            )


    nonzero_signs = [
        x for x in signs
        if x != 0
    ]


    changes = 0

    for i in range(
        len(nonzero_signs) - 1
    ):

        if (
            nonzero_signs[i]
            !=
            nonzero_signs[i + 1]
        ):

            changes += 1


    stable = (
        changes == 0
        and
        all(
            x > 0
            for x in nonzero_signs
        )
    )


    return (
        table,
        first_column,
        changes,
        stable
    )


# ============================================================
# BODE
# ============================================================

def plot_bode(
    system,
    omega
):

    response = ct.frequency_response(
        system,
        omega
    )


    magnitude = np.squeeze(
        response.magnitude
    )


    phase = np.squeeze(
        response.phase
    )


    magnitude_db = (
        20 *
        np.log10(
            np.maximum(
                magnitude,
                1e-12
            )
        )
    )


    phase_deg = (
        np.unwrap(
            phase
        )
        *
        180
        /
        np.pi
    )


    fig = plt.Figure(
        figsize=(9, 6),
        dpi=100
    )


    ax1 = fig.add_subplot(
        211
    )

    ax2 = fig.add_subplot(
        212
    )


    ax1.semilogx(
        omega,
        magnitude_db,
        linewidth=2
    )

    ax1.axhline(
        0,
        linestyle="--",
        linewidth=1
    )


    ax1.set_ylabel(
        "Magnitude (dB)"
    )

    ax1.set_title(
        "Bode Magnitude"
    )


    ax1.grid(
        True,
        which="both",
        alpha=0.3
    )


    ax2.semilogx(
        omega,
        phase_deg,
        linewidth=2
    )

    ax2.axhline(
        -180,
        linestyle="--",
        linewidth=1
    )


    ax2.set_xlabel(
        "Frequency (rad/s)"
    )

    ax2.set_ylabel(
        "Phase (deg)"
    )


    ax2.set_title(
        "Bode Phase"
    )


    ax2.grid(
        True,
        which="both",
        alpha=0.3
    )


    fig.tight_layout()


    display_figure(
        bode_tab,
        fig,
        "bode"
    )


# ============================================================
# NYQUIST
# ============================================================

def plot_nyquist(
    system,
    omega
):

    response = ct.frequency_response(
        system,
        omega
    )


    magnitude = np.squeeze(
        response.magnitude
    )

    phase = np.squeeze(
        response.phase
    )


    response_complex = (
        magnitude *
        np.exp(
            1j * phase
        )
    )


    fig = plt.Figure(
        figsize=(8, 7),
        dpi=100
    )


    ax = fig.add_subplot(
        111
    )


    ax.plot(
        response_complex.real,
        response_complex.imag,
        linewidth=2,
        label="G(jω)"
    )


    ax.plot(
        response_complex.real,
        -response_complex.imag,
        linestyle="--",
        alpha=0.45,
        label="Mirror"
    )


    ax.scatter(
        [-1],
        [0],
        marker="x",
        s=140,
        linewidths=3,
        label="Critical Point"
    )


    ax.axhline(
        0,
        linewidth=1
    )

    ax.axvline(
        0,
        linewidth=1
    )


    ax.set_xlabel(
        "Real Axis"
    )

    ax.set_ylabel(
        "Imaginary Axis"
    )


    ax.set_title(
        "Nyquist Plot"
    )


    ax.grid(
        True,
        alpha=0.3
    )


    ax.legend()

    ax.axis(
        "equal"
    )


    fig.tight_layout()


    display_figure(
        nyquist_tab,
        fig,
        "nyquist"
    )


# ============================================================
# DISK MARGIN
# ============================================================

def calculate_disk(
    system,
    omega
):

    results = {}

    for skew, name in [
        (1.0, "s"),
        (0.0, "balanced"),
        (-1.0, "t")
    ]:

        dm, dgm, dpm = ct.disk_margins(
            system,
            omega,
            skew=skew
        )


        results[
            name
        ] = {

            "dm": float(dm),

            "dgm": float(dgm),

            "dpm": float(dpm)
        }


        try:

            dm_curve, dgm_curve, dpm_curve = (
                ct.disk_margins(
                    system,
                    omega,
                    skew=skew,
                    returnall=True
                )
            )


            results[
                name
            ][
                "curve"
            ] = np.asarray(
                dm_curve
            )


        except:

            results[
                name
            ][
                "curve"
            ] = None


    # --------------------------------------------------------
    # Worst case from balanced curve
    # --------------------------------------------------------

    curve = results[
        "balanced"
    ][
        "curve"
    ]


    if curve is not None:

        valid = np.isfinite(
            curve
        )


        if np.any(valid):

            valid_indices = np.where(
                valid
            )[0]


            local_index = np.argmin(
                curve[valid]
            )


            index = valid_indices[
                local_index
            ]


            results[
                "balanced"
            ][
                "worst_frequency"
            ] = float(
                omega[index]
            )


        else:

            results[
                "balanced"
            ][
                "worst_frequency"
            ] = np.nan


    else:

        results[
            "balanced"
        ][
            "worst_frequency"
        ] = np.nan


    return results


# ============================================================
# DISK PLOT
# ============================================================

def plot_disk(
    disk,
    omega
):
    """
    Research-quality Disk Margin visualization.

    Panel A:
        Frequency-dependent disk margin DM(omega) for:
        S-based (skew=+1), Balanced (skew=0), and
        T-based (skew=-1).

    Panel B:
        Allowable combined gain/phase variation at the
        worst-case (minimum) disk margin for the same
        three skew formulations.

    The numerical disk margins are computed by
    control.disk_margins(). No calculated values are
    altered by this plotting function.
    """

    fig = plt.Figure(
        figsize=(12, 6.8),
        dpi=110
    )

    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    styles = {
        "s": {
            "label": "S-based (skew=+1)",
            "color": "tab:blue",
            "linestyle": "-"
        },
        "balanced": {
            "label": "Balanced (skew=0)",
            "color": "tab:orange",
            "linestyle": "-"
        },
        "t": {
            "label": "T-based (skew=-1)",
            "color": "tab:green",
            "linestyle": "--"
        }
    }

    omega_arr = np.asarray(
        omega,
        dtype=float
    )

    # ========================================================
    # PANEL A: Frequency-dependent Disk Margin
    # ========================================================

    curves_plotted = []

    for name in ["s", "balanced", "t"]:

        curve = disk[name].get("curve")

        if curve is None:
            continue

        curve = np.asarray(
            curve,
            dtype=float
        )

        valid = (
            np.isfinite(curve)
            & np.isfinite(omega_arr)
            & (omega_arr > 0)
            & (curve > 0)
        )

        if not np.any(valid):
            continue

        ax1.semilogx(
            omega_arr[valid],
            curve[valid],
            linewidth=2.2,
            color=styles[name]["color"],
            linestyle=styles[name]["linestyle"],
            label=styles[name]["label"]
        )

        curves_plotted.append(
            curve[valid]
        )

    # A logarithmic y-axis prevents a very large low-frequency
    # margin from visually hiding the S/B/T curves with smaller
    # values. The data themselves are unchanged.
    ax1.set_yscale("log")

    # --------------------------------------------------------
    # Mark the formal minimum for all three formulations.
    # --------------------------------------------------------

    marker_offsets = {
        "s": (8, 10),
        "balanced": (8, -28),
        "t": (8, 10)
    }

    for name in ["s", "balanced", "t"]:

        curve = disk[name].get("curve")

        if curve is None:
            continue

        curve = np.asarray(
            curve,
            dtype=float
        )

        valid = (
            np.isfinite(curve)
            & np.isfinite(omega_arr)
            & (omega_arr > 0)
            & (curve > 0)
        )

        if not np.any(valid):
            continue

        valid_idx = np.where(valid)[0]

        local_idx = np.argmin(
            curve[valid]
        )

        idx = valid_idx[
            local_idx
        ]

        dm_min = float(
            curve[idx]
        )

        w_worst = float(
            omega_arr[idx]
        )

        ax1.scatter(
            w_worst,
            dm_min,
            s=55,
            color=styles[name]["color"],
            edgecolors="black",
            linewidths=0.7,
            zorder=8
        )

        dx, dy = marker_offsets[name]

        ax1.annotate(
            (
                f"{name.upper()}: "
                f"{dm_min:.4g}\n"
                f"ω={w_worst:.4g}"
            ),
            xy=(
                w_worst,
                dm_min
            ),
            xytext=(
                dx,
                dy
            ),
            textcoords="offset points",
            fontsize=8,
            bbox=dict(
                boxstyle="round,pad=0.25",
                alpha=0.85
            ),
            arrowprops=dict(
                arrowstyle="->",
                linewidth=0.9
            )
        )

    ax1.set_xlabel(
        "Frequency (rad/s)"
    )

    ax1.set_ylabel(
        "Disk Margin (absolute, log scale)"
    )

    ax1.set_title(
        "A. Frequency-Dependent Disk Margin"
    )

    ax1.grid(
        True,
        which="both",
        alpha=0.28
    )

    ax1.legend(
        fontsize=8,
        loc="best",
        framealpha=0.92
    )

    # ========================================================
    # PANEL B: Allowable Gain/Phase Region
    #
    # This follows the published python-control disk-margin
    # example:
    #
    # f = [2 + alpha(1-skew)e^(j theta)] /
    #     [2 - alpha(1+skew)e^(j theta)]
    #
    # gamma_dB = 20 log10(|f|)
    # phi_deg  = angle(f) in degrees
    #
    # alpha is the WORST-CASE disk margin returned by
    # control.disk_margins(..., returnall=False).
    # ========================================================

    theta = np.linspace(
        0,
        np.pi,
        800
    )

    for name, skew in [
        ("t", -1.0),
        ("balanced", 0.0),
        ("s", 1.0)
    ]:

        alpha = disk[name].get("dm")

        if alpha is None:
            continue

        try:
            alpha = float(alpha)
        except Exception:
            continue

        if (
            not np.isfinite(alpha)
            or alpha <= 0
        ):
            continue

        f = (
            2
            + alpha
            * (1 - skew)
            * np.exp(1j * theta)
        ) / (
            2
            - alpha
            * (1 + skew)
            * np.exp(1j * theta)
        )

        gain_db = 20 * np.log10(
            np.abs(f)
        )

        phase_deg = np.rad2deg(
            np.angle(f)
        )

        ax2.plot(
            gain_db,
            phase_deg,
            linewidth=2.2,
            color=styles[name]["color"],
            linestyle=styles[name]["linestyle"],
            label=(
                f"{styles[name]['label']}: "
                f"DM={alpha:.4g}"
            )
        )

        # Mirror the upper-half boundary to make the
        # complete gain/phase allowable region visible.
        ax2.plot(
            gain_db,
            -phase_deg,
            linewidth=1.0,
            color=styles[name]["color"],
            linestyle=styles[name]["linestyle"],
            alpha=0.45
        )

    ax2.axhline(
        0,
        linewidth=0.8,
        linestyle="--"
    )

    ax2.axvline(
        0,
        linewidth=0.8,
        linestyle="--"
    )

    ax2.scatter(
        [0],
        [0],
        s=35,
        color="black",
        zorder=6
    )

    ax2.set_xlabel(
        "Gain Variation (dB)"
    )

    ax2.set_ylabel(
        "Phase Variation (deg)"
    )

    ax2.set_title(
        "B. Allowable Combined Gain/Phase Variation"
    )

    ax2.grid(
        True,
        alpha=0.28
    )

    ax2.legend(
        fontsize=8,
        loc="best",
        framealpha=0.92
    )

    # --------------------------------------------------------
    # Research interpretation note inside the figure.
    # --------------------------------------------------------

    fig.suptitle(
        "Disk Margin Analysis: Frequency Dependence and Robust Gain/Phase Region",
        fontsize=13,
        fontweight="bold"
    )

    fig.tight_layout(
        rect=[0, 0, 1, 0.94]
    )

    display_figure(
        disk_tab,
        fig,
        "disk"
    )


# ============================================================
# CRITICAL DISTURBANCE / ROBUSTNESS BOUNDARY
# ============================================================

def calculate_critical_disturbance(disk):
    """
    Convert the formal Balanced Disk Margin into a clear
    critical gain/phase uncertainty boundary.

    This uses the same admissible gain/phase boundary formula
    documented in the python-control disk-margin example:

        f = [2 + alpha(1-skew)e^(j theta)] /
            [2 - alpha(1+skew)e^(j theta)]

    For the balanced case skew=0:

        alpha = Balanced Disk Margin

    The returned values describe:
      - alpha_critical: formal worst-case Disk Margin
      - gain_intercept_db: +/- gain variation at zero phase
      - phase_intercept_deg: +/- phase variation at zero gain
      - worst_frequency: frequency at which alpha is minimum

    IMPORTANT:
    These values define the robustness boundary.  They do NOT
    mean that every perturbation beyond the boundary is
    destabilizing.  Rather, the disk margin is exhausted at
    the boundary and stability is no longer guaranteed beyond it.
    """

    balanced = disk.get("balanced", {})

    alpha = float(
        balanced.get("dm", np.nan)
    )

    worst_frequency = float(
        balanced.get("worst_frequency", np.nan)
    )

    if (
        not np.isfinite(alpha)
        or alpha <= 0
    ):
        return {
            "alpha_critical": np.nan,
            "worst_frequency": worst_frequency,
            "gain_intercept_db": np.nan,
            "phase_intercept_deg": np.nan
        }

    # Balanced disk margin is bounded by the disk definition.
    # Guard the gain-intercept expression against a singular
    # denominator at alpha=2.
    if alpha < 2.0:
        gain_factor = (
            2.0 + alpha
        ) / (
            2.0 - alpha
        )

        gain_intercept_db = (
            20.0
            * np.log10(gain_factor)
        )

    else:
        gain_intercept_db = np.inf

    phase_intercept_deg = (
        2.0
        * np.rad2deg(
            np.arctan(alpha / 2.0)
        )
    )

    return {
        "alpha_critical": alpha,
        "worst_frequency": worst_frequency,
        "gain_intercept_db": gain_intercept_db,
        "phase_intercept_deg": phase_intercept_deg
    }


def plot_critical_disturbance(
    disk,
    omega
):
    """
    Display a clear research-oriented robustness boundary.

    Panel A:
        Balanced allowable gain/phase boundary at the formal
        worst-case Disk Margin.

    Panel B:
        Normalized disturbance level alpha/alpha_critical.
        The value 1.0 is the formal robustness boundary.
        Above 1.0, robustness is no longer guaranteed.

    This visualization is intentionally labelled as a
    robustness boundary, not as a claim that every point
    beyond the boundary destabilizes the system.
    """

    critical = calculate_critical_disturbance(
        disk
    )

    alpha_crit = critical[
        "alpha_critical"
    ]

    worst_frequency = critical[
        "worst_frequency"
    ]

    gain_db = critical[
        "gain_intercept_db"
    ]

    phase_deg = critical[
        "phase_intercept_deg"
    ]

    fig = plt.Figure(
        figsize=(12, 6.8),
        dpi=110
    )

    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    # --------------------------------------------------------
    # PANEL A: Balanced disk gain/phase boundary
    # --------------------------------------------------------
    #
    # Special case:
    # For alpha -> 2 (the maximum normalized balanced
    # disk-margin value), the boundary becomes a limiting
    # two-sided phase boundary at +/-90 deg while the
    # gain intercept tends to +/- infinity.  The previous
    # implementation incorrectly refused to draw this case.

    eps = 1e-9

    if (
        np.isfinite(alpha_crit)
        and alpha_crit > 0
        and alpha_crit < 2.0 - eps
    ):

        theta = np.linspace(
            0,
            2 * np.pi,
            2000
        )

        f = (
            2.0
            + alpha_crit
            * np.exp(1j * theta)
        ) / (
            2.0
            - alpha_crit
            * np.exp(1j * theta)
        )

        boundary_gain_db = (
            20.0
            * np.log10(
                np.abs(f)
            )
        )

        boundary_phase_deg = np.rad2deg(
            np.angle(f)
        )

        finite = (
            np.isfinite(boundary_gain_db)
            & np.isfinite(boundary_phase_deg)
        )

        x = boundary_gain_db[finite]
        y = boundary_phase_deg[finite]

        ax1.plot(
            x,
            y,
            linewidth=2.5,
            color="tab:blue",
            label="Balanced critical boundary"
        )

        ax1.fill(
            x,
            y,
            alpha=0.18,
            color="tab:blue",
            label="Within disk-margin boundary"
        )

        ax1.scatter(
            [gain_db, -gain_db],
            [0, 0],
            s=65,
            color="tab:orange",
            edgecolors="black",
            zorder=6,
            label="Critical gain-only intercept"
        )

        ax1.scatter(
            [0, 0],
            [phase_deg, -phase_deg],
            s=65,
            color="tab:green",
            edgecolors="black",
            zorder=6,
            label="Critical phase-only intercept"
        )

        finite_x = np.abs(x[np.isfinite(x)])

        if finite_x.size:
            xlim = max(
                10.0,
                min(
                    50.0,
                    float(np.max(finite_x)) * 1.10
                )
            )

            ax1.set_xlim(
                -xlim,
                xlim
            )

        ax1.set_ylim(
            -100,
            100
        )

        ax1.axhline(
            0,
            linewidth=0.8,
            linestyle="--"
        )

        ax1.axvline(
            0,
            linewidth=0.8,
            linestyle="--"
        )

        ax1.annotate(
            (
                f"Critical gain: ±{gain_db:.3f} dB\n"
                f"Critical phase: ±{phase_deg:.3f}°"
            ),
            xy=(0, 0),
            xytext=(12, 18),
            textcoords="offset points",
            fontsize=9,
            bbox=dict(
                boxstyle="round,pad=0.35",
                alpha=0.90
            ),
            arrowprops=dict(
                arrowstyle="->",
                linewidth=1.0
            )
        )

    elif (
        np.isfinite(alpha_crit)
        and alpha_crit >= 2.0 - eps
    ):

        # Exact limiting balanced-disk case:
        # alpha_crit = 2, gain intercept is infinite and
        # phase-only boundary is +/-90 degrees.
        xlim = 40.0

        x_boundary = np.linspace(
            -xlim,
            xlim,
            800
        )

        ax1.plot(
            x_boundary,
            np.full_like(
                x_boundary,
                90.0
            ),
            linewidth=2.5,
            color="tab:blue",
            label="Balanced limiting boundary: +90°"
        )

        ax1.plot(
            x_boundary,
            np.full_like(
                x_boundary,
                -90.0
            ),
            linewidth=2.5,
            color="tab:blue",
            label="Balanced limiting boundary: −90°"
        )

        ax1.axhline(
            0,
            linewidth=0.8,
            linestyle="--"
        )

        ax1.axvline(
            0,
            linewidth=0.8,
            linestyle="--"
        )

        ax1.fill_between(
            x_boundary,
            -90.0,
            90.0,
            alpha=0.12,
            color="tab:blue",
            label="Finite gain/phase region"
        )

        ax1.set_xlim(
            -xlim,
            xlim
        )

        ax1.set_ylim(
            -100,
            100
        )

        ax1.annotate(
            (
                "αcrit = 2 (upper balanced limit)\n"
                "Critical gain-only variation: ±∞ dB\n"
                "Critical phase-only variation: ±90°\n"
                "Boundary shown in its limiting form"
            ),
            xy=(0, 90),
            xytext=(10, 18),
            textcoords="offset points",
            fontsize=9,
            bbox=dict(
                boxstyle="round,pad=0.4",
                alpha=0.92
            ),
            arrowprops=dict(
                arrowstyle="->",
                linewidth=1.0
            )
        )

    else:

        ax1.text(
            0.5,
            0.5,
            "Balanced Disk Margin boundary\n"
            "is unavailable for this result.",
            ha="center",
            va="center",
            transform=ax1.transAxes
        )


    ax1.set_xlabel(
        "Gain Variation (dB)"
    )

    ax1.set_ylabel(
        "Phase Variation (deg)"
    )

    ax1.set_title(
        "A. Critical Gain–Phase Disturbance Boundary"
    )

    ax1.grid(
        True,
        alpha=0.3
    )

    ax1.legend(
        fontsize=8,
        loc="best",
        framealpha=0.92
    )

    # --------------------------------------------------------
    # PANEL B: Robustness budget
    # --------------------------------------------------------

    q = np.linspace(
        0,
        1.40,
        400
    )

    ax2.plot(
        q,
        q,
        linewidth=2.5,
        color="tab:blue",
        label="Normalized disturbance level"
    )

    ax2.axvspan(
        0,
        1.0,
        alpha=0.18,
        color="tab:green",
        label="Within robustness boundary"
    )

    ax2.axvspan(
        1.0,
        1.40,
        alpha=0.15,
        color="tab:red",
        label="Beyond guaranteed robustness"
    )

    ax2.axvline(
        1.0,
        linewidth=2,
        linestyle="--",
        color="tab:red",
        label="Critical boundary: α/αcrit = 1"
    )

    ax2.scatter(
        [1.0],
        [1.0],
        s=90,
        color="red",
        edgecolors="black",
        zorder=7
    )

    ax2.annotate(
        (
            f"αcrit = {alpha_crit:.5f}\n"
            f"ωworst = {worst_frequency:.5g} rad/s"
        ),
        xy=(1.0, 1.0),
        xytext=(12, 18),
        textcoords="offset points",
        fontsize=9,
        bbox=dict(
            boxstyle="round,pad=0.35",
            alpha=0.90
        ),
        arrowprops=dict(
            arrowstyle="->",
            linewidth=1.0
        )
    )

    ax2.set_xlim(
        0,
        1.40
    )

    ax2.set_ylim(
        0,
        1.40
    )

    ax2.set_xlabel(
        "Normalized disturbance α / αcrit"
    )

    ax2.set_ylabel(
        "Normalized robustness level"
    )

    ax2.set_title(
        "B. Robustness Budget and Critical Disturbance"
    )

    ax2.grid(
        True,
        alpha=0.3
    )

    ax2.legend(
        fontsize=8,
        loc="best",
        framealpha=0.92
    )

    fig.suptitle(
        "Critical Disturbance Analysis from Balanced Disk Margin",
        fontsize=13,
        fontweight="bold"
    )

    fig.tight_layout(
        rect=[0, 0, 1, 0.94]
    )

    display_figure(
        critical_tab,
        fig,
        "critical_disturbance"
    )



# ============================================================
# POLE ZERO
# ============================================================

def plot_poles(
    system
):

    poles = np.asarray(
        ct.poles(system)
    )


    zeros = np.asarray(
        ct.zeros(system)
    )


    fig = plt.Figure(
        figsize=(8, 7),
        dpi=100
    )


    ax = fig.add_subplot(
        111
    )


    if len(poles):

        ax.scatter(
            poles.real,
            poles.imag,
            marker="x",
            s=130,
            linewidths=3,
            label="Poles"
        )


    if len(zeros):

        ax.scatter(
            zeros.real,
            zeros.imag,
            marker="o",
            s=100,
            facecolors="none",
            linewidths=2,
            label="Zeros"
        )


    ax.axvline(
        0,
        linestyle="--",
        linewidth=1
    )


    ax.axhline(
        0,
        linewidth=1
    )


    ax.set_xlabel(
        "Real Axis"
    )

    ax.set_ylabel(
        "Imaginary Axis"
    )


    ax.set_title(
        "Closed-Loop Pole-Zero Map"
    )


    ax.grid(
        True,
        alpha=0.3
    )


    ax.legend()


    fig.tight_layout()


    display_figure(
        pole_tab,
        fig,
        "poles"
    )


# ============================================================
# STEP RESPONSE
# ============================================================

def calculate_step(
    system
):

    time = make_time_vector(
        system
    )


    t, y = ct.step_response(
        system,
        T=time
    )


    try:

        info = ct.step_info(
            system
        )

    except:

        info = {}


    return (
        t,
        np.squeeze(y),
        info
    )


# ------------------------------------------------------------

def plot_step(
    system
):

    try:

        t, y, info = calculate_step(
            system
        )


        fig = plt.Figure(
            figsize=(9, 6),
            dpi=100
        )


        ax = fig.add_subplot(
            111
        )


        ax.plot(
            t,
            y,
            linewidth=2
        )


        ax.axhline(
            1,
            linestyle="--",
            linewidth=1
        )


        ax.set_xlabel(
            "Time (s)"
        )


        ax.set_ylabel(
            "Output"
        )


        ax.set_title(
            "Closed-Loop Step Response"
        )


        ax.grid(
            True,
            alpha=0.3
        )


        fig.tight_layout()


        display_figure(
            step_tab,
            fig,
            "step"
        )


        return info


    except Exception as error:

        clear_frame(
            step_tab
        )


        ctk.CTkLabel(
            step_tab,
            text=(
                "Step Response unavailable.\n\n"
                + str(error)
            ),
            text_color=RED,
            font=ctk.CTkFont(
                size=14
            )
        ).pack(
            expand=True
        )


        return {}


# ============================================================
# UNCERTAINTY MAP
# ============================================================

def plot_uncertainty(
    disk
):

    clear_frame(
        uncertainty_tab
    )


    fig = plt.Figure(
        figsize=(9, 7),
        dpi=100
    )


    ax = fig.add_subplot(
        111
    )


    # --------------------------------------------------------
    # User uncertainty
    # --------------------------------------------------------

    try:

        gain_percent = float(
            gain_uncertainty.get()
        )

        phase = float(
            phase_uncertainty.get()
        )


        if 0 <= gain_percent < 100:

            gain_pos = (
                20 *
                np.log10(
                    1 +
                    gain_percent /
                    100
                )
            )


            gain_neg = (
                20 *
                np.log10(
                    1 -
                    gain_percent /
                    100
                )
            )


            x = [
                gain_neg,
                gain_pos,
                gain_pos,
                gain_neg,
                gain_neg
            ]


            y = [
                -phase,
                -phase,
                phase,
                phase,
                -phase
            ]


            ax.plot(
                x,
                y,
                linestyle="--",
                linewidth=2,
                label="User uncertainty"
            )


            ax.fill(
                x,
                y,
                alpha=0.10
            )


    except:

        pass


    # --------------------------------------------------------
    # Reference axes
    # --------------------------------------------------------

    ax.axhline(
        0,
        linewidth=1
    )

    ax.axvline(
        0,
        linewidth=1
    )


    ax.set_xlabel(
        "Gain Variation (dB)"
    )


    ax.set_ylabel(
        "Phase Variation (deg)"
    )


    ax.set_title(
        "Gain–Phase Uncertainty Map"
    )


    ax.grid(
        True,
        alpha=0.3
    )


    ax.legend()


    fig.tight_layout()


    display_figure(
        uncertainty_tab,
        fig,
        "uncertainty"
    )


# ============================================================
# COMPARISON
# ============================================================

def update_comparison():

    if current_result is None:
        return


    r = current_result


    comparison_box.delete(
        "1.0",
        "end"
    )


    text = ""


    text += (
        "CLASSICAL vs DISK MARGIN\n"
    )

    text += (
        "=" * 90
        + "\n\n"
    )


    text += (
        "SYSTEM\n"
    )

    text += (
        "-" * 90
        + "\n"
    )

    text += (
        f"{r['equation']}\n\n"
    )


    text += (
        "NOMINAL STABILITY\n"
    )

    text += (
        "-" * 90
        + "\n"
    )

    text += (
        f"Closed-loop stability : "
        f"{r['stability']}\n"
    )

    text += (
        f"Maximum real pole     : "
        f"{fmt(r['max_real_pole'], 6)}\n\n"
    )


    text += (
        "CLASSICAL ANALYSIS\n"
    )

    text += (
        "-" * 90
        + "\n"
    )

    text += (
        f"Gain Margin      : "
        f"{fmt(r['gm_db'], 5)} dB\n"
    )

    text += (
        f"Phase Margin     : "
        f"{fmt(r['pm'], 5)} deg\n"
    )

    text += (
        f"Stability Margin : "
        f"{fmt(r['sm'], 7)}\n\n"
    )


    text += (
        "DISK MARGIN\n"
    )

    text += (
        "-" * 90
        + "\n"
    )

    text += (
        f"S-based          : "
        f"{fmt(r['disk']['s']['dm'], 7)}\n"
    )

    text += (
        f"Balanced         : "
        f"{fmt(r['disk']['balanced']['dm'], 7)}\n"
    )

    text += (
        f"T-based          : "
        f"{fmt(r['disk']['t']['dm'], 7)}\n"
    )

    text += (
        f"Worst frequency  : "
        f"{fmt(r['disk']['balanced']['worst_frequency'], 6)} rad/s\n\n"
    )


    text += (
        "TIME RESPONSE\n"
    )

    text += (
        "-" * 90
        + "\n"
    )


    info = r["step_info"]


    text += (
        f"Rise Time       : "
        f"{fmt(info.get('RiseTime'), 5)} s\n"
    )

    text += (
        f"Settling Time   : "
        f"{fmt(info.get('SettlingTime'), 5)} s\n"
    )

    text += (
        f"Overshoot       : "
        f"{fmt(info.get('Overshoot'), 5)} %\n"
    )

    text += (
        f"Peak            : "
        f"{fmt(info.get('Peak'), 5)}\n"
    )

    text += (
        f"Peak Time       : "
        f"{fmt(info.get('PeakTime'), 5)} s\n\n"
    )


    text += (
        "INTERPRETATION\n"
    )

    text += (
        "-" * 90
        + "\n"
    )

    text += (
        "Classical gain and phase margins characterize "
        "conventional frequency-domain stability margins. "
        "Disk Margin provides a complementary robustness "
        "measure for simultaneous gain and phase variations.\n\n"
    )

    text += (
        "The nominal stability decision in this software "
        "is based on closed-loop pole locations and the "
        "Routh-Hurwitz test.\n\n"
    )

    text += (
        "A low Disk Margin must not automatically be "
        "reported as nominal instability."
    )


    comparison_box.insert(
        "1.0",
        text
    )


# ============================================================
# ROBUSTNESS
# ============================================================

def update_robustness():

    if current_result is None:
        return


    r = current_result


    try:

        gain_percent = float(
            gain_uncertainty.get()
        )

        phase_deg = float(
            phase_uncertainty.get()
        )

    except:

        return


    dm = r[
        "disk"
    ][
        "balanced"
    ][
        "dm"
    ]


    # Engineering screening index
    gain_ratio = (
        gain_percent /
        100
    )


    phase_ratio = (
        np.deg2rad(
            phase_deg
        )
    )


    combined = np.sqrt(
        gain_ratio**2
        +
        phase_ratio**2
    )


    if np.isfinite(dm) and dm > 0:

        ratio = (
            combined /
            dm
        )

    else:

        ratio = np.nan


    if not np.isfinite(dm):

        status = "UNDETERMINED"
        color = YELLOW

    elif ratio < 0.70:

        status = "PASS"
        color = GREEN

    elif ratio <= 1.0:

        status = "WARNING"
        color = YELLOW

    else:

        status = "CRITICAL"
        color = RED


    robust_card.configure(
        text=status,
        text_color=color
    )


    robustness_box.delete(
        "1.0",
        "end"
    )


    text = ""


    text += (
        "ROBUSTNESS ASSESSMENT\n"
    )

    text += (
        "=" * 90
        + "\n\n"
    )


    text += (
        f"STATUS: {status}\n\n"
    )


    text += (
        "USER UNCERTAINTY\n"
    )

    text += (
        "-" * 90
        + "\n"
    )

    text += (
        f"Gain uncertainty  : ±{gain_percent:.3f}%\n"
    )

    text += (
        f"Phase uncertainty : ±{phase_deg:.3f}°\n\n"
    )


    text += (
        "DISK MARGIN\n"
    )

    text += (
        "-" * 90
        + "\n"
    )

    text += (
        f"Balanced Disk Margin : "
        f"{fmt(dm, 8)}\n"
    )

    text += (
        f"Worst-case frequency : "
        f"{fmt(r['disk']['balanced']['worst_frequency'], 6)} rad/s\n\n"
    )


    text += (
        "SCREENING INDICATOR\n"
    )

    text += (
        "-" * 90
        + "\n"
    )

    text += (
        f"Combined uncertainty index : "
        f"{combined:.6f}\n"
    )

    text += (
        f"Demand / DM ratio          : "
        f"{fmt(ratio, 6)}\n\n"
    )


    text += (
        "NOMINAL STABILITY\n"
    )

    text += (
        "-" * 90
        + "\n"
    )

    text += (
        f"Status             : "
        f"{r['stability']}\n"
    )

    text += (
        f"Maximum real pole : "
        f"{fmt(r['max_real_pole'], 6)}\n\n"
    )


    text += (
        "ENGINEERING INTERPRETATION\n"
    )

    text += (
        "-" * 90
        + "\n"
    )


    if status == "PASS":

        text += (
            "The specified uncertainty is relatively "
            "small compared with the computed Disk Margin."
        )

    elif status == "WARNING":

        text += (
            "The specified uncertainty approaches the "
            "robustness boundary indicated by the screening "
            "indicator."
        )

    elif status == "CRITICAL":

        text += (
            "The specified uncertainty exceeds the "
            "screening level associated with the computed "
            "Disk Margin."
        )

    else:

        text += (
            "A definitive robustness classification could "
            "not be obtained."
        )


    text += (
        "\n\nIMPORTANT:\n"
        "PASS/WARNING/CRITICAL is an engineering "
        "screening indicator implemented by this "
        "application. It is not the mathematical "
        "definition of Disk Margin."
    )


    robustness_box.insert(
        "1.0",
        text
    )


# ============================================================
# ROUTH DISPLAY
# ============================================================

def update_routh(
    denominator
):

    try:

        table, first, changes, stable = (
            analyze_routh(
                denominator
            )
        )


        routh_box.delete(
            "1.0",
            "end"
        )


        text = ""


        text += (
            "ROUTH-HURWITZ ANALYSIS\n"
        )

        text += (
            "=" * 90
            + "\n\n"
        )


        text += (
            "Characteristic polynomial:\n"
        )

        text += (
            polynomial_to_string(
                denominator
            )
            +
            "\n\n"
        )


        text += (
            "ROUTH TABLE\n"
        )

        text += (
            "-" * 90
            + "\n"
        )


        n = len(
            denominator
        ) - 1


        for i, row in enumerate(
            table
        ):

            power = n - i


            text += (
                f"s^{power:<3} | "
            )


            for value in row:

                text += (
                    f"{value:>14.6g} "
                )


            text += "\n"


        text += "\n"


        text += (
            "FIRST COLUMN\n"
        )

        text += (
            "-" * 90
            + "\n"
        )


        for value in first:

            text += (
                f"{value:.8g}\n"
            )


        text += "\n"


        text += (
            f"Sign changes : {changes}\n\n"
        )


        if stable:

            text += (
                "Routh-Hurwitz conclusion: "
                "STABLE\n"
            )

        else:

            text += (
                "Routh-Hurwitz conclusion: "
                "UNSTABLE or requires further "
                "special-case analysis\n"
            )


        routh_box.insert(
            "1.0",
            text
        )


    except Exception as error:

        routh_box.delete(
            "1.0",
            "end"
        )

        routh_box.insert(
            "1.0",
            "Routh-Hurwitz calculation failed:\n\n"
            + str(error)
        )


# ============================================================
# OVERVIEW
# ============================================================

def update_overview():

    if current_result is None:
        return


    r = current_result


    overview_box.delete(
        "1.0",
        "end"
    )


    text = ""


    text += (
        "SYSTEM ANALYSIS OVERVIEW\n"
    )

    text += (
        "=" * 90
        + "\n\n"
    )


    text += (
        f"{r['equation']}\n\n"
    )


    text += (
        f"Closed-loop:\n"
        f"{r['closed_loop_string']}\n\n"
    )


    text += (
        "NOMINAL STABILITY\n"
    )

    text += (
        "-" * 90
        + "\n"
    )

    text += (
        f"Status            : "
        f"{r['stability']}\n"
    )

    text += (
        f"Maximum real pole : "
        f"{fmt(r['max_real_pole'], 6)}\n\n"
    )


    text += (
        "CLASSICAL MARGINS\n"
    )

    text += (
        "-" * 90
        + "\n"
    )

    text += (
        f"Gain Margin  : "
        f"{fmt(r['gm_db'], 5)} dB\n"
    )

    text += (
        f"Phase Margin : "
        f"{fmt(r['pm'], 5)} deg\n"
    )

    text += (
        f"Stability Margin : "
        f"{fmt(r['sm'], 6)}\n\n"
    )


    text += (
        "DISK MARGIN\n"
    )

    text += (
        "-" * 90
        + "\n"
    )

    text += (
        f"S-based   : "
        f"{fmt(r['disk']['s']['dm'], 6)}\n"
    )

    text += (
        f"Balanced  : "
        f"{fmt(r['disk']['balanced']['dm'], 6)}\n"
    )

    text += (
        f"T-based   : "
        f"{fmt(r['disk']['t']['dm'], 6)}\n\n"
    )


    info = r["step_info"]


    text += (
        "TIME RESPONSE\n"
    )

    text += (
        "-" * 90
        + "\n"
    )

    text += (
        f"Rise Time     : "
        f"{fmt(info.get('RiseTime'), 5)} s\n"
    )

    text += (
        f"Settling Time : "
        f"{fmt(info.get('SettlingTime'), 5)} s\n"
    )

    text += (
        f"Overshoot     : "
        f"{fmt(info.get('Overshoot'), 5)} %\n"
    )

    text += (
        f"Peak          : "
        f"{fmt(info.get('Peak'), 5)}\n"
    )

    text += (
        f"Peak Time     : "
        f"{fmt(info.get('PeakTime'), 5)} s\n"
    )


    overview_box.insert(
        "1.0",
        text
    )


# ============================================================
# REPORT
# ============================================================

def generate_report():

    if current_result is None:
        return


    r = current_result


    report_box.delete(
        "1.0",
        "end"
    )


    text = ""


    text += (
        "ROBUST CONTROL ANALYZER V4\n"
    )

    text += (
        "=" * 90
        + "\n\n"
    )


    text += (
        "1. SYSTEM DEFINITION\n"
    )

    text += (
        "-" * 90
        + "\n"
    )

    text += (
        r["equation"]
        +
        "\n"
    )

    text += (
        f"Feedback: {r['feedback']}\n\n"
    )


    text += (
        "2. NOMINAL STABILITY\n"
    )

    text += (
        "-" * 90
        + "\n"
    )

    text += (
        f"Status: {r['stability']}\n"
    )

    text += (
        f"Maximum real pole: "
        f"{fmt(r['max_real_pole'], 8)}\n\n"
    )


    text += (
        "3. CLASSICAL FREQUENCY-DOMAIN ANALYSIS\n"
    )

    text += (
        "-" * 90
        + "\n"
    )

    text += (
        f"Gain Margin      : "
        f"{fmt(r['gm_db'], 6)} dB\n"
    )

    text += (
        f"Phase Margin     : "
        f"{fmt(r['pm'], 6)} deg\n"
    )

    text += (
        f"Stability Margin : "
        f"{fmt(r['sm'], 8)}\n"
    )

    text += (
        f"Gain crossover   : "
        f"{fmt(r['wcp'], 6)} rad/s\n"
    )

    text += (
        f"Phase crossover  : "
        f"{fmt(r['wcg'], 6)} rad/s\n\n"
    )


    text += (
        "4. DISK MARGIN ANALYSIS\n"
    )

    text += (
        "-" * 90
        + "\n"
    )

    text += (
        f"S-based DM  : "
        f"{fmt(r['disk']['s']['dm'], 8)}\n"
    )

    text += (
        f"Balanced DM : "
        f"{fmt(r['disk']['balanced']['dm'], 8)}\n"
    )

    text += (
        f"T-based DM  : "
        f"{fmt(r['disk']['t']['dm'], 8)}\n"
    )

    text += (
        f"Worst-case frequency : "
        f"{fmt(r['disk']['balanced']['worst_frequency'], 6)} rad/s\n\n"
    )


    text += (
        "5. DISK-BASED MARGINS\n"
    )

    text += (
        "-" * 90
        + "\n"
    )

    text += (
        f"Balanced disk GM : "
        f"{fmt(r['disk']['balanced']['dgm'], 6)} dB\n"
    )

    text += (
        f"Balanced disk PM : "
        f"{fmt(r['disk']['balanced']['dpm'], 6)} deg\n\n"
    )


    text += (
        "6. TIME-DOMAIN RESPONSE\n"
    )

    text += (
        "-" * 90
        + "\n"
    )


    info = r["step_info"]


    for key, label, unit in [

        ("RiseTime", "Rise Time", "s"),

        ("SettlingTime", "Settling Time", "s"),

        ("Overshoot", "Overshoot", "%"),

        ("Peak", "Peak", ""),

        ("PeakTime", "Peak Time", "s")

    ]:

        value = fmt(
            info.get(key),
            6
        )


        text += (
            f"{label:<20}: "
            f"{value} {unit}\n"
        )


    text += "\n"


    text += (
        "7. ENGINEERING INTERPRETATION\n"
    )

    text += (
        "-" * 90
        + "\n"
    )


    text += (
        "The nominal stability assessment is based on "
        "the closed-loop pole locations and the "
        "Routh-Hurwitz analysis.\n\n"
    )


    text += (
        "Classical gain and phase margins characterize "
        "conventional frequency-domain stability margins.\n\n"
    )


    text += (
        "Disk Margin provides a complementary robustness "
        "measure associated with simultaneous gain and "
        "phase variations.\n\n"
    )


    text += (
        "Therefore, a low Disk Margin should not be "
        "automatically interpreted as nominal instability. "
        "Nominal stability and robustness are reported "
        "as separate engineering properties."
    )


    report_box.insert(
        "1.0",
        text
    )


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze():

    global current_result


    try:

        status_label.configure(
            text="ANALYZING SYSTEM...",
            text_color=YELLOW
        )


        numerator = parse_coefficients(
            num_entry.get()
        )


        denominator = parse_coefficients(
            den_entry.get()
        )


        omega = frequency_vector()


        # ----------------------------------------------------
        # Plant
        # ----------------------------------------------------

        plant = ct.tf(
            numerator,
            denominator
        )


        # ----------------------------------------------------
        # Closed loop
        # ----------------------------------------------------

        if (
            feedback.get()
            ==
            "Negative Feedback"
        ):

            closed_loop = ct.feedback(
                plant,
                1,
                sign=-1
            )

        else:

            closed_loop = ct.feedback(
                plant,
                1,
                sign=1
            )


        # ----------------------------------------------------
        # Classical margins
        # ----------------------------------------------------

        gm, pm, wcg, wcp = ct.margin(
            plant
        )


        if (
            np.isfinite(gm)
            and
            gm > 0
        ):

            gm_db = (
                20 *
                np.log10(gm)
            )

        else:

            gm_db = np.inf


        # ----------------------------------------------------
        # Stability margin
        # ----------------------------------------------------

        try:

            sm_data = ct.stability_margins(
                plant
            )

            sm = sm_data[2]

        except:

            sm = np.nan


        # ----------------------------------------------------
        # Poles
        # ----------------------------------------------------

        poles = np.asarray(
            ct.poles(
                closed_loop
            )
        )


        zeros = np.asarray(
            ct.zeros(
                closed_loop
            )
        )


        if len(poles):

            max_real_pole = float(
                np.max(
                    np.real(
                        poles
                    )
                )
            )

        else:

            max_real_pole = np.nan


        # ----------------------------------------------------
        # Stability
        # ----------------------------------------------------

        if (
            np.isfinite(
                max_real_pole
            )
            and
            max_real_pole < -1e-9
        ):

            stability = "STABLE"

        elif (
            np.isfinite(
                max_real_pole
            )
            and
            max_real_pole > 1e-9
        ):

            stability = "UNSTABLE"

        else:

            stability = "MARGINALLY STABLE"


        # ----------------------------------------------------
        # Disk Margin
        # ----------------------------------------------------

        disk = calculate_disk(
            plant,
            omega
        )


        # Critical disturbance is derived from the Balanced
        # Disk Margin BEFORE current_result is constructed.
        critical_disturbance = (
            calculate_critical_disturbance(
                disk
            )
        )


        # ----------------------------------------------------
        # Step Response
        # ----------------------------------------------------

        try:

            step_info = plot_step(
                closed_loop
            )

            if step_info is None:
                step_info = {}

        except:

            step_info = {}


        # ----------------------------------------------------
        # Routh
        # ----------------------------------------------------

        update_routh(
            denominator
        )


        # ----------------------------------------------------
        # Store
        # ----------------------------------------------------

        equation = transfer_function_string(
            numerator,
            denominator
        )


        closed_loop_string = str(
            closed_loop
        )


        current_result = {

            "plant":
                plant,

            "closed_loop":
                closed_loop,

            "numerator":
                numerator,

            "denominator":
                denominator,

            "feedback":
                feedback.get(),

            "equation":
                equation,

            "closed_loop_string":
                closed_loop_string,

            "gm_db":
                gm_db,

            "pm":
                pm,

            "sm":
                sm,

            "wcg":
                wcg,

            "wcp":
                wcp,

            "poles":
                poles,

            "zeros":
                zeros,

            "max_real_pole":
                max_real_pole,

            "stability":
                stability,

            "disk":
                disk,

            "critical_disturbance":
                critical_disturbance,

            "step_info":
                step_info
        }


        # ----------------------------------------------------
        # Dashboard
        # ----------------------------------------------------

        gm_card.configure(
            text=(
                fmt(gm_db, 3)
                +
                " dB"
            )
        )


        pm_card.configure(
            text=(
                fmt(pm, 3)
                +
                "°"
            )
        )


        dm_card.configure(
            text=fmt(
                disk[
                    "balanced"
                ][
                    "dm"
                ],
                5
            )
        )


        if stability == "STABLE":

            stability_card.configure(
                text=stability,
                text_color=GREEN
            )

        elif stability == "UNSTABLE":

            stability_card.configure(
                text=stability,
                text_color=RED
            )

        else:

            stability_card.configure(
                text=stability,
                text_color=YELLOW
            )


        equation_label.configure(
            text=equation
        )


        closed_loop_label.configure(
            text=(
                "Closed-loop: "
                +
                closed_loop_string
            )
        )


        # ----------------------------------------------------
        # Plots
        # ----------------------------------------------------

        plot_bode(
            plant,
            omega
        )


        plot_nyquist(
            plant,
            omega
        )


        plot_disk(
            disk,
            omega
        )


        plot_critical_disturbance(
            disk,
            omega
        )


        plot_poles(
            closed_loop
        )


        plot_uncertainty(
            disk
        )


        # ----------------------------------------------------
        # Text pages
        # ----------------------------------------------------

        update_overview()

        update_comparison()

        update_robustness()

        generate_report()


        # Add the critical-disturbance interpretation to the
        # report after the standard report has been generated.
        cd = current_result.get(
            "critical_disturbance",
            {}
        )

        report_box.insert(
            "end",
            (
                "\n\n"
                "CRITICAL DISTURBANCE / ROBUSTNESS BOUNDARY\n"
                "------------------------------------------\n"
                f"Balanced Disk Margin (alpha_crit): "
                f"{fmt(cd.get('alpha_critical', np.nan), 6)}\n"
                f"Worst-case frequency: "
                f"{fmt(cd.get('worst_frequency', np.nan), 6)} rad/s\n"
                f"Critical gain-only intercept: "
                f"+/- {fmt(cd.get('gain_intercept_db', np.nan), 4)} dB\n"
                f"Critical phase-only intercept: "
                f"+/- {fmt(cd.get('phase_intercept_deg', np.nan), 4)} deg\n\n"
                "Interpretation: the critical disk-margin boundary "
                "represents the point at which the guaranteed robust-"
                "stability margin is exhausted. Perturbations beyond "
                "this boundary are outside the guaranteed robustness "
                "region and can cause loss of stability; they do not "
                "imply that every perturbation beyond the boundary "
                "will destabilize the system.\n"
            )
        )


        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        status_label.configure(
            text=(
                "ANALYSIS COMPLETE — "
                "Results are available in all tabs."
            ),
            text_color=GREEN
        )


        tabs.set(
            "Overview"
        )


    except Exception as error:

        status_label.configure(
            text="ANALYSIS FAILED",
            text_color=RED
        )


        messagebox.showerror(
            "Analysis Error",
            (
                "The system could not be analyzed.\n\n"
                + str(error)
            )
        )


# ============================================================
# COMPARISON BUTTON
# ============================================================

def show_comparison():

    if current_result is None:

        messagebox.showwarning(
            "No Analysis",
            "Analyze a system first."
        )

        return


    update_comparison()

    tabs.set(
        "Comparison"
    )


# ============================================================
# ROBUSTNESS BUTTON
# ============================================================

def show_robustness():

    if current_result is None:

        messagebox.showwarning(
            "No Analysis",
            "Analyze a system first."
        )

        return


    update_robustness()

    tabs.set(
        "Robustness"
    )



# ============================================================
# CRITICAL DISTURBANCE BUTTON
# ============================================================

def show_critical_disturbance():

    if current_result is None:

        messagebox.showwarning(
            "No Analysis",
            "Analyze a system first."
        )

        return

    disk = current_result.get(
        "disk"
    )

    if not disk:

        messagebox.showwarning(
            "No Disk Margin",
            "Disk Margin results are not available."
        )

        return

    omega = frequency_vector()

    plot_critical_disturbance(
        disk,
        omega
    )

    tabs.set(
        "Critical Disturbance"
    )



# ============================================================
# EXPORT
# ============================================================

def export_report():

    if current_result is None:

        messagebox.showwarning(
            "No Analysis",
            "Analyze a system first."
        )

        return


    filename = filedialog.asksaveasfilename(

        title="Export Analysis Report",

        defaultextension=".txt",

        filetypes=[
            (
                "Text file",
                "*.txt"
            )
        ]
    )


    if not filename:
        return


    try:

        text = report_box.get(
            "1.0",
            "end"
        )


        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                text
            )


        messagebox.showinfo(
            "Export",
            "Report exported successfully."
        )


    except Exception as error:

        messagebox.showerror(
            "Export Error",
            str(error)
        )


# ============================================================
# EXPORT FIGURES
# ============================================================

def export_figures():

    if current_result is None:
        messagebox.showwarning(
            "No Analysis",
            "Analyze a system first."
        )
        return

    if not current_figures:
        messagebox.showwarning(
            "No Figures",
            "No analysis figures are available to export."
        )
        return

    folder = filedialog.askdirectory(
        title="Select Folder for Research Figures"
    )

    if not folder:
        return

    try:
        from pathlib import Path

        base_folder = Path(folder)

        export_folder = (
            base_folder
            / "Robust_Control_Analyzer_Figures"
        )

        export_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        # Complete list of figures generated by the current V4.
        figure_names = {
            "bode": "Figure_01_Bode",
            "nyquist": "Figure_02_Nyquist",
            "disk": "Figure_03_Disk_Margin",
            "critical_disturbance": "Figure_04_Critical_Disturbance",
            "poles": "Figure_05_Pole_Zero_Map",
            "step": "Figure_06_Step_Response",
            "uncertainty": "Figure_07_Gain_Phase_Uncertainty"
        }

        exported = []
        missing = []

        # Export all expected V4 figures.
        for key, stem in figure_names.items():

            fig = current_figures.get(key)

            if fig is None:
                missing.append(key)
                continue

            png_path = export_folder / f"{stem}.png"
            pdf_path = export_folder / f"{stem}.pdf"
            svg_path = export_folder / f"{stem}.svg"

            fig.savefig(
                png_path,
                dpi=300,
                bbox_inches="tight",
                facecolor="white"
            )

            fig.savefig(
                pdf_path,
                bbox_inches="tight",
                facecolor="white"
            )

            fig.savefig(
                svg_path,
                bbox_inches="tight",
                facecolor="white"
            )

            exported.append(key)

        # Safety net: automatically export any additional figure
        # that may be added to V4 in the future.
        for key, fig in current_figures.items():

            if key in figure_names or fig is None:
                continue

            safe_key = re.sub(
                r"[^A-Za-z0-9_-]+",
                "_",
                str(key)
            )

            stem = f"Additional_{safe_key}"

            fig.savefig(
                export_folder / f"{stem}.png",
                dpi=300,
                bbox_inches="tight",
                facecolor="white"
            )

            fig.savefig(
                export_folder / f"{stem}.pdf",
                bbox_inches="tight",
                facecolor="white"
            )

            fig.savefig(
                export_folder / f"{stem}.svg",
                bbox_inches="tight",
                facecolor="white"
            )

            exported.append(key)

        # Create an audit manifest so you can verify exactly what
        # was exported for each system used in the paper.
        manifest = (
            export_folder
            / "Exported_Figures_Manifest.txt"
        )

        with open(
            manifest,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                "ROBUST CONTROL ANALYZER V4\n"
            )

            file.write(
                "COMPLETE RESEARCH FIGURE EXPORT\n"
            )

            file.write(
                "=" * 72
                + "\n\n"
            )

            file.write(
                "System equation:\n"
                + str(
                    current_result.get(
                        "equation",
                        "N/A"
                    )
                )
                + "\n\n"
            )

            file.write(
                "Feedback:\n"
                + str(
                    current_result.get(
                        "feedback",
                        "N/A"
                    )
                )
                + "\n\n"
            )

            file.write(
                "Formats:\n"
                "PNG: 300 dpi\n"
                "PDF: vector\n"
                "SVG: vector/editable\n\n"
            )

            file.write(
                "Expected figures:\n"
            )

            for key in figure_names:
                status = (
                    "EXPORTED"
                    if key in exported
                    else "MISSING"
                )

                file.write(
                    f"- {key}: {status}\n"
                )

            file.write(
                "\nAll figure keys available at export time:\n"
            )

            for key in current_figures:
                file.write(
                    f"- {key}\n"
                )

        if missing:

            messagebox.showwarning(
                "Figures Exported with Warning",
                (
                    f"Exported {len(exported)} figure(s).\n\n"
                    f"Missing: {', '.join(missing)}\n\n"
                    f"Folder:\n{export_folder}\n\n"
                    "See Exported_Figures_Manifest.txt."
                )
            )

        else:

            messagebox.showinfo(
                "All Figures Exported",
                (
                    f"Successfully exported ALL "
                    f"{len(figure_names)} V4 figures.\n\n"
                    "Each figure was saved as:\n"
                    "• PNG (300 dpi)\n"
                    "• PDF (vector)\n"
                    "• SVG (vector)\n\n"
                    f"Folder:\n{export_folder}"
                )
            )

    except Exception as error:

        messagebox.showerror(
            "Figure Export Error",
            str(error)
        )


# ============================================================
# RESET
# ============================================================

def reset():

    global current_result, current_figures


    current_result = None
    current_figures = {}


    num_entry.delete(
        0,
        "end"
    )


    den_entry.delete(
        0,
        "end"
    )


    num_entry.insert(
        0,
        "1"
    )


    den_entry.insert(
        0,
        "1, 2, 5"
    )


    gm_card.configure(
        text="—"
    )


    pm_card.configure(
        text="—"
    )


    dm_card.configure(
        text="—"
    )


    stability_card.configure(
        text="—",
        text_color=WHITE
    )


    robust_card.configure(
        text="—",
        text_color=WHITE
    )


    equation_label.configure(
        text="G(s) = —"
    )


    closed_loop_label.configure(
        text="Closed-loop: —"
    )


    status_label.configure(
        text="READY — Enter a system and press ANALYZE SYSTEM",
        text_color=GRAY
    )


    overview_box.delete(
        "1.0",
        "end"
    )


    comparison_box.delete(
        "1.0",
        "end"
    )


    robustness_box.delete(
        "1.0",
        "end"
    )


    report_box.delete(
        "1.0",
        "end"
    )


    routh_box.delete(
        "1.0",
        "end"
    )


    for frame in [

        bode_tab,
        nyquist_tab,
        disk_tab,
        critical_tab,
        pole_tab,
        step_tab,
        uncertainty_tab

    ]:

        clear_frame(
            frame
        )


    tabs.set(
        "Overview"
    )


# ============================================================
# BUTTON CONNECTIONS
# ============================================================

analyze_button.configure(
    command=analyze
)


compare_button.configure(
    command=show_comparison
)


robustness_button.configure(
    command=show_robustness
)


export_button.configure(
    command=export_report
)


export_figures_button.configure(
    command=export_figures
)


critical_button.configure(
    command=show_critical_disturbance
)


reset_button.configure(
    command=reset
)


# ============================================================
# DEFAULT SYSTEM
# ============================================================

num_entry.insert(
    0,
    "1"
)


den_entry.insert(
    0,
    "1, 2, 5"
)


# ============================================================
# START
# ============================================================

app.mainloop()