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

        FROM python:3.11

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
