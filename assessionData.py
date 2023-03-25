from dataclasses import dataclass

@dataclass(frozen=True)
class assessionData:
    accession:str
    env_from:int
    env_to:int