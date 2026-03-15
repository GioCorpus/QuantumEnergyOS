# Validaciones de seguridad y reproducibilidad

check-reqs:
    @echo "🔍 Validando requirements-pinned.txt..."
    @# 1. No debe contener comandos de shell
    @if grep -E '^(pip|sed|awk|head|tail|git)' requirements-pinned.txt; then \
        echo "❌ ERROR: requirements-pinned.txt contiene comandos inválidos"; \
        exit 1; \
    fi
    @# 2. Todas las líneas deben ser paquetes válidos o comentarios
    @if grep -vE '^(#|[a-zA-Z0-9_.-]+(==|>=|<=|>|<)[^ ]+|git\+https://)' requirements-pinned.txt | grep .; then \
        echo "❌ ERROR: requirements-pinned.txt contiene líneas no reconocidas"; \
        exit 1; \
    fi
    @# 3. Instalación en seco
    @pip install --dry-run -r requirements-pinned.txt >/dev/null || \
        ( echo "❌ ERROR: pip no pudo instalar requirements-pinned.txt"; exit 1 )
    @echo "✅ requirements-pinned.txt válido"
