# medibook/web/routes.py
"""
Rutas web para servir las vistas HTML del frontend.

Estas rutas renderizan templates Jinja2 que consumen
la API REST existente via JavaScript (fetch).
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="medibook/web/templates")

router = APIRouter(tags=["Web"], include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    """Redirige al login."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/web/login")


@router.get("/web/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Pagina de inicio de sesion."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/web/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard principal (requiere autenticacion en el frontend)."""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "active_page": "dashboard",
    })


@router.get("/web/appointments", response_class=HTMLResponse)
async def appointments_page(request: Request):
    """Vista de citas medicas."""
    return templates.TemplateResponse("appointments.html", {
        "request": request,
        "active_page": "appointments",
    })


@router.get("/web/doctors", response_class=HTMLResponse)
async def doctors_page(request: Request):
    """Vista de doctores."""
    return templates.TemplateResponse("doctors.html", {
        "request": request,
        "active_page": "doctors",
    })


@router.get("/web/patients", response_class=HTMLResponse)
async def patients_page(request: Request):
    """Vista de pacientes."""
    return templates.TemplateResponse("patients.html", {
        "request": request,
        "active_page": "patients",
    })
