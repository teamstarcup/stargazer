from dataclasses import dataclass

"""
An object that tracks metadata for a Prototype.
"""


@dataclass
class PrototypeMeta:
    file_path: str = ''
    line_number: int = -1
