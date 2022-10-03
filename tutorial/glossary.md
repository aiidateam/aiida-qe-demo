# Glossary

:::{glossary}

Computer
    Defines a computational resource, on which calculations can be run.
    It is loaded with a {term}`Transport` and {term}`Scheduler` plugin.

Code
    Defines a program that can be run on a {term}`Computer`.
    It is a special subclass of {term}`Data` node that can be used as input to a {term}`CalcJob`.

CalcJob
    A special type of {term}`Process` that is used to define the running of a {term}`Code`, the inputs required, the outputs generated, and the possible exit states.

Data
    A node that contains data, stored in the database.
    It is a subclass of {term}`Node` that can be linked as an input or output to a {term}`ProcessNode`.

Node
    The fundamental entity of AiiDA {term}`Provenance`.
    It is a container for data, which can be stored, and can be linked to other nodes.
    Nodes are subclassed into {term}`Data` and {term}`ProcessNode`.

Profile
    A collection of settings for a single AiiDA project.
    It includes configuration for connecting to data storage instances, which will record the provenance of your calculations.

Provenance
    The history of how data is created.
    AiiDA records the provenance of all data, and can use this to reconstruct the history of a calculation.

Scheduler
    A plugin that defines how AiiDA interfaces with a {term}`Computer`'s job scheduling software.

Process
    A task that can be run on a {term}`Computer`.
    When run, it will create a {term}`ProcessNode` that records the provenance of the process.

ProcessNode
    A node that represents a {term}`Process` in the provenance graph.
    It is a subclass of {term}`Node` and can be linked to input and output {term}`Data` nodes.

Transport
    A plugin that defines how AiiDA pulls and pushes data from a {term}`Computer`.

User
    Defines the creator of a piece of data.
    All {term}`Node` objects have a user associated with them.

Workflow
    A special type of {term}`Process` that defines one or more tasks to be run in sequence, the inputs required, the outputs generated, and the possible exit states.
    Each task can itself submit one or more {term}`CalcJob` or {term}`Workflow`.

:::
