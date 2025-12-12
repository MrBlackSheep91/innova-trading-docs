#!/usr/bin/env python3
"""
Signal Generator - Ejemplo para desarrolladores externos
Muestra como enviar señales de trading a InnovaTrading API

Requisitos:
    pip install requests

Uso:
    1. Configura tu API_KEY y API_URL
    2. Implementa tu logica de señales en generate_signals()
    3. Ejecuta el script continuamente o como cron job
"""

import requests
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

# =============================================================================
# CONFIGURACION - Modifica estos valores
# =============================================================================

API_URL = "https://api.innova-trading.com"  # URL de la API
API_KEY = "tu_api_key_aqui"                 # Tu API key
INDICATOR_ID = "mi_indicador"               # ID unico de tu indicador
INDICATOR_NAME = "Mi Indicador de Señales"  # Nombre visible en el chart
SYMBOL = "EURUSD"                           # Par a analizar
TIMEFRAME = 60                              # Timeframe en minutos (60 = H1)

# =============================================================================
# FUNCIONES DE API
# =============================================================================

def get_bars(symbol: str, timeframe: int, limit: int = 500) -> Optional[List[Dict]]:
    """
    Obtiene datos OHLC de la API.

    Args:
        symbol: Par de trading (ej: "EURUSD")
        timeframe: Timeframe en minutos (1, 5, 15, 60, 240, 1440)
        limit: Cantidad de barras a obtener (max 5000)

    Returns:
        Lista de barras con time, open, high, low, close, volume
        o None si hay error
    """
    url = f"{API_URL}/api/external/bars"
    params = {
        "symbol": symbol,
        "timeframe": timeframe,
        "limit": limit
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()
            return data.get("bars", [])
        else:
            print(f"Error obteniendo barras: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"Error de conexion: {e}")
        return None


def submit_signals(
    indicator_id: str,
    symbol: str,
    timeframe: int,
    indicator_name: str,
    points: List[Dict],
    lines: Optional[List[Dict]] = None,
    metadata: Optional[Dict] = None
) -> bool:
    """
    Envia señales a la API.

    Args:
        indicator_id: ID unico de tu indicador
        symbol: Par de trading
        timeframe: Timeframe en minutos
        indicator_name: Nombre visible del indicador
        points: Lista de puntos/señales (markers)
        lines: Lista de lineas horizontales (SL/TP levels)
        metadata: Informacion adicional opcional

    Returns:
        True si se enviaron correctamente, False si hubo error
    """
    url = f"{API_URL}/api/external/indicators/{indicator_id}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "symbol": symbol,
        "timeframe": timeframe,
        "indicator_name": indicator_name,
        "version": "1.0",
        "points": points,
        "lines": lines or [],
        "metadata": metadata or {}
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code in [200, 201]:
            result = response.json()
            print(f"Señales enviadas: {result.get('points_received', 0)} puntos, {result.get('lines_received', 0)} lineas")
            print(f"Expira: {result.get('expires_at')}")
            return True
        else:
            print(f"Error enviando señales: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"Error de conexion: {e}")
        return False


# =============================================================================
# TU LOGICA DE SEÑALES - Modifica esta funcion
# =============================================================================

def generate_signals(bars: List[Dict]) -> tuple:
    """
    Genera señales basadas en los datos OHLC.

    MODIFICA ESTA FUNCION con tu estrategia de trading.

    Args:
        bars: Lista de barras con time, open, high, low, close
              bars[0] es la mas antigua, bars[-1] es la mas reciente

    Returns:
        Tuple de (points, lines):
        - points: Lista de markers/flechas
        - lines: Lista de lineas horizontales para SL/TP
    """
    points = []
    lines = []
    signal_count = 0

    # =========================================================================
    # EJEMPLO: Detectar Inside Bars y generar señal con Entry, SL, TP
    # Reemplaza esto con tu propia estrategia
    # =========================================================================

    for i in range(2, len(bars)):
        prev = bars[i - 1]
        curr = bars[i]

        # Detectar Inside Bar
        is_inside_bar = (
            curr["high"] < prev["high"] and
            curr["low"] > prev["low"]
        )

        if not is_inside_bar:
            continue

        # Determinar direccion basada en cierre
        mid_point = (prev["high"] + prev["low"]) / 2
        is_bullish = curr["close"] > mid_point

        # Calcular niveles
        bar_time = curr["time"]  # IMPORTANTE: usar el timestamp real
        entry_price = curr["close"]

        signal_id = f"signal_{signal_count:03d}"
        signal_count += 1

        if is_bullish:
            # Señal de COMPRA
            stop_loss = prev["low"] - 0.0005  # 5 pips debajo
            tp1 = entry_price + (entry_price - stop_loss) * 1  # RR 1:1
            tp2 = entry_price + (entry_price - stop_loss) * 2  # RR 1:2
            tp3 = entry_price + (entry_price - stop_loss) * 3  # RR 1:3

            # Entry point (flecha)
            points.append({
                "time": bar_time,
                "type": "low",
                "price": entry_price,
                "label": "BUY",
                "color": "#3b82f6",  # Azul
                "shape": "arrowUp",
                "size": 2
            })

            # LINEAS HORIZONTALES (extienden 15 barras)
            lines.append({
                "id": f"{signal_id}_entry",
                "price": entry_price,
                "start_time": bar_time,
                "bars": 15,
                "label": f"Entry: {entry_price:.5f}",
                "color": "#3b82f6",
                "style": "dashed",
                "width": 1
            })

            lines.append({
                "id": f"{signal_id}_sl",
                "price": stop_loss,
                "start_time": bar_time,
                "bars": 15,
                "label": f"SL: {stop_loss:.5f}",
                "color": "#ef4444",
                "style": "solid",
                "width": 2
            })

            lines.append({
                "id": f"{signal_id}_tp1",
                "price": tp1,
                "start_time": bar_time,
                "bars": 15,
                "label": f"TP1: {tp1:.5f}",
                "color": "#22c55e",
                "style": "dotted",
                "width": 1
            })

            lines.append({
                "id": f"{signal_id}_tp2",
                "price": tp2,
                "start_time": bar_time,
                "bars": 15,
                "label": f"TP2: {tp2:.5f}",
                "color": "#10b981",
                "style": "dotted",
                "width": 1
            })

            lines.append({
                "id": f"{signal_id}_tp3",
                "price": tp3,
                "start_time": bar_time,
                "bars": 15,
                "label": f"TP3: {tp3:.5f}",
                "color": "#059669",
                "style": "dotted",
                "width": 1
            })

        else:
            # Señal de VENTA
            stop_loss = prev["high"] + 0.0005  # 5 pips arriba
            tp1 = entry_price - (stop_loss - entry_price) * 1
            tp2 = entry_price - (stop_loss - entry_price) * 2
            tp3 = entry_price - (stop_loss - entry_price) * 3

            # Entry point (flecha)
            points.append({
                "time": bar_time,
                "type": "high",
                "price": entry_price,
                "label": "SELL",
                "color": "#f97316",  # Naranja
                "shape": "arrowDown",
                "size": 2
            })

            # LINEAS HORIZONTALES
            lines.append({
                "id": f"{signal_id}_entry",
                "price": entry_price,
                "start_time": bar_time,
                "bars": 15,
                "label": f"Entry: {entry_price:.5f}",
                "color": "#f97316",
                "style": "dashed",
                "width": 1
            })

            lines.append({
                "id": f"{signal_id}_sl",
                "price": stop_loss,
                "start_time": bar_time,
                "bars": 15,
                "label": f"SL: {stop_loss:.5f}",
                "color": "#ef4444",
                "style": "solid",
                "width": 2
            })

            lines.append({
                "id": f"{signal_id}_tp1",
                "price": tp1,
                "start_time": bar_time,
                "bars": 15,
                "label": f"TP1: {tp1:.5f}",
                "color": "#22c55e",
                "style": "dotted",
                "width": 1
            })

            lines.append({
                "id": f"{signal_id}_tp2",
                "price": tp2,
                "start_time": bar_time,
                "bars": 15,
                "label": f"TP2: {tp2:.5f}",
                "color": "#10b981",
                "style": "dotted",
                "width": 1
            })

            lines.append({
                "id": f"{signal_id}_tp3",
                "price": tp3,
                "start_time": bar_time,
                "bars": 15,
                "label": f"TP3: {tp3:.5f}",
                "color": "#059669",
                "style": "dotted",
                "width": 1
            })

    return points, lines


# =============================================================================
# EJECUCION PRINCIPAL
# =============================================================================

def run_once():
    """Ejecuta el generador de señales una vez."""
    print("=" * 60)
    print(f"Signal Generator - {datetime.now(timezone.utc).isoformat()}")
    print(f"Symbol: {SYMBOL} | Timeframe: {TIMEFRAME}m")
    print("=" * 60)

    # 1. Obtener datos
    print("\n1. Obteniendo datos OHLC...")
    bars = get_bars(SYMBOL, TIMEFRAME, limit=500)

    if not bars:
        print("   ERROR: No se pudieron obtener los datos")
        return False

    print(f"   OK: {len(bars)} barras obtenidas")

    # 2. Generar señales
    print("\n2. Generando señales...")
    points, lines = generate_signals(bars)
    print(f"   OK: {len(points)} puntos, {len(lines)} lineas generadas")

    if not points and not lines:
        print("   No hay señales para enviar")
        return True

    # 3. Contar tipos de señales
    buy_signals = len([s for s in points if s.get("label") == "BUY"])
    sell_signals = len([s for s in points if s.get("label") == "SELL"])
    print(f"   - BUY: {buy_signals}")
    print(f"   - SELL: {sell_signals}")

    # 4. Enviar a la API
    print("\n3. Enviando señales a la API...")
    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_points": len(points),
        "total_lines": len(lines),
        "buy_count": buy_signals,
        "sell_count": sell_signals,
        "strategy": "Inside Bar with Multi-TP + Lines"
    }

    success = submit_signals(
        indicator_id=INDICATOR_ID,
        symbol=SYMBOL,
        timeframe=TIMEFRAME,
        indicator_name=INDICATOR_NAME,
        points=points,
        lines=lines,
        metadata=metadata
    )

    if success:
        print("\n" + "=" * 60)
        print("EXITO! Señales enviadas correctamente.")
        print("Las señales aparecen automaticamente en el chart.")
        print("=" * 60)

    return success


def run_continuous(interval_seconds: int = 300):
    """
    Ejecuta el generador de señales continuamente.

    Args:
        interval_seconds: Intervalo entre ejecuciones (default: 5 minutos)
    """
    print(f"Iniciando modo continuo (cada {interval_seconds} segundos)")
    print("Presiona Ctrl+C para detener\n")

    while True:
        try:
            run_once()
            print(f"\nProxima ejecucion en {interval_seconds} segundos...\n")
            time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n\nDetenido por el usuario")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print(f"Reintentando en {interval_seconds} segundos...\n")
            time.sleep(interval_seconds)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        # Modo continuo: python signal_generator.py --continuous
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 300
        run_continuous(interval)
    else:
        # Modo unico: python signal_generator.py
        run_once()
