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

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

## Uso correcto (IMPORTANTE)

El error que mostraste aparece porque PowerShell interpretó cada parámetro (`--remision-pdf`, `--contrato-pdf`, etc.) como un comando separado.

Debes ejecutar **todo en una sola instrucción**.

### Opción A: una sola línea (PowerShell)

```powershell
python src/autoforms_bot.py --remision-pdf "C:\ruta\REMISION_0106.pdf" --contrato-pdf "C:\ruta\CONTRATO_FIJO.pdf" --headless false --dry-run
```

### Opción B: varias líneas en PowerShell (usar acento grave `)

```powershell
python src/autoforms_bot.py `
  --remision-pdf "C:\ruta\REMISION_0106.pdf" `
  --contrato-pdf "C:\ruta\CONTRATO_FIJO.pdf" `
  --headless false `
  --dry-run
```

> En PowerShell **NO** se usa `\` para continuar línea (eso es de bash). Se usa el backtick: `` ` ``.

### Linux / macOS (sí usa `\`)

```bash
python src/autoforms_bot.py \
  --remision-pdf /ruta/REMISION_0106.pdf \
  --contrato-pdf /ruta/CONTRATO_FIJO.pdf \
  --headless false \
  --dry-run
```


## Login automático

Si APPOLO te redirige a `login.aspx`, ahora el bot puede autenticarse automáticamente.

Puedes pasar credenciales por parámetros:

```powershell
python src/autoforms_bot.py --remision-pdf "C:\ruta\REMISION_0106.pdf" --contrato-pdf "C:\ruta\CONTRATO_FIJO.pdf" --headless false --dry-run --username gcjm --password 'Gcjm123$'
```

> En PowerShell usa comillas simples para contraseñas con `$` (ejemplo: `'Gcjm123$'`).

O por variables de entorno:

```powershell
$env:APPOLO_USER = "gcjm"
$env:APPOLO_PASS = 'Gcjm123$'
python src/autoforms_bot.py --remision-pdf "C:\ruta\REMISION_0106.pdf" --contrato-pdf "C:\ruta\CONTRATO_FIJO.pdf" --headless false --dry-run
```

## Notas importantes

- El portal usa controles ASP.NET dinámicos; los selectores están implementados para el flujo real, pero puede requerir ajuste fino en ambiente productivo.
- Si el usuario ya está autenticado por SSO/sesión, el bot entra directo al formulario.
- Se guarda evidencia en `artifacts/apolo_form_<timestamp>.png`.

## Archivos clave

- `src/autoforms_bot.py`: flujo completo de automatización APPOLO (pasos 1-55).
- `src/remision_parser.py`: extracción automática de datos desde el PDF de Remisión.
