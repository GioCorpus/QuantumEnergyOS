# Security Policy

## Supported Versions
We support the latest stable release.

## Reporting a Vulnerability
Please report vulnerabilities privately to:

security@quantumenergyos.org

Do NOT open public issues for security problems.

import os
from qiskit_ibm_runtime import QiskitRuntimeService

token = os.getenv("IBM_QUANTUM_TOKEN")
service = QiskitRuntimeService(token=token)

export IBM_QUANTUM_TOKEN="TU_TOKEN"

QuantumCircuit(1000)

MAX_QUBITS = 32
if n_qubits > MAX_QUBITS:
    raise ValueError("Too many qubits")

    pip-audit
safety
bandit

pip install pip-audit
pip-audit

name: Security Scan

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install tools
        run: |
          pip install pip-audit bandit
      - name: Dependency scan
        run: pip-audit
      - name: Static security scan
        run: bandit -r .
        pip install pip-audit
pip-audit --fix -r requirements.txt

# Opción 2: instalar requirements actualizados directamente
pip install -r requirements.txt --upgrade

# Verificar que quedó limpio
pip-audit -r requirements.txt

RUN pip install qiskit qiskit-aer

WORKDIR /app
COPY . .

CMD ["python", "main.py"]

docker run --memory=4g --cpus=2 quantumenergyos

def validate_circuit(circuit):
    if circuit.num_qubits > 32:
        raise Exception("Too many qubits")

        import hashlib

hash = hashlib.sha256(str(circuit).encode()).hexdigest()

QuantumEnergyOS
│
├── quantum/
│   ├── circuits
│   ├── algorithms
│   └── simulators
│
├── security/
│   ├── input_validation
│   ├── credential_manager
│   └── sandbox
│
├── cloud/
│   └── ibm_quantum
│
├── logs/
└── api/

SECURITY.md
CODE_OF_CONDUCT.md
CONTRIBUTING.md

# Security Policy

## Reporting a Vulnerability

Please report vulnerabilities privately via email.

security@quantumenergyos.org

# 🔐 Security Policy — QuantumEnergyOS

## Versiones soportadas

| Versión | Soporte de seguridad |
|---------|----------------------|
| `main`  | ✅ Activo            |
| < 1.0   | ❌ No soportado      |

## Reportar una vulnerabilidad

**No abras un Issue público para vulnerabilidades de seguridad.**

Envía un reporte privado a través de:
- GitHub Security Advisories: **Settings → Security → Advisories → New advisory**
- O por correo a: `security@[tu-dominio]` (PGP disponible bajo petición)

Incluye:
1. Descripción del problema
2. Pasos para reproducir
3. Impacto potencial
4. Versión afectada

Responderemos en **72 horas**. Si se confirma, publicaremos un CVE y fix en ≤ 14 días.

## Modelo de amenazas

QuantumEnergyOS opera con las siguientes superficies de ataque en mente:

| Superficie | Mitigación |
|---|---|
| Input de circuitos cuánticos | Validación con Pydantic + límite `max_qubits=32` |
| API REST | JWT + rate limiting + HTTPS obligatorio |
| Dependencias | Dependabot + `pip-audit` + `safety` en CI |
| Contenedor | Docker `--read-only --memory=512m` + usuario no-root |
| Código | `bandit` + `semgrep` en cada PR |
| Releases | Tags firmados con GPG (`git tag -s`) |
| Secretos | `.env` nunca en git — usar `.env.example` como plantilla |

## Prácticas de desarrollo seguro

- Commits firmados: `git config --global commit.gpgsign true`
- SBOM generado en cada release (formato CycloneDX)
- Imágenes Docker escaneadas con `trivy` antes de publicar
- Entornos reproducibles con Nix o Guix (roadmap)

import os
token = os.getenv("IBM_QUANTUM_TOKEN")


