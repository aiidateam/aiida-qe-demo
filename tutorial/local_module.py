import json
import os
import pathlib
import shutil
import warnings
from dataclasses import dataclass

os.environ["AIIDA_PATH"] = str(pathlib.Path(__file__).parent / "_aiida_path")
import psutil
# import after setting the environment variable
from aiida import load_ipython_extension, load_profile, manage, orm
from aiida.storage.sqlite_temp import SqliteTempBackend
from aiida_pseudo.cli.install import download_sssp
from aiida_pseudo.cli.utils import create_family_from_archive
from aiida_pseudo.groups.family import SsspConfiguration, SsspFamily


@dataclass
class AiiDALoaded:
    profile: manage.Profile
    computer: orm.Computer
    pw_code: orm.Code
    pseudos: SsspFamily
    si: orm.StructureData


def load_temp_profile(
    name="temp_profile", add_computer=True, add_pw_code=True, add_sssp=True, debug=False, wipe=True,
):
    """Load a temporary profile with a computer and code."""
    try:
        load_ipython_extension(get_ipython())
    except NameError:
        pass
    path = pathlib.Path(os.environ["AIIDA_PATH"]) / ".aiida" / "repository" / name
    if wipe and path.exists():
        shutil.rmtree(path)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        manage.configuration.settings
    profile = SqliteTempBackend.create_profile(
            name,
            options={"runner.poll.interval": 1},
            debug=debug,
    )
    profile = load_profile(profile)
    computer = load_computer(wipe) if add_computer else None
    pw_code = load_pw_code(computer) if (computer and add_pw_code) else None
    pseudos = load_sssp_pseudos() if add_sssp else None
    si = create_si_structure()

    return AiiDALoaded(profile, computer, pw_code, pseudos, si)


def load_computer(wipe=True):
    """Idempotent function to add the computer to the database."""
    path = pathlib.Path(__file__).parent / "_aiida_workdir"
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
        pseudos = pathlib.Path("sssp_pseudos")
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
