# Script Simple para Iniciar Servidor Flask
# Proyecto Big Data - Universidad Central

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Iniciando Servidor Flask..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Matar procesos en puerto 5001
Write-Host "Liberando puerto 5001..." -ForegroundColor Yellow
$proc = Get-NetTCPConnection -LocalPort 5001 -ErrorAction SilentlyContinue
if ($proc) {
    $proc | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
}
Write-Host "Puerto liberado" -ForegroundColor Green
Write-Host ""

# Iniciar servidor
Write-Host "Iniciando aplicacion..." -ForegroundColor Yellow
Write-Host ""

Start-Process "http://127.0.0.1:5001/documentos"
& ".venv\Scripts\python.exe" app.py
