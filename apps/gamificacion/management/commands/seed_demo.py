import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from apps.users.models import Usuario, PerfilDocente, PerfilEstudiante
from apps.academico.models import Etapa, Tema, Seccion, ProgresoTema
from apps.preguntas.models import Pregunta, ElementoPregunta
from apps.intentos.models import IntentoTema, RespuestaEstudiante


class Command(BaseCommand):
    help = "Crea datos de prueba: 1 docente, 1 sección, 5 estudiantes, preguntas e intentos resueltos."

    def handle(self, *args, **kwargs):
        docente, _ = Usuario.objects.get_or_create(
            username="docente_demo", defaults={"rol": "docente"}
        )
        docente.set_password("demo1234")
        docente.rol = "docente"
        docente.save()
        PerfilDocente.objects.get_or_create(usuario=docente)

        etapa, _ = Etapa.objects.get_or_create(titulo="Etapa 1: Biología como Ciencia", orden=1)
        tema, _ = Tema.objects.get_or_create(etapa=etapa, titulo="Concepto", orden=1)

        preguntas = []
        for i in range(5):
            p, _ = Pregunta.objects.get_or_create(
                tema=tema, enunciado=f"Pregunta demo {i+1}: ¿Qué estudia la Biología?",
                defaults={"tipo": "contextual", "creado_por": docente}
            )
            correcta, _ = ElementoPregunta.objects.get_or_create(
                pregunta=p, rol="alternativa", contenido="La vida", defaults={"es_correcto": True, "orden": 1}
            )
            preguntas.append((p, correcta))

        seccion, _ = Seccion.objects.get_or_create(nombre="3ro A Biología", docente=docente)

        nombres = ["Juan Perez", "Maria Garcia", "Carlos Ruiz", "Sandra Lopez", "Pedro Vera"]
        estudiantes_perfiles = []

        for idx, nombre in enumerate(nombres):
            username = f"estudiante_demo_{idx+1}"
            usuario, _ = Usuario.objects.get_or_create(
                username=username,
                defaults={"rol": "estudiante", "first_name": nombre.split()[0], "last_name": nombre.split()[1]},
            )
            usuario.set_password("demo1234")
            usuario.save()
            perfil, _ = PerfilEstudiante.objects.get_or_create(usuario=usuario)
            seccion.estudiantes.add(perfil)
            estudiantes_perfiles.append(perfil)

            ProgresoTema.objects.get_or_create(
                estudiante=perfil, tema=tema, defaults={"desbloqueado": True}
            )

        for perfil in estudiantes_perfiles:
            for dias_atras in [150, 120, 90, 60, 30, 5]:
                fecha = timezone.now() - timedelta(days=dias_atras)
                intento = IntentoTema.objects.create(
                    estudiante=perfil, tema=tema, vidas_restantes=random.randint(2, 5), completado=True
                )
                intento.iniciado = fecha
                intento.finalizado = fecha
                intento.save()

                for pregunta, correcta in preguntas:
                    es_correcta = random.random() < (0.5 + dias_atras * -0.002)
                    RespuestaEstudiante.objects.create(
                        intento=intento, pregunta=pregunta, es_correcta=es_correcta,
                        payload={"alternativa_id": correcta.id if es_correcta else 999},
                        tiempo_respuesta_ms=random.randint(3000, 15000),
                        creado=fecha,
                    )

        self.stdout.write(self.style.SUCCESS(
            f"Listo: docente_demo/demo1234, sección '{seccion.nombre}' (id={seccion.id}), "
            f"tema '{tema.titulo}' (id={tema.id}), 5 estudiantes creados."
        ))
