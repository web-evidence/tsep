"""Bounded, isolated verification processes; no test/result cache. Apache-2.0."""
from collections import deque
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time


def stop(process):
    # Each task owns a process group, including its Python/Node descendants.
    if os.name == 'posix':
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    elif process.poll() is None:
        process.kill()
    process.wait()


def clean_environment(environment):
    return dict({k: v for k, v in environment.items() if not k.startswith('PYTHON')},
                PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')


def execute(tasks, workers, timeout, checks):
    """Run every task once, preserve ordered receipts, fail on error or interruption.

    tasks: (label, command, cwd, environment). Only independent phases belong
    here. Test order, fixtures and interpreter isolation inside a suite stay as-is.
    """
    if workers not in (1, 2, 4) or not 0 < timeout <= 86400:
        raise ValueError('Invalid bounded verification concurrency/deadline')
    pending = deque(enumerate(tasks))
    active = {}
    results = {}
    failure = None
    with tempfile.TemporaryDirectory(prefix='tsep-check-logs-') as folder:
        try:
            while pending or active:
                while pending and len(active) < workers and failure is None:
                    index, (label, command, cwd, environment) = pending.popleft()
                    out = open(Path(folder)/str(index), 'w+b')
                    err = open(Path(folder)/(str(index)+'.err'), 'w+b')
                    start = time.monotonic()
                    try:
                        task_temp = Path(folder)/(str(index)+'.tmp')
                        task_temp.mkdir()
                        isolated = dict(clean_environment(environment), TMPDIR=str(task_temp))
                        process = subprocess.Popen(command, cwd=cwd, env=isolated,
                                                   stdout=out, stderr=err,
                                                   start_new_session=(os.name == 'posix'))
                    except BaseException:
                        out.close(); err.close()
                        raise
                    active[index] = (process, label, start, out, err)
                    print('[verify] start: '+label, file=sys.stderr, flush=True)
                for index, (process, label, start, out, err) in list(active.items()):
                    elapsed = time.monotonic()-start
                    code = process.poll()
                    timed_out = code is None and elapsed >= timeout
                    if code is None and not timed_out:
                        continue
                    if timed_out:
                        stop(process)
                    leaked = False
                    if os.name == 'posix' and not timed_out:
                        try:
                            os.killpg(process.pid, 0)
                        except ProcessLookupError:
                            pass
                        else:
                            leaked = True
                            stop(process)
                    out.seek(0); err.seek(0)
                    result = {'name': label, 'exit': None if timed_out else code,
                              'seconds': round(time.monotonic()-start, 3),
                              'stdout': out.read().decode('utf-8', errors='replace'),
                              'stderr': err.read().decode('utf-8', errors='replace')}
                    if timed_out:
                        result.update(timed_out=True, timeout_seconds=timeout)
                    if leaked:
                        result['leaked_process_group'] = True
                    results[index] = result
                    out.close(); err.close(); del active[index]
                    print('[verify] end: '+label+'; exit='+str(result['exit'])+
                          '; seconds='+str(result['seconds']), file=sys.stderr, flush=True)
                    if timed_out or leaked or code != 0:
                        failure = label + (' timed out' if timed_out else ' leaked descendants' if leaked else ' failed')
                if failure:
                    raise ValueError(failure+'; see check output')
                if active:
                    time.sleep(0.05)
        finally:
            # A failed/cancelled phase cannot leave descendants running, nor
            # produce a green receipt while its peers are unfinished.
            for index, (process, label, start, out, err) in active.items():
                stop(process)
                out.seek(0); err.seek(0)
                results[index] = {'name': label, 'exit': process.returncode,
                                  'cancelled': True,
                                  'seconds': round(time.monotonic()-start, 3),
                                  'stdout': out.read().decode('utf-8', errors='replace'),
                                  'stderr': err.read().decode('utf-8', errors='replace')}
                out.close(); err.close()
            checks.extend(results[index] for index in sorted(results))
