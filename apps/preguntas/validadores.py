from abc import ABC, abstractmethod

from apps.preguntas.models import ElementoPregunta


class ValidadorRespuesta(ABC):
    def __init__(self, pregunta):
        self.pregunta = pregunta

    @abstractmethod
    def validar(self, payload: dict) -> bool:
        ...


class ValidadorContextualOInferencial(ValidadorRespuesta):
    def validar(self, payload):
        return self.pregunta.elementos.filter(
            id=payload.get("alternativa_id"),
            rol=ElementoPregunta.Rol.ALTERNATIVA,
            es_correcto=True,
        ).exists()


class ValidadorVFPremisas(ValidadorRespuesta):
    """El alumno marca cada premisa como Verdadero/Falso.
    payload: {"premisas": {<premisa_id>: bool}} donde bool es lo que marcó
    el alumno y es_correcto del elemento es la verdad real."""

    def validar(self, payload):
        respuestas = payload.get("premisas")
        if not isinstance(respuestas, dict) or not respuestas:
            return False

        premisas = list(self.pregunta.elementos.filter(rol=ElementoPregunta.Rol.PREMISA))
        if len(premisas) != len(respuestas):
            return False

        return all(
            respuestas.get(premisa.id) == premisa.es_correcto
            for premisa in premisas
        )


class ValidadorCuantasCorrectas(ValidadorRespuesta):
    """El alumno indica cuántas de las premisas son verdaderas.
    payload: {"cuantas_correctas": int}"""

    def validar(self, payload):
        valor = payload.get("cuantas_correctas")
        if valor is None or not isinstance(valor, int):
            return False

        cuantas = self.pregunta.elementos.filter(
            rol=ElementoPregunta.Rol.PREMISA, es_correcto=True
        ).count()
        return valor == cuantas


class ValidadorCompletar(ValidadorRespuesta):
    def validar(self, payload):
        huecos = {
            e.posicion_hueco: e.id
            for e in self.pregunta.elementos.filter(rol=ElementoPregunta.Rol.HUECO)
        }
        if not huecos:
            return False

        return huecos == {
            int(pos): palabra_id
            for pos, palabra_id in (payload or {}).items()
        }


class ValidadorFactory:
    _registro = {
        "contextual": ValidadorContextualOInferencial,
        "inferencial": ValidadorContextualOInferencial,
        "vf_premisas": ValidadorVFPremisas,
        "cuantas_correctas": ValidadorCuantasCorrectas,
        "completar": ValidadorCompletar,
    }

    @classmethod
    def crear(cls, pregunta) -> ValidadorRespuesta:
        clase = cls._registro.get(pregunta.tipo)
        if not clase:
            raise ValueError(f"No hay validador registrado para tipo '{pregunta.tipo}'")
        return clase(pregunta)