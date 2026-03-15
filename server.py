"""
api/server.py — QuantumEnergyOS REST API
─────────────────────────────────────────
Backend FastAPI que expone los módulos de simulación cuántica como endpoints HTTP.

Endpoints:
  POST /api/v1/cooling          → Simula enfriamiento criogénico de qubits
  POST /api/v1/grid/balance     → Optimización QAOA de red eléctrica
  POST /api/v1/fusion/simulate  → Simulación D-T y potencia estimada
  POST /api/v1/braiding/debug   → Benchmark de fidelidad topológica
  GET  /api/v1/status           → Health check del sistema

Ejecutar:
  uvicorn api.server:app --reload --port 8000

Autor: GioCorpus — QuantumEnergyOS, Mexicali, B.C.
"""

from __future__ import annotations

import hashlib
import logging
import os
import random
import time
from dataclasses import dataclass, field
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("qeos.api")

# ── Constantes ────────────────────────────────────────────────────────────────
VERSION = "0.4.0"
MAX_QUBITS  = 16       # Límite seguro para simulación clásica en servidor
MAX_SHOTS   = 10_000   # Evitar DoS por shots exagerados
MAX_NODES   = 8        # Nodos de red eléctrica simulados

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="QuantumEnergyOS API",
    description=(
        "Simulación cuántica para optimización de redes eléctricas, "
        "fusión nuclear D-T y qubits topológicos Majorana. "
        "Desde Mexicali, Baja California — para el mundo."
    ),
    version=VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # En producción: restringir a tu dominio
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ── Modelos de entrada ────────────────────────────────────────────────────────

class SolicitudCooling(BaseModel):
    """Parámetros para simulación de enfriamiento criogénico."""
    n_qubits: int = Field(
        default=8,
        ge=1,
        le=MAX_QUBITS,
        description="Número de qubits a enfriar (1–16)",
    )
    ciclos_braiding: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Ciclos de braiding protector por qubit",
    )

    @field_validator("n_qubits")
    @classmethod
    def validar_qubits(cls, v: int) -> int:
        if v > MAX_QUBITS:
            raise ValueError(f"n_qubits no puede superar {MAX_QUBITS}")
        return v


class SolicitudGrid(BaseModel):
    """Parámetros para balanceo de red eléctrica."""
    n_nodos: int = Field(
        default=4,
        ge=2,
        le=MAX_NODES,
        description="Número de nodos de la red (2–8)",
    )
    shots: int = Field(
        default=100,
        ge=1,
        le=MAX_SHOTS,
        description="Shots del circuito QAOA",
    )
    gamma: float = Field(
        default=0.4,
        ge=0.0,
        le=3.14159,
        description="Parámetro gamma del operador de costo",
    )
    beta: float = Field(
        default=0.7,
        ge=0.0,
        le=3.14159,
        description="Parámetro beta del operador de mezcla",
    )


class SolicitudFusion(BaseModel):
    """Parámetros del reactor D-T para simulación de fusión."""
    temperatura_kev: float = Field(
        default=65.0,
        ge=10.0,
        le=200.0,
        description="Temperatura del plasma en keV (10–200)",
    )
    densidad_n20: float = Field(
        default=1.5,
        ge=0.1,
        le=10.0,
        description="Densidad del plasma en 10^20 m⁻³",
    )
    tiempo_conf_seg: float = Field(
        default=3.0,
        ge=0.1,
        le=100.0,
        description="Tiempo de confinamiento en segundos",
    )
    n_precision: int = Field(
        default=4,
        ge=2,
        le=8,
        description="Qubits de precisión para QPE (2–8)",
    )


class SolicitudBraiding(BaseModel):
    """Parámetros para benchmark de qubits topológicos."""
    n_shots: int = Field(
        default=200,
        ge=10,
        le=MAX_SHOTS,
        description="Shots para benchmark de fidelidad",
    )
    verificar_paridad: bool = Field(
        default=True,
        description="Incluir verificación de paridad fermiónica",
    )

# ── Lógica de simulación (Python, compatible con el Q# conceptual) ────────────

def simular_cooling(n_qubits: int, ciclos: int) -> dict[str, Any]:
    """
    Simula el protocolo de enfriamiento criogénico.
    En producción: delegar a Q# via qsharp.run().
    """
    resultados_qubits = []
    enfriados = 0

    for i in range(n_qubits):
        # Simular probabilidad de éxito según ciclos de braiding
        # Más ciclos → mayor protección topológica → mayor tasa de éxito
        prob_exito = 1.0 - (0.15 * (0.9 ** ciclos))
        exito = random.random() < prob_exito

        temp_inicial_k = 300.0 + random.uniform(-20, 50)   # Desierto de B.C.
        temp_final_k   = 4.0 + random.uniform(0, 2)        # Criogenia real

        if exito:
            enfriados += 1

        resultados_qubits.append({
            "id":            i,
            "estado":        "4K_operacional" if exito else "ruido_termico",
            "temp_inicial_k": round(temp_inicial_k, 2),
            "temp_final_k":   round(temp_final_k, 2),
            "exito":         exito,
        })

    return {
        "n_qubits":       n_qubits,
        "enfriados":      enfriados,
        "tasa_exito_pct": round(enfriados / n_qubits * 100, 1),
        "ciclos_braiding": ciclos,
        "qubits":         resultados_qubits,
        "mensaje":        (
            f"{enfriados}/{n_qubits} qubits operacionales. "
            "El desierto no gana hoy — el crióstato dice gracias."
        ),
    }


def simular_grid(n_nodos: int, shots: int, gamma: float, beta: float) -> dict[str, Any]:
    """
    Simula el balanceo QAOA de red eléctrica.
    """
    COSTO_BASE_KW = 150.0  # kW de desperdicio por nodo en sobrecarga

    mejor_config  = None
    mejor_costo   = float("inf")
    historial     = []

    for shot in range(shots):
        # Circuito QAOA simulado: probabilidad de sobrecarga ∝ gamma, beta
        config = []
        for nodo in range(n_nodos):
            # Probabilidad de sobrecarga influenciada por parámetros QAOA
            p_sobrecarga = 0.3 * (1 - beta / 3.14159) * (1 + gamma / 3.14159) / 2
            p_sobrecarga = max(0.05, min(0.8, p_sobrecarga))
            config.append(1 if random.random() < p_sobrecarga else 0)

        # Calcular costo de la configuración
        costo = sum(COSTO_BASE_KW for c in config if c == 1)
        # Penalización cascada para nodos adyacentes en sobrecarga
        for i in range(n_nodos - 1):
            if config[i] == 1 and config[i + 1] == 1:
                costo += COSTO_BASE_KW * 0.533

        if costo < mejor_costo:
            mejor_costo  = costo
            mejor_config = config[:]

        if shot % (shots // 10) == 0:
            historial.append({"shot": shot, "mejor_costo_kw": round(mejor_costo, 2)})

    n_sobrecargas    = sum(mejor_config)
    ahorro_vs_peor   = (n_nodos * COSTO_BASE_KW * 1.5) - mejor_costo
    ahorro_pct       = round(ahorro_vs_peor / (n_nodos * COSTO_BASE_KW * 1.5) * 100, 1)

    return {
        "n_nodos":         n_nodos,
        "shots":           shots,
        "gamma":           gamma,
        "beta":            beta,
        "mejor_config":    mejor_config,
        "nodos_sobrecarga": n_sobrecargas,
        "desperdicio_kw":  round(mejor_costo, 2),
        "ahorro_pct":      ahorro_pct,
        "historial":       historial,
        "mensaje": (
            f"Red de {n_nodos} nodos balanceada en {shots} shots. "
            f"Ahorro estimado: {ahorro_pct}% vs configuración no optimizada."
        ),
    }


def simular_fusion(
    temp_kev: float,
    densidad_n20: float,
    tiempo_conf: float,
    n_precision: int,
) -> dict[str, Any]:
    """
    Simula la estimación de potencia del reactor D-T.
    """
    SECCION_EFICAZ_PEAK = 5.0e-28   # m²
    ENERGIA_DT_J        = 2.818e-12  # J — 17.6 MeV
    LAWSON              = 3.0e21     # m⁻³·s

    # Eficiencia cuántica (QPE simplificado)
    # Pico real D-T: ~65 keV → modelar como gaussiana
    eficiencia_qpe = 0.85 * (-(( (temp_kev - 65.0) / 40.0 ) ** 2))
    eficiencia_qpe = max(0.05, abs(eficiencia_qpe) + random.uniform(0, 0.15))
    eficiencia_qpe = min(1.0, eficiencia_qpe)

    # Física del reactor
    seccion_eficaz   = SECCION_EFICAZ_PEAK * eficiencia_qpe
    densidad         = densidad_n20 * 1.0e20
    velocidad_termica = 1.0e6 * (temp_kev / 65.0) ** 0.5
    tasa_reaccion    = densidad ** 2 * seccion_eficaz * velocidad_termica
    potencia_w       = tasa_reaccion * ENERGIA_DT_J * 800.0  # volumen 800 m³
    potencia_mw      = potencia_w / 1.0e6

    factor_lawson    = densidad * tiempo_conf / LAWSON
    potencia_neta_mw = potencia_mw * factor_lawson - (15.0 / max(0.01, factor_lawson))

    ignicion         = potencia_neta_mw >= 500.0
    criterio_lawson  = factor_lawson >= 1.0

    return {
        "temperatura_kev":      temp_kev,
        "densidad_n20":         densidad_n20,
        "tiempo_conf_seg":      tiempo_conf,
        "n_precision_qpe":      n_precision,
        "eficiencia_qpe":       round(eficiencia_qpe, 4),
        "factor_lawson":        round(factor_lawson, 4),
        "criterio_lawson_ok":   criterio_lawson,
        "potencia_bruta_mw":    round(potencia_mw, 2),
        "potencia_neta_mw":     round(potencia_neta_mw, 2),
        "ignicion_alcanzada":   ignicion,
        "mensaje": (
            "🔥 ¡Ignición! Potencia suficiente para la red del noroeste."
            if ignicion else
            f"Potencia neta: {round(potencia_neta_mw, 1)} MW. "
            "Aumentar densidad o tiempo de confinamiento para alcanzar 500 MW."
        ),
    }


def simular_braiding(n_shots: int, verificar_paridad: bool) -> dict[str, Any]:
    """
    Simula el benchmark de fidelidad topológica.
    """
    # Fidelidad base: qubits topológicos tienen ~99%+ en simulación ideal
    fidelidad_base = 0.97
    ruido          = random.gauss(0, 0.015)
    fidelidad      = max(0.0, min(1.0, fidelidad_base + ruido))

    coincidencias  = int(fidelidad * n_shots)
    exitoso        = fidelidad > 0.95

    # Tasa de error de fase
    tasa_error_fase = max(0.0, random.gauss(0.02, 0.005))

    # Verificación de paridad
    paridad_ok = None
    if verificar_paridad:
        paridad_ok = random.random() > 0.03  # 97% de éxito en paridad

    return {
        "n_shots":           n_shots,
        "coincidencias":     coincidencias,
        "fidelidad_pct":     round(fidelidad * 100, 2),
        "exitoso":           exitoso,
        "tasa_error_fase_pct": round(tasa_error_fase * 100, 3),
        "paridad_ok":        paridad_ok,
        "estado_sistema":    "OPERACIONAL" if exitoso else "REQUIERE_CALIBRACION",
        "mensaje": (
            f"✓ Fidelidad topológica: {round(fidelidad * 100, 1)}% — "
            "Qubits Majorana operacionales. La topología protege."
            if exitoso else
            f"⚠ Fidelidad baja ({round(fidelidad * 100, 1)}%) — "
            "Revisar temperatura del crióstato y alineación del campo magnético."
        ),
    }

# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/api/v1/status")
async def health_check() -> dict[str, Any]:
    """Health check del sistema QuantumEnergyOS."""
    return {
        "status":   "operational",
        "version":  VERSION,
        "origen":   "Mexicali, Baja California — QuantumEnergyOS",
        "modulos":  ["cooling", "grid", "fusion", "braiding"],
        "timestamp": time.time(),
    }


@app.post("/api/v1/cooling")
async def endpoint_cooling(solicitud: SolicitudCooling) -> dict[str, Any]:
    """
    Simula enfriamiento criogénico de qubits Majorana.
    Reduce temperatura lógica de 300 K (desierto) a 4 K (operacional).
    """
    logger.info(f"Cooling: {solicitud.n_qubits} qubits, {solicitud.ciclos_braiding} ciclos")
    t0 = time.perf_counter()

    try:
        resultado = simular_cooling(solicitud.n_qubits, solicitud.ciclos_braiding)
    except Exception as exc:
        logger.error(f"Error en cooling: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en simulación de cooling: {exc}",
        )

    resultado["latencia_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    return resultado


@app.post("/api/v1/grid/balance")
async def endpoint_grid(solicitud: SolicitudGrid) -> dict[str, Any]:
    """
    Optimización QAOA de red eléctrica.
    Minimiza energía desperdiciada por configuraciones de sobrecarga.
    """
    logger.info(f"Grid: {solicitud.n_nodos} nodos, {solicitud.shots} shots")
    t0 = time.perf_counter()

    try:
        resultado = simular_grid(
            solicitud.n_nodos,
            solicitud.shots,
            solicitud.gamma,
            solicitud.beta,
        )
    except Exception as exc:
        logger.error(f"Error en grid balance: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en simulación de red: {exc}",
        )

    resultado["latencia_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    return resultado


@app.post("/api/v1/fusion/simulate")
async def endpoint_fusion(solicitud: SolicitudFusion) -> dict[str, Any]:
    """
    Simula reactor de fusión D-T asistido por QPE cuántico.
    Objetivo: 500 MW para la red eléctrica del noroeste de México.
    """
    logger.info(f"Fusion: T={solicitud.temperatura_kev} keV, n={solicitud.densidad_n20}e20 m⁻³")
    t0 = time.perf_counter()

    try:
        resultado = simular_fusion(
            solicitud.temperatura_kev,
            solicitud.densidad_n20,
            solicitud.tiempo_conf_seg,
            solicitud.n_precision,
        )
    except Exception as exc:
        logger.error(f"Error en fusión: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en simulación de fusión: {exc}",
        )

    resultado["latencia_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    return resultado


@app.post("/api/v1/braiding/debug")
async def endpoint_braiding(solicitud: SolicitudBraiding) -> dict[str, Any]:
    """
    Benchmark de fidelidad de operaciones topológicas (braiding Majorana).
    Incluye verificación de paridad fermiónica y detección de errores de fase.
    """
    logger.info(f"Braiding: {solicitud.n_shots} shots, paridad={solicitud.verificar_paridad}")
    t0 = time.perf_counter()

    try:
        resultado = simular_braiding(solicitud.n_shots, solicitud.verificar_paridad)
    except Exception as exc:
        logger.error(f"Error en braiding: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en benchmark de braiding: {exc}",
        )

    resultado["latencia_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    return resultado


# ── Manejo de errores globales ────────────────────────────────────────────────

@app.exception_handler(Exception)
async def manejador_global(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Error no manejado en {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Error interno del servidor", "detalle": str(exc)},
    )
