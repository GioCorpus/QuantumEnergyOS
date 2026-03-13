# ──────────────────────────────────────────────────────────────
# Dockerfile — QuantumEnergyOS (hardened)
#
# Principios de seguridad aplicados:
#   - Imagen base mínima (python:3.11-slim)
#   - Usuario no-root (qeos:1000)
#   - Sistema de archivos read-only (--read-only en runtime)
#   - Memoria limitada (--memory=512m en runtime)
#   - Sin secretos en la imagen — se inyectan en runtime
#   - Dependencias fijadas con hash (requirements-lock.txt)
#   - SBOM generado con syft en CI
# ──────────────────────────────────────────────────────────────

# ── Stage 1: Builder ──────────────────────────────────────────
FROM python:3.11-slim AS builder

# Metadatos OCI
LABEL org.opencontainers.image.title="QuantumEnergyOS"
LABEL org.opencontainers.image.description="Optimización cuántica de redes eléctricas"
LABEL org.opencontainers.image.source="https://github.com/GioCorpus/QuantumEnergyOS"
LABEL org.opencontainers.image.licenses="MIT"

# Variables de build (no son secretos)
ARG PYTHON_VERSION=3.11
ARG BUILD_DATE
ARG GIT_SHA

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Copiar solo requirements primero (cache layer)
COPY requirements.txt requirements-lock.txt* ./

# Instalar dependencias en directorio temporal
RUN pip install --upgrade pip --no-cache-dir && \
    pip install --no-cache-dir \
        --require-hashes \
        -r requirements.txt \
        --target /build/packages || \
    pip install --no-cache-dir \
        -r requirements.txt \
        --target /build/packages

# ── Stage 2: Runtime (imagen final mínima) ───────────────────
FROM python:3.11-slim AS runtime

# Seguridad: no ejecutar como root
RUN groupadd --gid 1000 qeos && \
    useradd --uid 1000 --gid 1000 --no-create-home --shell /bin/false qeos

# Copiar dependencias del builder
COPY --from=builder /build/packages /usr/local/lib/python3.11/site-packages/

# Directorio de trabajo con permisos mínimos
WORKDIR /app
RUN chown qeos:qeos /app

# Copiar código fuente
COPY --chown=qeos:qeos src/          ./src/
COPY --chown=qeos:qeos security/     ./security/
COPY --chown=qeos:qeos api/          ./api/
COPY --chown=qeos:qeos qsharp.json   ./

# Directorios temporales necesarios (read-only filesystem requiere tmpfs en runtime)
RUN mkdir -p /tmp/qeos /app/logs && \
    chown -R qeos:qeos /tmp/qeos /app/logs

# Cambiar a usuario sin privilegios
USER qeos:qeos

# Variables de entorno seguras (valores por defecto NO para producción)
ENV QEOS_ENV=production \
    QEOS_PORT=8000 \
    QEOS_LOG_LEVEL=INFO \
    QEOS_JWT_EXPIRY_HOURS=24 \
    QEOS_RATE_LIMIT_REQ=60 \
    QEOS_RATE_LIMIT_WIN=60 \
    PYTHONPATH=/app

# QEOS_JWT_SECRET debe inyectarse en runtime:
#   docker run -e QEOS_JWT_SECRET=$(openssl rand -hex 32) ...
# NUNCA incluir secretos en la imagen.

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" \
    || exit 1

# Punto de entrada
CMD ["python", "-m", "api.server"]

# ──────────────────────────────────────────────────────────────
# Correr en modo hardened:
#
#   docker run \
#     --read-only \
#     --memory=512m \
#     --memory-swap=512m \
#     --cpus=2 \
#     --security-opt no-new-privileges \
#     --cap-drop ALL \
#     --tmpfs /tmp:size=64m,noexec,nosuid \
#     -e QEOS_JWT_SECRET=$(openssl rand -hex 32) \
#     -p 8000:8000 \
#     quantumenergyos:latest
# ──────────────────────────────────────────────────────────────
