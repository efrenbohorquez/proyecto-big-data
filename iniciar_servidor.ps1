# Script para iniciar el servidor Flask de forma limpia
# Proyecto Big Data - Universidad Central
# Autor: Efren Bohorquez Vargas

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  SERVIDOR FLASK - PROYECTO BIG DATA" -ForegroundColor Cyan
Write-Host "  Universidad Central - Maestría en Analítica" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Detener procesos Python existentes en el puerto 5001
Write-Host "1. Verificando procesos Python en puerto 5001..." -ForegroundColor Yellow
$connections = netstat -ano | Select-String ":5001" | Select-String "LISTENING"
if ($connections) {
    $pids = $connections | ForEach-Object { 
        ($_ -split '\s+')[-1] 
    } | Select-Object -Unique
    
    foreach ($pid in $pids) {
        try {
            Stop-Process -Id $pid -Force -ErrorAction Stop
            Write-Host "   CheckMark Proceso $pid detenido" -ForegroundColor Green
        } catch {
            Write-Host "   Warning No se pudo detener proceso $pid" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "   CheckMark Puerto 5001 libre" -ForegroundColor Green
}

Start-Sleep -Seconds 2

# Activar entorno virtual
Write-Host ""
Write-Host "2. Activando entorno virtual..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"
Write-Host "   OK Entorno activado" -ForegroundColor Green

Start-Sleep -Seconds 1

# Iniciar servidor
Write-Host ""
Write-Host "3. Iniciando servidor Flask..." -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  SERVIDOR INICIADO" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Accede a las siguientes URLs:" -ForegroundColor White
Write-Host "  - Landing Page:  http://127.0.0.1:5001/" -ForegroundColor Cyan
Write-Host "  - Búsqueda:      http://127.0.0.1:5001/documentos" -ForegroundColor Cyan
Write-Host "  - API Buscar:    http://127.0.0.1:5001/api/buscar" -ForegroundColor Cyan
Write-Host "  - Estadísticas:  http://127.0.0.1:5001/api/estadisticas" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Presiona CTRL+C para detener el servidor" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

# Abrir navegador automáticamente
Start-Process "http://127.0.0.1:5001/documentos"

# Ejecutar aplicación
& python app.py
