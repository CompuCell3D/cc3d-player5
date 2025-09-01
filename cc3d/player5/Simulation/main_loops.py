import time

from cc3d import CompuCellSetup
from cc3d.CompuCellSetup import (
    check_for_cpp_errors, incorporate_script_steering_changes, initialize_cc3d_sim, print_profiling_report)
from cc3d.core.logging import LoggedContext
from cc3d.cpp import CompuCell


def main_loop_player(sim, simthread=None, steppable_registry=None):
    """
    main loop for GUI based simulations
    :param sim:
    :param simthread:
    :param steppable_registry:
    :return:
    """
    t1 = time.time()
    compiled_code_run_time = 0.0

    pg = CompuCellSetup.persistent_globals

    steppable_registry = pg.steppable_registry
    simthread = pg.simthread

    initialize_cc3d_sim(sim, simthread)

    restart_manager = pg.restart_manager
    init_using_restart_snapshot_enabled = restart_manager.restart_enabled()

    # simthread.waitForInitCompletion()
    # simthread.waitForPlayerTaskToFinish()

    with LoggedContext() as lc:

        if steppable_registry is not None:
            lc.log()

            steppable_registry.init(sim)

    # called in extraInitSimulationObjects
    # sim.start()

    with LoggedContext() as lc:

        if not steppable_registry is None and not init_using_restart_snapshot_enabled:
            lc.log()

            steppable_registry.start()
            simthread.steppablePostStartPrep()

    run_finish_flag = True

    restart_manager.prepare_restarter()
    beginning_step = restart_manager.get_restart_step()

    with LoggedContext() as lc:

        if init_using_restart_snapshot_enabled:
            lc.log()

            steppable_registry.restart_steering_panel()

    cur_step = beginning_step

    with LoggedContext() as lc:

        while cur_step < sim.getNumSteps():
            lc.log(msg=f'Step {cur_step}')

            simthread.beforeStep(_mcs=cur_step)
            if simthread.getStopSimulation() or CompuCellSetup.persistent_globals.user_stop_simulation_flag:
                lc.log()

                run_finish_flag = False
                break

            if steppable_registry is not None:
                lc.log()

                steppable_registry.stepRunBeforeMCSSteppables(cur_step)

            compiled_code_begin = time.time()

            if cur_step != 0 or CompuCellSetup.persistent_globals.execute_step_at_mcs_0:
                sim.step(cur_step)  # steering using steppables

            check_for_cpp_errors(CompuCellSetup.persistent_globals.simulator)

            compiled_code_end = time.time()

            compiled_code_run_time += (compiled_code_end - compiled_code_begin) * 1000

            # steering using GUI. GUI steering overrides steering done in the steppables
            simthread.steerUsingGUI(sim)

            if not steppable_registry is None:
                lc.log()

                steppable_registry.step(cur_step)

            # restart manager will decide whether to output files or not based on its settings
            restart_manager.output_restart_files(cur_step)

            # passing Python-script-made changes in XML to C++ code
            incorporate_script_steering_changes(simulator=sim)

            # steer application will only update modules that uses requested using updateCC3DModule function from simulator
            sim.steer()
            check_for_cpp_errors(CompuCellSetup.persistent_globals.simulator)

            screen_update_frequency = simthread.getScreenUpdateFrequency()
            screenshot_frequency = simthread.getScreenshotFrequency()
            screenshot_output_flag = simthread.getImageOutputFlag()

            if pg.screenshot_manager is not None and pg.screenshot_manager.has_ad_hoc_screenshots():
                lc.log()

                simthread.loopWork(cur_step)
                simthread.loopWorkPostEvent(cur_step)

            elif (screen_update_frequency > 0 and cur_step % screen_update_frequency == 0) or (
                    screenshot_output_flag and screenshot_frequency > 0 and cur_step % screenshot_frequency == 0):
                lc.log()

                simthread.loopWork(cur_step)
                simthread.loopWorkPostEvent(cur_step)

            cur_step += 1

            # checking if curr step is listed in pause_at dict. If so we emit pause signal
            try:
                with LoggedContext():

                    pg.pause_at[cur_step]
                    simthread.emit_pause_request()

            except KeyError:
                lc.log()
                pass

    with LoggedContext() as lc:

        if run_finish_flag:
            lc.log()

            # # we emit request to finish simulation
            simthread.emitFinishRequest()
            # # then we wait for GUI thread to unlock the finishMutex - it will only happen when all tasks
            # in the GUI thread are completed (especially those that need simulator object to stay alive)
            print("CALLING FINISH")
            lc.log(CompuCell.LOG_INFORMATION, 'CALLING FINISH')

            simthread.waitForFinishingTasksToConclude()
            simthread.waitForPlayerTaskToFinish()
            steppable_registry.finish()
            sim.cleanAfterSimulation()
            simthread.simulationFinishedPostEvent(True)
            steppable_registry.clean_after_simulation()

        else:
            lc.log()

            steppable_registry.on_stop()
            sim.cleanAfterSimulation()

            # # sim.unloadModules()
            print("CALLING UNLOAD MODULES NEW PLAYER")
            lc.log(CompuCell.LOG_INFORMATION, 'CALLING UNLOAD MODULES NEW PLAYER')

            simthread.sendStopSimulationRequest()
            simthread.simulationFinishedPostEvent(True)

            steppable_registry.clean_after_simulation()

    t2 = time.time()
    print_profiling_report(py_steppable_profiler_report=steppable_registry.get_profiler_report(),
                           compiled_code_run_time=compiled_code_run_time, total_run_time=(t2 - t1) * 1000.0)
    simthread.emit_make_movie_request()


def main_loop_player_cml_result_replay(sim, simthread, steppableRegistry):
    """

    :param sim:
    :param simthread:
    :param steppableRegistry:
    :return:
    """
