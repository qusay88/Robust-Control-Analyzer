# Robust Control Analyzer

A Python-based graphical tool for classical stability analysis and disk-margin
robustness assessment of single-input single-output linear time-invariant systems.

From one transfer function it computes closed-loop stability, Routh–Hurwitz
conditions, Bode and Nyquist behavior, classical gain/phase margins, S-based,
balanced and T-based disk margins, critical gain–phase disturbance levels,
pole-zero maps, step-response metrics and the uncertainty region, and exports a report.

## Installation

    git clone https://github.com/qusay88/Robust-Control-Analyzer.git
    cd Robust-Control-Analyzer
    pip install -r requirements.txt

Tested with Python 3.12.5 (NumPy 2.5.2, SciPy 1.18.0, Matplotlib 3.11.1,
python-control 0.10.2, CustomTkinter 5.2.2).

## Usage

    python Robust_Control_Analyzer.py

Enter the numerator and denominator coefficients, choose the feedback
configuration, frequency range and gain/phase uncertainty, then open the analysis tabs.

## Validation

* `examples/dc_motor_validation.py` — DC-motor position loop with P and PID
  controllers; compares python-control disk margins (the call used by the tool)
  with an independent closed-form evaluation.
* `validation/matlab_diskmargin_check.m` — prints MATLAB `diskmargin` values for the
  six benchmark systems and the DC-motor loops, to compare with the tool.

## Citation

See `CITATION.cff`. A DOI is provided by the Zenodo archive of each tagged release.

## License

MIT — see `LICENSE`.
