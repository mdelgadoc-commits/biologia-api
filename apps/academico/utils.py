"""
Funciones STATELESS: no tocan la base de datos ni nada externo.
Mismos parámetros -> mismo resultado, siempre. Ideales para testear sin BD.
"""


def calcular_progreso_porcentaje(total_temas: int, completados: int) -> float:
    """Ej: 5 temas, 2 completados -> 40.0"""
    if total_temas == 0:
        return 0.0
    return round((completados / total_temas) * 100, 1)


def determinar_icono_estado(desbloqueado: bool, completado: bool) -> str:
    """Traduce el estado de un tema al nombre del ícono que debe mostrar Vue."""
    if completado:
        return "check"
    if desbloqueado:
        return "disponible"
    return "candado"


def validar_secuencia_ordenes(ordenes: list) -> bool:
    """True si los 'orden' de los temas de una etapa son consecutivos (1,2,3...)
    sin huecos ni repetidos."""
    esperado = list(range(1, len(ordenes) + 1))
    return sorted(ordenes) == esperado
