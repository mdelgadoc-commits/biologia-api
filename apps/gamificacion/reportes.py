from django.db.models import Count, Q, Avg, F
from django.utils import timezone
from datetime import timedelta
from apps.intentos.models import RespuestaEstudiante, IntentoTema
from apps.users.models import PerfilEstudiante

UMBRAL_APROBACION = 85  # % — como en "Pass Rate (>85%)"


class ReporteSeccionService:
    """Arma los datos agregados de una sección (clase) para el dashboard docente."""

    def __init__(self, seccion, tema_id=None):
        self.seccion = seccion
        self.tema_id = tema_id  # filtro opcional por 'Topic'

    def _intentos_base(self):
        qs = IntentoTema.objects.filter(estudiante__in=self.seccion.estudiantes.all())
        if self.tema_id:
            qs = qs.filter(tema_id=self.tema_id)
        return qs

    def resumen(self):
        """Total Students, Pass Rate, Avg Score — la fila superior del dashboard."""
        estudiantes = self.seccion.estudiantes.count()
        intentos = self._intentos_base().filter(completado=True)
        promedios = []
        for intento in intentos:
            total = intento.respuestas.count()
            if total == 0:
                continue
            correctas = intento.respuestas.filter(es_correcta=True).count()
            promedios.append(correctas / total * 100)
        avg_score = round(sum(promedios) / len(promedios), 0) if promedios else 0
        pass_rate = round(
            (sum(1 for p in promedios if p >= UMBRAL_APROBACION) / len(promedios) * 100)
            if promedios else 0
        )
        return {
            "total_students": estudiantes,
            "pass_rate": pass_rate,
            "avg_score": avg_score,
        }

    def conceptos_criticos(self, limite=5):
        """'Bombea sangre (Corazón) - 85% error, 27 alumnos' — agrupado por pregunta/tripleta."""
        respuestas = RespuestaEstudiante.objects.filter(
            intento__in=self._intentos_base()
        ).select_related("pregunta")
        agregados = (
            respuestas.values("pregunta__id", "pregunta__enunciado")
            .annotate(
                total=Count("id"),
                errores=Count("id", filter=Q(es_correcta=False)),
            )
            .order_by()
        )
        resultado = []
        for a in agregados:
            if a["total"] == 0:
                continue
            tasa_error = round(a["errores"] / a["total"] * 100)
            resultado.append({
                "concepto": a["pregunta__enunciado"],
                "tasa_error": tasa_error,
                "alumnos_fallaron": a["errores"],
            })
        resultado.sort(key=lambda x: x["tasa_error"], reverse=True)
        return resultado[:limite]

    def heatmap(self):
        """Estudiante x Tema -> % de aciertos. Para la tabla roja/amarilla/verde."""
        filas = []
        for perfil in self.seccion.estudiantes.select_related("usuario"):
            intentos = self._intentos_base().filter(estudiante=perfil, completado=True)
            fila = {"estudiante": perfil.usuario.get_full_name() or perfil.usuario.username, "temas": {}}
            for intento in intentos:
                total = intento.respuestas.count()
                if total == 0:
                    continue
                correctas = intento.respuestas.filter(es_correcta=True).count()
                fila["temas"][intento.tema.titulo] = round(correctas / total * 100)
            filas.append(fila)
        return filas

    def evolucion_mensual(self, meses=6, top=5):
        """Top N estudiantes con su % de acierto mes a mes + % de mejora este mes."""
        desde = timezone.now() - timedelta(days=30 * meses)
        respuestas = RespuestaEstudiante.objects.filter(
            intento__in=self._intentos_base(),
            creado__gte=desde,
        ).select_related("intento__estudiante__usuario")

        datos = {}
        for r in respuestas:
            estudiante = r.intento.estudiante
            mes = r.creado.strftime("%Y-%m")
            datos.setdefault(estudiante.id, {"estudiante": estudiante, "meses": {}})
            m = datos[estudiante.id]["meses"].setdefault(mes, {"total": 0, "correctas": 0})
            m["total"] += 1
            if r.es_correcta:
                m["correctas"] += 1

        series = []
        for info in datos.values():
            meses_ordenados = sorted(info["meses"].keys())
            puntos = [
                {"mes": m, "porcentaje": round(v["correctas"] / v["total"] * 100)}
                for m, v in ((m, info["meses"][m]) for m in meses_ordenados)
            ]
            mejora = puntos[-1]["porcentaje"] - puntos[-2]["porcentaje"] if len(puntos) >= 2 else 0
            promedio = round(sum(p["porcentaje"] for p in puntos) / len(puntos)) if puntos else 0
            series.append({
                "estudiante": info["estudiante"].usuario.get_full_name() or info["estudiante"].usuario.username,
                "puntos": puntos,
                "promedio": promedio,
                "mejora_este_mes": mejora,
            })
        series.sort(key=lambda s: s["promedio"], reverse=True)
        return series[:top]

    def evolucion_individual(self, estudiante_id):
        """Para el filtro 'Alumno - Juan Pérez': avance de velocidad y precisión."""
        intentos = self._intentos_base().filter(estudiante_id=estudiante_id, completado=True).order_by("iniciado")
        puntos = []
        for intento in intentos:
            respuestas = intento.respuestas.all()
            total = respuestas.count()
            if total == 0:
                continue
            correctas = respuestas.filter(es_correcta=True).count()
            tiempos = [r.tiempo_respuesta_ms for r in respuestas if r.tiempo_respuesta_ms]
            tiempo_prom = round(sum(tiempos) / len(tiempos)) if tiempos else None
            puntos.append({
                "tema": intento.tema.titulo,
                "fecha": intento.iniciado.date().isoformat(),
                "precision": round(correctas / total * 100),
                "tiempo_respuesta_prom_ms": tiempo_prom,
            })
        if len(puntos) >= 2:
            mejora_precision = puntos[-1]["precision"] - puntos[0]["precision"]
            tiempos_validos = [p["tiempo_respuesta_prom_ms"] for p in puntos if p["tiempo_respuesta_prom_ms"]]
            mejora_velocidad_ms = (
                tiempos_validos[0] - tiempos_validos[-1] if len(tiempos_validos) >= 2 else None
            )
        else:
            mejora_precision = 0
            mejora_velocidad_ms = None
        return {
            "puntos": puntos,
            "mejora_precision_pct": mejora_precision,
            "mejora_velocidad_ms": mejora_velocidad_ms,
        }
