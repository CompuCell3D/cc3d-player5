import sys
import os
from pathlib import Path
import subprocess
import argparse


def main():
    conda_exec = find_conda()
    print('conda_exec=', conda_exec)
    conda_env_name = find_current_conda_env(conda_exec=conda_exec)
    if not conda_exec or not conda_env_name:
        return

    args = process_cml()

# {conda_exec} activate base \n conda list env

    command_win = f'echo %cd% & {conda_exec} activate c1_test & conda list'

    # command_win = f'{conda_exec} activate {conda_env_name} & conda install -c local cc3d=4.3.1'

    command_join_char = ';'
    if sys.platform.startswith('win'):
        command_join_char = '&'

    command = f'{conda_exec} activate c2_test {command_join_char} conda install -c local {args.package}={args.version}'


    # ret = subprocess.run(command_win, capture_output=True, shell=True)
    # print(ret.stdout.decode())
    proc = subprocess.Popen(command, shell=True)
    proc.wait()


    # subprocess.run(f'{conda_exec} activate base ; conda list env', shell=True)
    # subprocess.call(f'{conda_exec} list env', shell=True)
    # os.system(f'{conda_exec} activate base', )
    # os.system(f'{conda_exec} list env')
    input1 = input("PRESS ANY KEY TO CONTINUE... ")


def process_cml():
    """

    :return:
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--package', type=str)
    parser.add_argument('--version', type=str)

    # Parse and print the results
    args = parser.parse_args()

    return args

def find_current_conda_env(conda_exec):
    if conda_exec is None:
        return None

    envs = subprocess.check_output(f'{conda_exec} env list', shell=True).splitlines()
    active_env = list(filter(lambda s: '*' in str(s), envs))[0]
    env_name = active_env.decode("utf-8").split()[0]
    return env_name


def find_conda():
    conda_exec = None
    python_exec = Path(sys.executable)
    python_exec_dir = python_exec.parent
    print('python_exec_dir=', python_exec_dir)

    if sys.platform.startswith('darwin') or sys.platform.startswith('linux'):

        conda_exec_candidates = [
            # if using other env
            Path().joinpath(*python_exec_dir.parts[:-3]).joinpath('bin', 'conda'),
            # if using python.app or similar from env
            Path().joinpath(*python_exec_dir.parts[:-5]).joinpath('bin', 'conda'),
            # if using base conda env
            python_exec_dir.joinpath('conda'),
        ]

        for candidate in conda_exec_candidates:
            if candidate.exists() and os.access(str(candidate), os.X_OK):
                conda_exec = candidate
                break

        print('conda_exec=', conda_exec)
        os.system(str(conda_exec))
    elif sys.platform.startswith('win'):

        conda_exec_candidates = [
            # if using other env
            Path().joinpath(*python_exec_dir.parts[:-2]).joinpath('condabin', 'conda.bat'),
            # if using python.app or similar from env

            # if using base conda env
            python_exec_dir.joinpath('condabin', 'conda.bat'),
        ]

        for candidate in conda_exec_candidates:
            if candidate.exists():
                conda_exec = candidate
                break

    return conda_exec


if __name__ == '__main__':
    main()
