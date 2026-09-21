from django.core.cache import cache
from django.test import TestCase, TransactionTestCase

from apps.academico.models import Etapa, ProgresoTema, Seccion, Tema
from apps.intentos.models import IntentoTema
from apps.intentos.services import (
    SinPreguntasDisponibles,
    finalizar_intento,
    iniciar_intento,
    responder_pregunta,
)
from apps.preguntas.models import ElementoPregunta, Pregunta
from apps.users.models import PerfilEstudiante, Usuario


def crear_contextual(tema, creador, enunciado):
    pregunta = Pregunta.objects.create(
        tema=tema, tipo="contextual", enunciado=enunciado, creado_por=creador
    )
    ElementoPregunta.objects.create(
        pregunta=pregunta, rol="alternativa", contenido=enunciado + " ok",
        es_correcto=True, orden=0,
    )
    ElementoPregunta.objects.create(
        pregunta=pregunta, rol="alternativa", contenido=enunciado + " mal",
        es_correcto=False, orden=1,
    )
    return pregunta


def crear_pregunta_por_tipo(tipo, tema, creador):
    pregunta = Pregunta.objects.create(tema=tema, tipo=tipo, creado_por=creador)
    if tipo == "contextual":
        ElementoPregunta.objects.create(
            pregunta=pregunta, rol="alternativa", contenido="ok", es_correcto=True, orden=0
        )
        ElementoPregunta.objects.create(
            pregunta=pregunta, rol="alternativa", contenido="mal", es_correcto=False, orden=1
        )
    elif tipo == "vf_premisas":
        for verdad in (True, False, True, False):
            ElementoPregunta.objects.create(
                pregunta=pregunta, rol="premisa", contenido="premisa",
                es_correcto=verdad, orden=0,
            )
    elif tipo == "cuantas_correctas":
        for verdad in (True, False, True):
            ElementoPregunta.objects.create(
                pregunta=pregunta, rol="premisa", contenido="premisa",
                es_correcto=verdad, orden=0,
            )
    elif tipo == "completar":
        ElementoPregunta.objects.create(
            pregunta=pregunta, rol="hueco", contenido="sol", es_correcto=True, orden=0, posicion_hueco=0
        )
        ElementoPregunta.objects.create(
            pregunta=pregunta, rol="hueco", contenido="luna", es_correcto=True, orden=1, posicion_hueco=1
        )
        ElementoPregunta.objects.create(
            pregunta=pregunta, rol="distractor", contenido="estrella", es_correcto=False, orden=2
        )
    return pregunta


class IniciarYResponderTest(TestCase):
    def setUp(self):
        self.docente = Usuario.objects.create(username="doc_juego", rol=Usuario.Rol.DOCENTE)
        usuario = Usuario.objects.create(username="alu_juego", rol=Usuario.Rol.ESTUDIANTE)
        self.estudiante = PerfilEstudiante.objects.create(usuario=usuario, vidas=5, monedas=0)
        self.etapa = Etapa.objects.create(titulo="Etapa 1", orden=1)
        self.tema = Tema.objects.create(etapa=self.etapa, titulo="Tema", orden=1)

    def alternativa_correcta(self, pregunta):
        return pregunta.elementos.get(es_correcto=True)

    def test_iniciar_arma_la_distribucion_completa(self):
        # CONTEXTO: un tema con el set completo de tipos (2 contextuales + 1 de cada).
        for tipo in ("contextual", "contextual", "vf_premisas", "cuantas_correctas", "completar"):
            crear_pregunta_por_tipo(tipo, self.tema, self.docente)

        intento = iniciar_intento(self.estudiante, self.tema)

        self.assertEqual(intento.preguntas_asignadas.count(), 5)
        tipos = set(intento.preguntas_asignadas.values_list("tipo", flat=True))
        self.assertEqual(tipos, {"contextual", "vf_premisas", "cuantas_correctas", "completar"})

        retomado = iniciar_intento(self.estudiante, self.tema)
        self.assertEqual(retomado.id, intento.id)

    def test_iniciar_sin_preguntas_lanza_error(self):
        otro = Tema.objects.create(etapa=self.etapa, titulo="Sin contenido", orden=2)
        with self.assertRaises(SinPreguntasDisponibles):
            iniciar_intento(self.estudiante, otro)

    def test_responder_corregir_no_resta_vidas(self):
        crear_contextual(self.tema, self.docente, "Pregunta 1")
        pregunta = crear_contextual(self.tema, self.docente, "Pregunta 2")
        intento = iniciar_intento(self.estudiante, self.tema)
        self.assertEqual(intento.preguntas_asignadas.count(), 2)
        correcta = self.alternativa_correcta(pregunta)

        resultado = responder_pregunta(
            intento, pregunta.id, {"alternativa_id": correcta.id}, 1500
        )

        self.assertTrue(resultado["es_correcta"])
        self.assertEqual(resultado["vidas_restantes"], 5)
        self.assertFalse(resultado["intento_finalizado"])

    def test_responder_incorrecto_resta_vida_y_acumula_racha(self):
        pregunta = crear_contextual(self.tema, self.docente, "Pregunta")
        intento = iniciar_intento(self.estudiante, self.tema)
        incorrecta = pregunta.elementos.get(es_correcto=False)

        responder_pregunta(intento, pregunta.id, {"alternativa_id": incorrecta.id})

        intento.refresh_from_db()
        self.assertEqual(intento.vidas_restantes, 4)
        self.assertEqual(intento.racha_errores_actual, 1)
        self.assertEqual(intento.racha_errores_maxima, 1)

    def test_responder_ultima_pregunta_finaliza_exitoso(self):
        for tipo in ("contextual", "contextual"):
            crear_pregunta_por_tipo(tipo, self.tema, self.docente)
        intento = iniciar_intento(self.estudiante, self.tema)

        asignadas = list(intento.preguntas_asignadas.all())
        self.assertEqual(len(asignadas), 2)
        for i, pregunta in enumerate(asignadas):
            correcta = self.alternativa_correcta(pregunta)
            resultado = responder_pregunta(
                intento, pregunta.id, {"alternativa_id": correcta.id}
            )
            final = i == len(asignadas) - 1
            self.assertEqual(resultado["intento_finalizado"], final)
            if final:
                self.assertTrue(resultado["exitoso"])

        self.estudiante.refresh_from_db()
        self.assertEqual(self.estudiante.monedas, 30)

    def test_sin_vidas_finaliza_fracaso_y_no_otorga(self):
        pregunta = crear_contextual(self.tema, self.docente, "Pregunta")
        intento = iniciar_intento(self.estudiante, self.tema)
        intento.vidas_restantes = 1
        intento.save(update_fields=["vidas_restantes"])
        incorrecta = pregunta.elementos.get(es_correcto=False)

        resultado = responder_pregunta(intento, pregunta.id, {"alternativa_id": incorrecta.id})

        self.assertTrue(resultado["intento_finalizado"])
        self.assertFalse(resultado["exitoso"])
        self.assertFalse(intento.completado)
        self.estudiante.refresh_from_db()
        self.assertEqual(self.estudiante.monedas, 0)

    def test_responder_pregunta_ajena_lanza_error(self):
        pregunta = crear_contextual(self.tema, self.docente, "Pregunta")
        intento = iniciar_intento(self.estudiante, self.tema)
        otro_tema = Tema.objects.create(etapa=self.etapa, titulo="Otro", orden=9)
        ajena = crear_contextual(otro_tema, self.docente, "Ajena")
        with self.assertRaises(ValueError):
            responder_pregunta(intento, ajena.id, {"alternativa_id": 1})
        # La pregunta propia sí pertenece.
        responsable = responder_pregunta(
            intento, pregunta.id, {"alternativa_id": self.alternativa_correcta(pregunta).id}
        )
        self.assertTrue(responsable["es_correcta"])


class FinalizarIntentoProgresoTest(TestCase):
    def setUp(self):
        self.docente = Usuario.objects.create(username="doc_servicio", rol=Usuario.Rol.DOCENTE)
        usuario = Usuario.objects.create(username="alu_servicio", rol=Usuario.Rol.ESTUDIANTE)
        self.estudiante = PerfilEstudiante.objects.create(usuario=usuario, vidas=5, monedas=0)
        self.etapa = Etapa.objects.create(titulo="Etapa 1", orden=1)
        self.tema1 = Tema.objects.create(etapa=self.etapa, titulo="Tema 1", orden=1)
        self.tema2 = Tema.objects.create(
            etapa=self.etapa, titulo="Tema 2", orden=2, tema_previo=self.tema1
        )

    def crear_intento(self, vidas=5, racha=0):
        return IntentoTema.objects.create(
            estudiante=self.estudiante, tema=self.tema1,
            vidas_restantes=vidas, racha_errores_maxima=racha,
        )

    def test_exitoso_cierra_otorga_estrellas_y_desbloquea_siguiente(self):
        intento = self.crear_intento(vidas=5, racha=0)

        finalizar_intento(intento, exitoso=True)

        intento.refresh_from_db()
        self.assertIsNotNone(intento.finalizado)
        self.assertTrue(intento.completado)

        progreso = ProgresoTema.objects.get(estudiante=self.estudiante, tema=self.tema1)
        self.assertTrue(progreso.completado)
        self.assertEqual(progreso.estrellas, 3)

        siguiente = ProgresoTema.objects.get(estudiante=self.estudiante, tema=self.tema2)
        self.assertTrue(siguiente.desbloqueado)

        self.estudiante.refresh_from_db()
        self.assertEqual(self.estudiante.monedas, 30)

    def test_exitoso_con_pocas_vidas_da_menos_estrellas_y_monedas(self):
        intento = self.crear_intento(vidas=1, racha=0)

        finalizar_intento(intento, exitoso=True)

        progreso = ProgresoTema.objects.get(estudiante=self.estudiante, tema=self.tema1)
        self.assertEqual(progreso.estrellas, 1)

        self.estudiante.refresh_from_db()
        self.assertEqual(self.estudiante.monedas, 10)

    def test_no_exitoso_solo_cierra_sin_recompensas(self):
        intento = self.crear_intento(vidas=3, racha=0)

        finalizar_intento(intento, exitoso=False)

        intento.refresh_from_db()
        self.assertIsNotNone(intento.finalizado)
        self.assertFalse(intento.completado)
        self.assertFalse(
            ProgresoTema.objects.filter(estudiante=self.estudiante, tema=self.tema1).exists()
        )
        self.estudiante.refresh_from_db()
        self.assertEqual(self.estudiante.monedas, 0)

    def test_repetir_con_menos_estrellas_no_baja_la_mejor_puntuacion(self):
        finalizar_intento(self.crear_intento(vidas=5), exitoso=True)
        finalizar_intento(self.crear_intento(vidas=1), exitoso=True)

        progreso = ProgresoTema.objects.get(estudiante=self.estudiante, tema=self.tema1)
        self.assertEqual(progreso.estrellas, 3)


class FinalizarIntentoCacheTest(TransactionTestCase):
    """TransactionTestCase porque on_commit solo corre con commits reales."""

    def setUp(self):
        self.docente = Usuario.objects.create(username="doc_cache", rol=Usuario.Rol.DOCENTE)
        usuario = Usuario.objects.create(username="alu_cache", rol=Usuario.Rol.ESTUDIANTE)
        self.estudiante = PerfilEstudiante.objects.create(usuario=usuario, vidas=5, monedas=0)
        self.etapa = Etapa.objects.create(titulo="Etapa 1", orden=1)
        self.tema = Tema.objects.create(etapa=self.etapa, titulo="Tema", orden=1)
        self.seccion = Seccion.objects.create(nombre="3ro A", docente=self.docente)
        self.seccion.estudiantes.add(self.estudiante)
        self.intento = IntentoTema.objects.create(
            estudiante=self.estudiante, tema=self.tema, vidas_restantes=5
        )
        cache.clear()

    def clave(self):
        return f"dashboard:resumen:{self.seccion.id}:todos"

    def test_exitoso_invalida_cache_de_la_seccion(self):
        from apps.gamificacion.cache_reportes import obtener_resumen_cacheado
        obtener_resumen_cacheado(self.seccion)
        self.assertIsNotNone(cache.get(self.clave()))

        finalizar_intento(self.intento, exitoso=True)

        self.assertIsNone(cache.get(self.clave()))

    def test_no_exitoso_no_toca_la_cache(self):
        from apps.gamificacion.cache_reportes import obtener_resumen_cacheado
        obtener_resumen_cacheado(self.seccion)
        self.assertIsNotNone(cache.get(self.clave()))

        finalizar_intento(self.intento, exitoso=False)

        self.assertIsNotNone(cache.get(self.clave()))