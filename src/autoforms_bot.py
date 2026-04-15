from __future__ import annotations

import argparse
import os
import time
from pathlib import Path
from typing import Callable

from playwright.sync_api import Page, sync_playwright

from remision_parser import parse_remision

BASE_URL = (
    "https://appolozfcayena.gestiontl.co/grupoconstructor/Operaciones/Procesos/"
    "CrearFormularioOtrasMercanc%C3%ADas.aspx"
)

LOGIN_URL_HINT = "login.aspx"



class ApoloFormBot:
    def __init__(self, page: Page, timeout_ms: int = 20_000):
        self.page = page
        self.timeout_ms = timeout_ms

    def click(self, selector: str) -> None:
        self.page.locator(selector).first.click(timeout=self.timeout_ms)

    def fill(self, selector: str, value: str) -> None:
        self.page.locator(selector).first.fill(value, timeout=self.timeout_ms)

    def press_enter(self, selector: str) -> None:
        self.page.locator(selector).first.press("Enter", timeout=self.timeout_ms)

    def click_text(self, text: str) -> None:
        self.page.get_by_text(text, exact=False).first.click(timeout=self.timeout_ms)

    def click_role(self, role: str, name: str) -> None:
        self.page.get_by_role(role, name=name, exact=False).first.click(timeout=self.timeout_ms)

    def attach_file(self, selector: str, file_path: str) -> None:
        self.page.locator(selector).first.set_input_files(file_path, timeout=self.timeout_ms)

    def wait(self, ms: int) -> None:
        self.page.wait_for_timeout(ms)

    def safe_step(self, title: str, fn: Callable[[], None]) -> None:
        try:
            fn()
        except Exception as exc:
            raise RuntimeError(f"Error en paso '{title}': {exc}") from exc

    def is_login_page(self) -> bool:
        return LOGIN_URL_HINT in self.page.url.lower()

    def login_if_needed(self, username: str | None, password: str | None) -> None:
        if not self.is_login_page():
            return
        if not username or not password:
            raise RuntimeError(
                "El portal redirigió al login. Debes pasar --username y --password "
                "(o APPOLO_USER / APPOLO_PASS)."
            )

        user_locator = self.page.locator(
            "input[name*='UserName'], input[id*='UserName'], #UserName, input[type='text']"
        ).first
        pass_locator = self.page.locator(
            "input[name*='Password'], input[id*='Password'], #Password, input[type='password']"
        ).first

        user_locator.fill(username, timeout=self.timeout_ms)
        pass_locator.fill(password, timeout=self.timeout_ms)

        login_button = self.page.locator(
            "input[type='submit'][value*='Login'], button:has-text('Login'), input[name*='LoginButton']"
        ).first
        login_button.click(timeout=self.timeout_ms)
        self.page.wait_for_load_state("domcontentloaded")

    def run(
        self,
        data: dict[str, str],
        contrato_pdf: str,
        dry_run: bool,
        username: str | None,
        password: str | None,
    ) -> None:
        self.page.goto(BASE_URL, wait_until="domcontentloaded")
        self.login_if_needed(username=username, password=password)

        # 1-4 tipo operación
        self.safe_step("Tipo Operación: Ingreso", lambda: self.click("#dnn_ctr17918_DocumentosActivosFijos_ddlTipoOperacion"))
        self.safe_step("Seleccionar Ingreso", lambda: self.click_text("Ingreso"))
        self.safe_step("Generar", lambda: self.click_role("button", "Generar"))

        # 5-10 agregar ítem formulario
        self.safe_step("Agregar ítem", lambda: self.click_role("button", "Agregar"))
        self.safe_step("Descripción", lambda: self.fill("input[name*='txtDescripcion']", data["descripcion_item"]))
        self.safe_step("Cantidad", lambda: self.fill("input[name*='txtCantidad']", data["cantidad"]))
        self.safe_step("Serial", lambda: self.fill("input[name*='txtSerial']", data.get("serial", "")))
        self.safe_step("Guardar ítem", lambda: self.click_role("button", "Guardar"))

        # 11-21 datos adicionales
        self.safe_step("Contrato", lambda: self.fill("input[name*='txtContrato']", data["contrato"]))
        self.safe_step("Fecha contrato", lambda: self.fill("input[name*='dtFechaContrato$dateInput']", data["fecha_contrato"]))
        self.safe_step("Propietario", lambda: self.fill("input[name*='txtPropietarios']", data["propietario"]))
        self.safe_step("Observaciones", lambda: self.fill("textarea[name*='txtObservaciones']", data["observaciones"]))
        self.safe_step("Placa", lambda: self.fill("input[name*='txtPlaca']", data["placa"]))
        self.safe_step("Guardar bloque", lambda: self.click_role("button", "Guardar"))

        # 22-37 complemento 1 REMISION + archivo variable
        self.add_complemento(
            busqueda=data["tipo_complemento_1_busqueda"],
            opcion=data["tipo_complemento_1"],
            numero=data["numero_complemento_1"],
            descripcion=data["descripcion_complemento_1"],
            archivo=data["archivo_remision"],
        )

        # 38-53 complemento 2 CONTRATO + archivo fijo
        self.add_complemento(
            busqueda=data["tipo_complemento_2_busqueda"],
            opcion=data["tipo_complemento_2"],
            numero=data["numero_complemento_2"],
            descripcion=data["descripcion_complemento_2"],
            archivo=str(Path(contrato_pdf).resolve()),
        )

        # 54-55
        self.safe_step("Guardar formulario", lambda: self.click_role("button", "Guardar"))
        if not dry_run:
            self.safe_step("Aprobar", lambda: self.click_role("button", "Aprobar"))

    def add_complemento(
        self,
        busqueda: str,
        opcion: str,
        numero: str,
        descripcion: str,
        archivo: str,
    ) -> None:
        self.safe_step("Agregar complemento", lambda: self.click_role("button", "Agregar"))
        self.safe_step("Abrir búsqueda tipo complemento", lambda: self.click("button[name*='btnF4TipoComplemento']"))
        self.safe_step("Buscar tipo complemento", lambda: self.fill("input[name*='txtParametroBusqueda']", busqueda))
        self.safe_step("Click buscar", lambda: self.click_role("button", "Buscar"))
        self.safe_step("Seleccionar tipo complemento", lambda: self.click_text(opcion))
        self.safe_step("Cerrar popup búsqueda", lambda: self.click_role("button", "Close"))

        self.safe_step("Número complemento", lambda: self.fill("input[name*='txtNumeroComplemento']", numero))
        self.safe_step("Descripción complemento", lambda: self.fill("input[name*='txtDescripcionComplemento']", descripcion))
        self.safe_step("Guardar complemento", lambda: self.click_role("button", "Guardar"))

        self.safe_step("Editar adjunto", lambda: self.click("a[title='Editar'], button[title='Editar']"))
        self.safe_step("Subir archivo", lambda: self.upload_attachment_in_modal(archivo))
        self.safe_step("Cerrar modal datos complemento", lambda: self.click_role("button", "Cerrar"))

    def upload_attachment_in_modal(self, file_path: str) -> None:
        self.attach_file("input[type='file']", file_path)
        self.click_role("button", "Subir")
        self.wait(1200)
        self.click_role("button", "Cerrar")


def run(
    remision_pdf: str,
    contrato_pdf: str,
    headless: bool,
    dry_run: bool,
    username: str | None,
    password: str | None,
) -> Path:
    Path("artifacts").mkdir(exist_ok=True)
    data = parse_remision(remision_pdf)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        bot = ApoloFormBot(page)
        bot.run(
            data=data,
            contrato_pdf=contrato_pdf,
            dry_run=dry_run,
            username=username,
            password=password,
        )

        output = Path(f"artifacts/apolo_form_{int(time.time())}.png")
        page.screenshot(path=str(output), full_page=True)
        browser.close()
        return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Automatiza Crear Formulario Otras Mercancías de APPOLO. "
            "El PDF de Remisión cambia (extrae datos), el contrato es fijo."
        )
    )
    parser.add_argument("--remision-pdf", required=True, help="PDF variable: Remisión")
    parser.add_argument("--contrato-pdf", required=True, help="PDF fijo: contrato")
    parser.add_argument("--headless", default="false", choices=["true", "false"])
    parser.add_argument("--dry-run", action="store_true", help="No da clic en Aprobar")
    parser.add_argument("--username", default=None, help="Usuario APPOLO")
    parser.add_argument("--password", default=None, help="Contraseña APPOLO")

    args = parser.parse_args()
    username = args.username or os.getenv("APPOLO_USER")
    password = args.password or os.getenv("APPOLO_PASS")

    result = run(
        remision_pdf=args.remision_pdf,
        contrato_pdf=args.contrato_pdf,
        headless=args.headless == "true",
        dry_run=args.dry_run,
        username=username,
        password=password,
    )
    print(f"Evidencia guardada en: {result}")
