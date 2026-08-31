from abc import ABC, abstractmethod


class ValidadorRespuesta(ABC):
    def __init__(self, pregunta):
        self.pregunta = pregunta

    @abstractmethod
    def validar(self, payload: dict) -> bool:
        ...


class ValidadorContextualOInferencial(ValidadorRespuesta):
    def validar(self, payload):
        return self.pregunta.elementos.filter(
            id=payload["alternativa_id"], rol="alternativa", es_correcto=True
        ).exists()


class ValidadorVFPremisas(ValidadorRespuesta):
    def validar(self, payload):
        return self.pregunta.elementos.filter(
            id=payload["alternativa_id"], rol="alternativa", es_correcto=True
        ).exists()


class ValidadorCuantasCorrectas(ValidadorRespuesta):
    def validar(self, payload):
        return self.pregunta.elementos.filter(
            id=payload["alternativa_id"], rol="alternativa", es_correcto=True
        ).exists()


class ValidadorCompletar(ValidadorRespuesta):
    def validar(self, payload):
        huecos = {e.posicion_hueco: e.id for e in self.pregunta.elementos.filter(rol="hueco")}
        return all(
            huecos.get(int(pos)) == palabra_id
            for pos, palabra_id in payload.items()
        )


class ValidadorAbierta(ValidadorRespuesta):
    def validar(self, payload):
        return None


class ValidadorFactory:
    _registro = {
        "contextual": ValidadorContextualOInferencial,
        "inferencial": ValidadorContextualOInferencial,
        "vf_premisas": ValidadorVFPremisas,
        "cuantas_correctas": ValidadorCuantasCorrectas,
        "completar": ValidadorCompletar,
        "abierta": ValidadorAbierta,
    }

    @classmethod
    def crear(cls, pregunta) -> ValidadorRespuesta:
        clase = cls._registro.get(pregunta.tipo)
        if not clase:
            raise ValueError(f"No hay validador registrado para tipo '{pregunta.tipo}'")
        return clase(pregunta)
