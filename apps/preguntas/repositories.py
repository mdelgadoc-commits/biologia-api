from .models import Pregunta


class PreguntaRepository:
    @staticmethod
    def por_tema_y_tipo(tema_id: int, tipo: str, cantidad: int):
        return list(
            Pregunta.objects.filter(tema_id=tema_id, tipo=tipo, activa=True)
            .order_by("?")[:cantidad]
        )

    @staticmethod
    def pertenece_al_tema(pregunta_id: int, tema_id: int) -> bool:
        return Pregunta.objects.filter(id=pregunta_id, tema_id=tema_id, activa=True).exists()

    @staticmethod
    def obtener_activa(pregunta_id: int) -> Pregunta:
        return Pregunta.objects.get(id=pregunta_id, activa=True)
