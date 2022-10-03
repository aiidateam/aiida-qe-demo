"""Load and populate a temporary profile with a computer and code."""
from __future__ import annotations

import json
import os
import pathlib
import shutil
from dataclasses import dataclass

import psutil

# import after setting the environment variable
from aiida import get_profile, load_ipython_extension, load_profile, manage, orm
from aiida.storage.sqlite_temp import SqliteTempBackend
from aiida_pseudo.cli.install import download_sssp
from aiida_pseudo.cli.utils import create_family_from_archive
from aiida_pseudo.groups.family import SsspConfiguration, SsspFamily


@dataclass
class AiiDALoaded:
    profile: manage.Profile
    computer: orm.Computer
    code: orm.Code
    pseudos: SsspFamily
    structure: orm.StructureData


def load_temp_profile(
    name="temp_profile",
    add_computer=True,
    add_pw_code=True,
    add_sssp=True,
    debug=False,
    wipe_previous=True,
):
    """Load a temporary profile with a computer and code.

    This function is idempotent, so it can be called multiple times without
    creating duplicate computers and codes.

    :param name: The name of the profile to load.
    :param add_computer: Whether to add a computer to the profile.
    :param add_pw_code: Whether to add a Quantum ESPRESSO pw.x code to the profile.
    :param add_sssp: Whether to add the SSSP pseudopotentials to the profile.
    :param debug: Whether to enable debug mode (printing all SQL queries).
    :param wipe_previous: Whether to wipe any previous data
    """
    # load the ipython extension, if possible
    try:
        load_ipython_extension(get_ipython())
    except NameError:
        pass

    profile = get_profile()
    loaded = False
    if not (profile and profile.name == name):
        loaded = True
        path = pathlib.Path(os.environ["AIIDA_PATH"]) / ".aiida" / "repository" / name
        if wipe_previous and path.exists():
            shutil.rmtree(path)
        profile = SqliteTempBackend.create_profile(
            name,
            options={"runner.poll.interval": 1},
            debug=debug,
        )
    load_profile(profile, allow_switch=True)
    computer = (
        load_computer(profile.name, loaded and wipe_previous) if add_computer else None
    )
    pw_code = load_pw_code(computer) if (computer and add_pw_code) else None
    pseudos = load_sssp_pseudos() if add_sssp else None
    structure = create_si_structure()

    return AiiDALoaded(profile, computer, pw_code, pseudos, structure)


def load_computer(profile_name: str, wipe=True):
    """Idempotent function to add the computer to the database."""
    path = pathlib.Path(__file__).parent / "_aiida_workdir" / profile_name
    if wipe and path.exists():
        shutil.rmtree(path)
    created, computer = orm.Computer.collection.get_or_create(
        label="local_direct",
        description="local computer with direct scheduler",
        hostname="localhost",
        workdir=str(path.absolute()),
        transport_type="core.local",
        scheduler_type="core.direct",
    )
    if created:
        computer.store()
        computer.set_minimum_job_poll_interval(0.0)
        computer.set_default_mpiprocs_per_machine(
            min(2, psutil.cpu_count(logical=False))
        )
        computer.configure()
    return computer


def load_pw_code(computer):
    """Idempotent function to add the code to the database."""
    try:
        code = orm.load_code("pw.x@local_direct")
    except:
        code = orm.Code(
            input_plugin_name="quantumespresso.pw",
            remote_computer_exec=[computer, shutil.which("pw.x")],
        )
        code.label = "pw.x"
        code.description = "pw.x code on local computer"
        code.set_prepend_text("export OMP_NUM_THREADS=1")
        code.store()
    return code


def create_si_structure():
    cell = [
        [3.7881476451529, 0.0, 0.0],
        [1.8940738225764, 3.2806320939886, 0.0],
        [1.8940738225764, 1.0935440313296, 3.0930096003167],
    ]
    structure = orm.StructureData(cell=cell)
    structure.append_atom(position=(0.0, 0.0, 0.0), symbols="Si")
    structure.append_atom(
        position=(1.8940738225764, 1.0935440313296, 0.77325240007918), symbols="Si"
    )
    structure.store()
    return structure


def load_sssp_pseudos(version="1.1", functional="PBE", protocol="efficiency"):
    """Load the SSSP pseudopotentials."""
    config = SsspConfiguration(version, functional, protocol)
    label = SsspFamily.format_configuration_label(config)

    try:
        family = orm.Group.collection.get(label=label)
    except:
        pseudos = pathlib.Path(__file__).parent / "sssp_pseudos"
        pseudos.mkdir(exist_ok=True)

        filename = label.replace("/", "-")

        if not (pseudos / (filename + ".tar.gz")).exists():
            download_sssp(
                config, pseudos / (filename + ".tar.gz"), pseudos / (filename + ".json")
            )

        family = create_family_from_archive(
            SsspFamily,
            label,
            pseudos / (filename + ".tar.gz"),
        )
        family.set_cutoffs(
            {
                k: {i: v[i] for i in ["cutoff_wfc", "cutoff_rho"]}
                for k, v in json.loads(
                    (pseudos / (filename + ".json")).read_text()
                ).items()
            },
            "normal",
            unit="Ry",
        )
    return family
