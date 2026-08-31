from abc import ABC, abstractmethod
import random
from .repositories import PreguntaRepository

DISTRIBUCION_DEFECTO = {
    "contextual": 8,
    "vf_premisas": 4,
    "cuantas_correctas": 4,
    "inferencial": 4,
    "completar": 10,
}


class EstrategiaSeleccionPreguntas(ABC):
    @abstractmethod
    def seleccionar(self, tema_id: int) -> list:
        ...


class SeleccionAleatoriaSimple(EstrategiaSeleccionPreguntas):
    def __init__(self, distribucion: dict = None):
        self.distribucion = distribucion or DISTRIBUCION_DEFECTO

    def seleccionar(self, tema_id: int) -> list:
        preguntas = []
        for tipo, cantidad in self.distribucion.items():
            preguntas += PreguntaRepository.por_tema_y_tipo(tema_id, tipo, cantidad)
        random.shuffle(preguntas)
        return preguntas
