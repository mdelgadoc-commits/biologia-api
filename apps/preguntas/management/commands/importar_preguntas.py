"""Importa tripletas (preguntas con sus elementos) desde un JSON.

Formato esperado:

{
  "etapas": [
    {
      "titulo": "El cuerpo humano",
      "orden": 1,
      "temas": [
        {
          "titulo": "El corazón",
          "orden": 1,
          "icono": "corazon",
          "tema_previo": "La sangre",   // título del tema previo (misma etapa, opcional)
          "preguntas": [
            {
              "tipo": "contextual",     // contextual | inferencial | vf_premisas | cuantas_correctas | completar
              "enunciado": "¿Qué órgano bombea la sangre?",
              "dificultad": 1,
              "elementos": [
                {"rol": "alternativa", "contenido": "Corazón", "es_correcto": true, "orden": 0},
                {"rol": "alternativa", "contenido": "Pulmón", "es_correcto": false, "orden": 1}
              ]
            }
          ]
        }
      ]
    }
  ]
}

Ejemplo de uso:
    python manage.py importar_preguntas tripletas.json --docente docente_demo
    python manage.py importar_preguntas tripletas.json --borrar-antes
"""
import json

from django.core.management.base import BaseCommand, CommandError

from apps.academico.models import Etapa, Tema
from apps.preguntas.models import ElementoPregunta, Pregunta, TipoPregunta
from apps.users.models import Usuario

TIPOS_IMPORTABLES = {
    choice[0] for choice in TipoPregunta.choices if choice[0] != "abierta"
}
ROLES_VALIDOS = {choice[0] for choice in ElementoPregunta.Rol.choices}


class Command(BaseCommand):
    help = "Carga tripletas (preguntas + elementos) desde un archivo JSON."

    def add_arguments(self, parser):
        parser.add_argument("archivo", type=str, help="ruta al JSON de contenido")
        parser.add_argument(
            "--docente", type=str,
            help="username del docente que aparece como creador de las preguntas",
        )
        parser.add_argument(
            "--borrar-antes", action="store_true",
            help="borra etapas/temas/preguntas existentes antes de importar",
        )

    def handle(self, *args, **options):
        with open(options["archivo"], encoding="utf-8") as f:
            data = json.load(f)

        creador = self._resolver_creador(options.get("docente"))

        if options["borrar_antes"]:
            ElementoPregunta.objects.all().delete()
            Pregunta.objects.all().delete()
            Tema.objects.all().delete()
            Etapa.objects.all().delete()
            self.stdout.write("Contenido previo eliminado.")

        contadores = {"etapas": 0, "temas": 0, "preguntas": 0, "elementos": 0}

        for index_etapa, dato_etapa in enumerate(data.get("etapas", []), start=1):
            contadores["etapas"] += 1
            etapa, _ = Etapa.objects.get_or_create(
                titulo=dato_etapa["titulo"],
                defaults={"orden": dato_etapa.get("orden", index_etapa)},
            )
            if "orden" in dato_etapa and etapa.orden != dato_etapa["orden"]:
                etapa.orden = dato_etapa["orden"]
                etapa.save()

            temas = dato_etapa.get("temas", [])
            creados = {}
            for index_tema, dato_tema in enumerate(temas, start=1):
                tema, _ = Tema.objects.get_or_create(
                    etapa=etapa, titulo=dato_tema["titulo"],
                    defaults={"orden": dato_tema.get("orden", index_tema)},
                )
                if "orden" in dato_tema and tema.orden != dato_tema["orden"]:
                    tema.orden = dato_tema["orden"]
                if "icono" in dato_tema:
                    tema.icono = dato_tema.get("icono", "")
                tema.save()
                creados[dato_tema["titulo"]] = tema
                contadores["temas"] += 1

            # Segundo pase: enlazar tema_previo por título (misma etapa).
            for dato_tema in temas:
                previo = dato_tema.get("tema_previo")
                if previo:
                    if previo not in creados:
                        raise CommandError(
                            f"Etapa '{dato_etapa['titulo']}': tema_previo '{previo}' "
                            f"no existe dentro de la misma etapa."
                        )
                    creados[dato_tema["titulo"]].tema_previo = creados[previo]
                    creados[dato_tema["titulo"]].save(update_fields=["tema_previo"])

            for dato_tema in temas:
                tema = creados[dato_tema["titulo"]]
                for index_pregunta, dato_pregunta in enumerate(dato_tema.get("preguntas", []), start=1):
                    camino = (
                        f"Etapa '{dato_etapa['titulo']}' > Tema '{dato_tema['titulo']}' "
                        f"> Pregunta {index_pregunta}"
                    )
                    self._validar_pregunta(dato_pregunta, camino)
                    pregunta = Pregunta.objects.create(
                        tema=tema,
                        tipo=dato_pregunta["tipo"],
                        enunciado=dato_pregunta["enunciado"],
                        dificultad=dato_pregunta.get("dificultad", 1),
                        creado_por=creador,
                        activa=dato_pregunta.get("activa", True),
                    )
                    for i, elemento in enumerate(dato_pregunta.get("elementos", [])):
                        ElementoPregunta.objects.create(
                            pregunta=pregunta,
                            rol=elemento["rol"],
                            contenido=elemento["contenido"],
                            es_correcto=elemento.get("es_correcto", False),
                            orden=elemento.get("orden", i),
                            posicion_hueco=elemento.get("posicion_hueco"),
                        )
                        contadores["elementos"] += 1
                    contadores["preguntas"] += 1

        self.stdout.write(self.style.SUCCESS(
            f"Importación completa: {contadores['etapas']} etapas, "
            f"{contadores['temas']} temas, {contadores['preguntas']} preguntas, "
            f"{contadores['elementos']} elementos."
        ))

    def _resolver_creador(self, username):
        if not username:
            return None
        creador = Usuario.objects.filter(username=username).first()
        if not creador:
            raise CommandError(f"No existe un usuario con username '{username}'.")
        if creador.rol != Usuario.Rol.DOCENTE:
            raise CommandError(f"'{username}' no tiene rol docente.")
        return creador

    def _validar_pregunta(self, dato, camino):
        tipo = dato.get("tipo")
        if tipo not in TIPOS_IMPORTABLES:
            raise CommandError(
                f"{camino}: tipo '{tipo}' inválido. Tipos permitidos: "
                f"{', '.join(sorted(TIPOS_IMPORTABLES))}."
            )

        elementos = dato.get("elementos", [])
        if not elementos:
            raise CommandError(f"{camino}: debe incluir al menos un elemento.")

        for i, e in enumerate(elementos):
            if e.get("rol") not in ROLES_VALIDOS:
                raise CommandError(
                    f"{camino} > elemento {i}: rol '{e.get('rol')}' inválido."
                )

        if tipo in ("contextual", "inferencial"):
            correctas = [e for e in elementos if e.get("rol") == "alternativa" and e.get("es_correcto")]
            if len(correctas) != 1:
                raise CommandError(
                    f"{camino}: debe haber exactamente una alternativa correcta "
                    f"(rol 'alternativa', es_correcto true)."
                )

        if tipo in ("vf_premisas", "cuantas_correctas"):
            premisas = [e for e in elementos if e.get("rol") == "premisa"]
            if not premisas:
                raise CommandError(f"{camino}: requiere al menos una premisa (rol 'premisa').")
            if any(e.get("es_correcto") is None for e in premisas):
                raise CommandError(f"{camino}: cada premisa debe indicar es_correcto (true/false).")
            if tipo == "cuantas_correctas" and not any(e.get("es_correcto") for e in premisas):
                raise CommandError(f"{camino}: al menos una premisa debe ser verdadera.")

        if tipo == "completar":
            huecos = [e for e in elementos if e.get("rol") == "hueco"]
            if not huecos:
                raise CommandError(f"{camino}: requiere al menos un hueco (rol 'hueco').")
            posiciones = [h.get("posicion_hueco") for h in huecos]
            if any(p is None for p in posiciones):
                raise CommandError(f"{camino}: cada hueco necesita 'posicion_hueco'.")
            if len(posiciones) != len(set(posiciones)):
                raise CommandError(f"{camino}: las posiciones de hueco no pueden repetirse.")