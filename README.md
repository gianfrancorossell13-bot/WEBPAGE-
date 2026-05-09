# Guardian Ciudadano Peru

Proyecto web para el curso de Arquitectura de Aplicaciones.

La solucion centraliza informacion de delitos en Lima Metropolitana y Callao, y ahora incorpora una plataforma con autenticacion, base de datos de usuarios, controles de seguridad y evidencia de arquitectura segura.

## Arquitectura

```text
Usuario autenticado
  -> Frontend React/Vite
  -> Cliente API centralizado
  -> FastAPI
  -> Servicios de negocio
  -> Repositorios
  -> SQLite
```

### Principios aplicados del curso

- Seguridad como requisito no funcional: el dashboard ya no es publico; requiere login.
- Layering: UI, API, servicios, repositorios y base de datos estan separados.
- Minimo privilegio: los endpoints de analitica requieren token activo.
- Fail-safe defaults: sin token valido, la API responde 401.
- Mediacion completa: cada request protegido valida token, usuario y estado activo.
- Separacion de responsabilidades: autenticacion, analitica, persistencia y presentacion estan en modulos distintos.
- Auditoria: los intentos de login se registran en `audit_logs`.
- Registro verificado: el alta de usuarios requiere un codigo temporal de 6 digitos.
- CI/CD: se incluye workflow de GitHub Actions con compilacion, build frontend y Bandit SAST.

## Tecnologias usadas

- Frontend: React + Vite
- Backend: Python + FastAPI
- Base de datos: SQLite para el MVP academico
- Graficos: Recharts
- Mapa: Leaflet + OpenStreetMap
- Seguridad: hash PBKDF2 + salt, token firmado con expiracion, cabeceras HTTP seguras
- Email: SMTP opcional para enviar codigos de verificacion

## Usuario academico

La aplicacion crea automaticamente un usuario inicial si no existe:

```text
Correo: analista@guardian.pe
Contrasena: Guardian2026!
Rol: admin
```

Puedes cambiarlo con variables de entorno antes de iniciar el backend:

```powershell
$env:GUARDIAN_ADMIN_EMAIL="tu-correo@dominio.com"
$env:GUARDIAN_ADMIN_PASSWORD="TuPassword2026!"
$env:GUARDIAN_TOKEN_KEY="clave-larga-y-privada"
```

Tambien puedes copiar `backend/.env.example` como referencia de configuracion.

## Registro con codigo por correo

La pantalla de acceso permite crear una cuenta nueva. El flujo es:

1. Ingresa nombre, correo y contrasena.
2. La API genera un codigo de 6 digitos.
3. Si SMTP esta configurado, el codigo llega al correo.
4. Ingresas el codigo y la cuenta queda creada con rol `analista`.

Para envio real de correo configura estas variables antes de iniciar el backend:

```powershell
$env:GUARDIAN_SMTP_HOST="smtp.gmail.com"
$env:GUARDIAN_SMTP_PORT="587"
$env:GUARDIAN_SMTP_USER="tu-correo@gmail.com"
$env:GUARDIAN_SMTP_PASSWORD="tu-app-password"
$env:GUARDIAN_EMAIL_FROM="tu-correo@gmail.com"
```

El proyecto ya incluye `backend/.env`; completa ahi los valores de Gmail para no escribirlos cada vez.

En Gmail debes usar una App Password, no tu contrasena normal.

Para pruebas locales sin SMTP puedes activar temporalmente:

```powershell
$env:GUARDIAN_DEV_EMAIL_CODES="true"
```

Con ese modo, la API muestra el codigo de desarrollo en la respuesta y tambien lo escribe en logs. Para usar Gmail o produccion debe estar en `false`.

## Ejecutar backend

Abre una terminal en VS Code:

```bash
cd backend
python -m venv .venv
```

En Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Instala dependencias:

```bash
pip install -r requirements.txt
```

Ejecuta el servidor:

```bash
uvicorn app.main:app --reload
```

La API estara en:

```text
http://127.0.0.1:8000
```

La documentacion automatica estara en:

```text
http://127.0.0.1:8000/docs
```

## Ejecutar frontend

Abre otra terminal en VS Code:

```bash
cd frontend
npm install
npm run dev
```

La web estara en:

```text
http://localhost:5173
```

## Verificaciones recomendadas

Backend:

```bash
python -m compileall app
```

Frontend:

```bash
npm run build
```

Smoke test de login:

```powershell
$body = @{ email = "analista@guardian.pe"; password = "Guardian2026!" } | ConvertTo-Json
$session = Invoke-RestMethod http://127.0.0.1:8000/api/auth/login -Method Post -ContentType "application/json" -Body $body
Invoke-RestMethod http://127.0.0.1:8000/api/resumen -Headers @{ Authorization = "Bearer $($session.access_token)" }
```

Smoke test de registro sin SMTP solo para modo desarrollo:

Antes de ejecutarlo activa temporalmente `GUARDIAN_DEV_EMAIL_CODES=true` en `backend/.env`.

```powershell
$email = "nuevo$([int](Get-Random -Maximum 999999))@guardian.pe"
$registro = @{
  nombre = "Nuevo Analista"
  email = $email
  password = "Nuevo2026!"
} | ConvertTo-Json
$pendiente = Invoke-RestMethod http://127.0.0.1:8000/api/auth/register/request -Method Post -ContentType "application/json" -Body $registro
$verificacion = @{
  email = $email
  codigo = $pendiente.codigo_dev
} | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8000/api/auth/register/verify -Method Post -ContentType "application/json" -Body $verificacion
```

## Mejoras futuras

- Reemplazar SQLite por PostgreSQL + PostGIS.
- Agregar gestion de usuarios desde el frontend.
- Integrar DAST con OWASP ZAP en el pipeline.
- Exportar reportes en PDF o Excel.
- Agregar monitoreo de errores y metricas de disponibilidad.
