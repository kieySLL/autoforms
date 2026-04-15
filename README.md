# AutoForms Bot (APPOLO - Otras Mercancías)

Automatiza el flujo exacto de **Crear Formulario Otras Mercancías** en APPOLO con el paso a paso que compartiste (1 al 55).

## Qué resuelve

- El archivo **variable** es la **Remisión** (PDF).
- El archivo de **Contrato** es **fijo**.
- El bot:
  1. Abre el formulario.
  2. Hace el flujo de generación y datos del formulario.
  3. Crea **complemento REMISIÓN** y adjunta el PDF variable.
  4. Crea **complemento CONTRATO** y adjunta el PDF fijo.
  5. Guarda y (opcional) aprueba.

## Extracción automática desde Remisión

`src/remision_parser.py` intenta extraer desde el PDF de remisión:

- `numero_complemento_1` (número de remisión, por nombre o texto)
- `contrato` (patrón `CO-xxx-xxxx`)
- `fecha_contrato` (`dd/mm/yyyy`)
- `placa` (patrón `ABC123`)
- `cantidad` (si detecta `Cantidad`)

Si no encuentra algo, usa valores por defecto seguros:

- Contrato: `CO-235-2026`
- Fecha: `11/03/2026`
- Placa: `UEV510`
- Cantidad: `15`

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Uso

```bash
python src/autoforms_bot.py \
  --remision-pdf /ruta/REMISION_0106.pdf \
  --contrato-pdf /ruta/CONTRATO_FIJO.pdf \
  --headless false
```

Para pruebas sin aprobar:

```bash
python src/autoforms_bot.py \
  --remision-pdf /ruta/REMISION_0106.pdf \
  --contrato-pdf /ruta/CONTRATO_FIJO.pdf \
  --headless false \
  --dry-run
```

## Notas importantes

- El portal usa controles ASP.NET dinámicos; los selectores están implementados para el flujo real, pero puede requerir ajuste fino en ambiente productivo.
- Si el usuario ya está autenticado por SSO/sesión, el bot entra directo al formulario.
- Se guarda evidencia en `artifacts/apolo_form_<timestamp>.png`.

## Archivos clave

- `src/autoforms_bot.py`: flujo completo de automatización APPOLO (pasos 1-55).
- `src/remision_parser.py`: extracción automática de datos desde el PDF de Remisión.
