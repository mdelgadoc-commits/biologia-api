from django.test import TestCase

from apps.academico.models import Etapa, Tema
from apps.preguntas.models import ElementoPregunta, Pregunta
from apps.preguntas.validadores import ValidadorFactory
from apps.users.models import Usuario


class ValidadorTest(TestCase):
    def setUp(self):
        self.profesor = Usuario.objects.create(username="prof_validador", rol=Usuario.Rol.DOCENTE)
        self.etapa = Etapa.objects.create(titulo="Etapa 1", orden=1)
        self.tema = Tema.objects.create(etapa=self.etapa, titulo="Tema", orden=1)

    def crear_pregunta(self, tipo, elementos):
        pregunta = Pregunta.objects.create(
            tema=self.tema, tipo=tipo, enunciado="Enunciado", dificultad=1,
            creado_por=self.profesor,
        )
        ElementoPregunta.objects.bulk_create([
            ElementoPregunta(
                pregunta=pregunta, rol=rol, contenido=str(i), es_correcto=es_correcto,
                orden=i, posicion_hueco=posicion_hueco,
            )
            for i, (rol, es_correcto, posicion_hueco) in enumerate(elementos)
        ])
        return pregunta

    def test_contextual_con_alternativa_correcta(self):
        pregunta = self.crear_pregunta("contextual", [
            ("alternativa", True, None),
            ("alternativa", False, None),
            ("alternativa", False, None),
        ])
        alternativa = pregunta.elementos.get(es_correcto=True)
        validador = ValidadorFactory.crear(pregunta)

        self.assertTrue(validador.validar({"alternativa_id": alternativa.id}))
        otra = pregunta.elementos.filter(es_correcto=False).first()
        self.assertFalse(validador.validar({"alternativa_id": otra.id}))

    def test_inferencial_usa_el_mismo_validador(self):
        pregunta = self.crear_pregunta("inferencial", [("alternativa", True, None)])
        alternativa = pregunta.elementos.first()
        self.assertTrue(
            ValidadorFactory.crear(pregunta).validar({"alternativa_id": alternativa.id})
        )

    def test_vf_premisas_evalua_cada_premisa(self):
        pregunta = self.crear_pregunta("vf_premisas", [
            ("premisa", True, None),
            ("premisa", False, None),
            ("premisa", True, None),
            ("premisa", False, None),
        ])
        premisas = {e.id: e.es_correcto for e in pregunta.elementos.all()}

        validador = ValidadorFactory.crear(pregunta)
        self.assertTrue(validador.validar({"premisas": premisas}))

        incorrecto = dict(premisas)
        primer_id = list(premisas)[0]
        incorrecto[primer_id] = not premisas[primer_id]
        self.assertFalse(validador.validar({"premisas": incorrecto}))

    def test_vf_premisas_requiere_responder_todas(self):
        pregunta = self.crear_pregunta("vf_premisas", [
            ("premisa", True, None),
            ("premisa", False, None),
        ])
        premisas = {e.id: e.es_correcto for e in pregunta.elementos.all()}
        completo = {k: v for k, v in premisas.items()}
        incompleto = {list(completo)[0]: list(completo.values())[0]}

        validador = ValidadorFactory.crear(pregunta)
        self.assertTrue(validador.validar({"premisas": completo}))
        self.assertFalse(validador.validar({"premisas": incompleto}))
        self.assertFalse(validador.validar({}))

    def test_cuantas_correctas_cuenta_premisas_verdaderas(self):
        pregunta = self.crear_pregunta("cuantas_correctas", [
            ("premisa", True, None),
            ("premisa", False, None),
            ("premisa", True, None),
        ])
        cuantas = pregunta.elementos.filter(es_correcto=True).count()
        self.assertEqual(cuantas, 2)

        validador = ValidadorFactory.crear(pregunta)
        self.assertTrue(validador.validar({"cuantas_correctas": 2}))
        self.assertFalse(validador.validar({"cuantas_correctas": 1}))
        self.assertFalse(validador.validar({}))

    def test_completar_exige_todos_los_huecos_sin_sobras(self):
        pregunta = self.crear_pregunta("completar", [
            ("hueco", True, 0),
            ("hueco", True, 1),
            ("distractor", False, None),
        ])
        huecos = {e.posicion_hueco: e.id for e in pregunta.elementos.filter(rol="hueco")}

        validador = ValidadorFactory.crear(pregunta)
        self.assertTrue(validador.validar(huecos))
        self.assertFalse(validador.validar({}))
        self.assertFalse(validador.validar({"0": 999}))

    def test_factory_no_registra_abierta_y_rechaza_tipos_desconocidos(self):
        self.assertNotIn("abierta", ValidadorFactory._registro)

        pregunta = self.crear_pregunta("contextual", [("alternativa", True, None)])
        pregunta.tipo = "abierta"
        with self.assertRaises(ValueError):
            ValidadorFactory.crear(pregunta)

        pregunta.tipo = "no_existe"
        with self.assertRaises(ValueError):
            ValidadorFactory.crear(pregunta)