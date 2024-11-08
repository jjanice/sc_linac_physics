from random import choice
from unittest.mock import MagicMock, call

from PyQt5.QtGui import QColor
from pytestqt.qtbot import QtBot

from applications.quench_processing.quench_gui import QuenchGUI
from applications.quench_processing.quench_linac import QUENCH_MACHINE
from applications.quench_processing.quench_worker import QuenchWorker
from utils.qt import make_rainbow
from utils.sc_linac.decarad import Decarad

non_hl_iterator = QUENCH_MACHINE.non_hl_iterator


def populate_gui(gui: QuenchGUI):
    gui.status_label.setText = MagicMock()
    gui.status_label.setStyleSheet = MagicMock()
    gui.start_button.setEnabled = MagicMock()
    cavity = next(non_hl_iterator)
    gui.current_cav = cavity
    gui.current_cm = cavity.cryomodule
    # gui.cm_combobox.setCurrentText(cavity.cryomodule.name)
    # gui.cav_combobox.setCurrentText(str(cavity.number))


def test_handle_status(qtbot: QtBot):
    gui = QuenchGUI()
    qtbot.addWidget(gui)
    populate_gui(gui)
    msg = "Testing handle status"
    gui.handle_status(msg)
    gui.status_label.setStyleSheet.assert_called_with("color: blue;")
    gui.status_label.setText.assert_called_with(msg)


def test_handle_error(qtbot):
    gui = QuenchGUI()
    qtbot.addWidget(gui)
    populate_gui(gui)
    msg = "Testing handle error"
    gui.handle_error(msg)
    gui.status_label.setStyleSheet.assert_called_with("color: red;")
    gui.status_label.setText.assert_called_with(msg)
    gui.start_button.setEnabled.assert_called_with(True)


def test_handle_finished(qtbot):
    gui = QuenchGUI()
    qtbot.addWidget(gui)
    populate_gui(gui)
    msg = "Testing handle finished"
    gui.handle_finished(msg)
    gui.status_label.setStyleSheet.assert_called_with("color: green;")
    gui.status_label.setText.assert_called_with(msg)
    gui.start_button.setEnabled.assert_called_with(True)


def test_process(qtbot):
    gui = QuenchGUI()
    qtbot.addWidget(gui)
    populate_gui(gui)
    gui.current_decarad = Decarad(choice([1, 2]))
    gui.make_quench_worker = MagicMock()
    gui.quench_worker = MagicMock()
    gui.process()
    gui.start_button.setEnabled.assert_called_with(False)
    assert gui.current_cav.decarad == gui.current_decarad
    gui.make_quench_worker.assert_called()
    gui.quench_worker.start.assert_called()


def test_make_quench_worker(qtbot: QtBot):
    gui = QuenchGUI()
    qtbot.addWidget(gui)
    populate_gui(gui)
    gui.quench_worker = None
    gui.make_quench_worker()
    assert isinstance(gui.quench_worker, QuenchWorker)


def test_clear_connections(qtbot: QtBot):
    gui = QuenchGUI()
    qtbot.addWidget(gui)
    populate_gui(gui)
    signal = MagicMock()
    gui.clear_connections(signal)
    signal.disconnect.assert_called()


def test_clear_all_connections(qtbot: QtBot):
    gui = QuenchGUI()
    qtbot.addWidget(gui)
    populate_gui(gui)
    gui.rf_controls = MagicMock()
    gui.clear_connections = MagicMock()
    gui.clear_all_connections()
    gui.clear_connections.assert_called_with(gui.decarad_off_button.clicked)


def test_update_timeplot(qtbot: QtBot):
    gui = QuenchGUI()
    qtbot.addWidget(gui)
    populate_gui(gui)
    gui.update_cm = MagicMock()
    gui.amp_rad_timeplot = MagicMock()
    decarad = choice([1, 2])
    gui.decarad_combobox.setCurrentText(str(decarad))
    gui.update_timeplot()
    gui.amp_rad_timeplot.clearCurves.assert_called()
    gui.amp_rad_timeplot.addYChannel.assert_called()

    colors = make_rainbow(num_colors=11)
    channels = [gui.current_cav.aact_pv] + [
        head.raw_dose_rate_pv for head in Decarad(decarad).heads.values()
    ]
    axes = ["Amplitude"] + ["Radiation" for _ in range(10)]
    calls = []
    for channel, (r, g, b, a), axis in zip(channels, colors, axes):
        calls.append(
            call(
                y_channel=channel,
                useArchiveData=True,
                color=QColor(r, g, b, a),
                yAxisName=axis,
            )
        )
    gui.amp_rad_timeplot.addYChannel.assert_has_calls(calls, any_order=True)


def test_update_decarad(qtbot: QtBot):
    gui = QuenchGUI()
    qtbot.addWidget(gui)
    populate_gui(gui)
    gui.update_timeplot = MagicMock()
    gui.clear_connections = MagicMock()
    gui.decarad_on_button.clicked = MagicMock()
    gui.decarad_off_button.clicked = MagicMock()

    gui.update_decarad()

    assert gui.current_decarad == Decarad(int(gui.decarad_combobox.currentText()))
    gui.update_timeplot.assert_called()
    gui.clear_connections.assert_called()
    gui.decarad_on_button.clicked.connect.assert_called_with(
        gui.current_decarad.turn_on
    )
    gui.decarad_off_button.clicked.connect.assert_called_with(
        gui.current_decarad.turn_off
    )
    assert gui.current_decarad.power_status_pv == gui.decarad_status_readback.channel
    assert (
        gui.current_decarad.voltage_readback_pv == gui.decarad_voltage_readback.channel
    )


# TODO figure out why this test is causing problems
"""pydm.widgets.enum_combo_box:enum_combo_box.py:179
   Can not change value to 'ACCL:L0B:0110:RFMODECTRL-6'.
   Not an option in PyDMComboBox"""

# def test_update_cm(qtbot: QtBot):
#     gui = QuenchGUI()
#     qtbot.addWidget(gui)
#     populate_gui(gui)
#     gui.clear_all_connections = MagicMock()
#     gui.update_timeplot = MagicMock()
#     gui.waveform_updater.updatePlot = MagicMock()
#     gui.rf_controls.ssa_on_button = MagicMock()
#     gui.rf_controls.ssa_off_button = MagicMock()
#     gui.rf_controls.rf_on_button = MagicMock()
#     gui.rf_controls.rf_off_button = MagicMock()
#     gui.start_button = MagicMock()
#     gui.abort_button = MagicMock()
#
#     gui.update_cm()
#     gui.clear_all_connections.assert_called()
#     gui.update_timeplot.assert_called()
#     gui.waveform_updater.updatePlot.assert_called()
#     cavity = gui.current_cav
#     gui.rf_controls.ssa_on_button.clicked.connect.assert_called_with(cavity.ssa.turn_on)
#     gui.rf_controls.ssa_off_button.clicked.connect.assert_called_with(
#         cavity.ssa.turn_off
#     )
#     assert gui.rf_controls.ssa_readback_label.channel == cavity.ssa.status_pv
#
#     assert gui.rf_controls.rf_mode_combobox.channel == cavity.rf_mode_ctrl_pv
#     assert gui.rf_controls.rf_mode_readback_label.channel == cavity.rf_mode_pv
#     gui.rf_controls.rf_on_button.clicked.connect.assert_called_with(cavity.turn_on)
#     gui.rf_controls.rf_off_button.clicked.connect.assert_called_with(cavity.turn_off)
#     assert gui.rf_controls.rf_status_readback_label.channel == cavity.rf_state_pv
#
#     assert gui.rf_controls.ades_spinbox.channel == cavity.ades_pv
#     assert gui.rf_controls.aact_readback_label.channel == cavity.aact_pv
#     assert gui.rf_controls.srf_max_spinbox.channel == cavity.srf_max_pv
#     assert gui.rf_controls.srf_max_readback_label.channel == cavity.srf_max_pv
#
#     gui.start_button.clicked.connect.assert_called_with(gui.process)
#     gui.abort_button.clicked.connect.assert_called_with(cavity.request_abort)
