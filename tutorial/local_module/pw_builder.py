from aiida.orm import Code, Bool, StructureData

from aiida_quantumespresso.workflows.pw.base import PwBaseWorkChain
from aiida_quantumespresso.calculations.functions.create_kpoints_from_distance import (
    create_kpoints_from_distance,
)


def get_pw_builder(code: Code, structure: StructureData, protocol: str = "moderate"):
    """Get a fully populated `PwCalculation` builder for a given structure and protocol."""

    base_builder = PwBaseWorkChain.get_builder_from_protocol(
        code=code,
        structure=structure,
        protocol=protocol,
    )

    pw_builder = code.get_builder()

    pw_builder.structure = structure
    pw_builder.kpoints = create_kpoints_from_distance(
        structure=structure,
        distance=base_builder.kpoints_distance,
        force_parity=Bool(False),
        metadata={"store_provenance": False},
    )
    pw_builder.parameters = base_builder.pw.parameters
    pw_builder.pseudos = base_builder.pw.pseudos

    return pw_builder
