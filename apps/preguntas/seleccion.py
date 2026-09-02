from abc import ABC, abstractmethod
import random
from .repositories import PreguntaRepository

DISTRIBUCION_DEFECTO = {
    "contextual": 2,
    "vf_premisas": 1,
    "cuantas_correctas": 1,
    "completar": 1,
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
