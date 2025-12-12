/**
 * Signal Generator - Ejemplo para desarrolladores externos (Node.js)
 * Muestra como enviar señales de trading a InnovaTrading API
 *
 * Requisitos:
 *   npm install node-fetch (o usar fetch nativo en Node 18+)
 *
 * Uso:
 *   1. Configura API_KEY y API_URL
 *   2. Implementa tu logica en generateSignals()
 *   3. node signal_generator.js
 *   4. Para modo continuo: node signal_generator.js --continuous
 */

// =============================================================================
// CONFIGURACION - Modifica estos valores
// =============================================================================

const CONFIG = {
  API_URL: "https://api.innova-trading.com",  // URL de la API
  API_KEY: "tu_api_key_aqui",                 // Tu API key
  INDICATOR_ID: "mi_indicador",               // ID unico de tu indicador
  INDICATOR_NAME: "Mi Indicador JS",          // Nombre visible en el chart
  SYMBOL: "EURUSD",                           // Par a analizar
  TIMEFRAME: 60,                              // Timeframe en minutos (60 = H1)
};

// =============================================================================
// FUNCIONES DE API
// =============================================================================

/**
 * Obtiene datos OHLC de la API
 * @param {string} symbol - Par de trading (ej: "EURUSD")
 * @param {number} timeframe - Timeframe en minutos
 * @param {number} limit - Cantidad de barras (max 5000)
 * @returns {Promise<Array|null>} Lista de barras o null si error
 */
async function getBars(symbol, timeframe, limit = 500) {
  const url = new URL(`${CONFIG.API_URL}/api/external/bars`);
  url.searchParams.set("symbol", symbol);
  url.searchParams.set("timeframe", timeframe);
  url.searchParams.set("limit", limit);

  try {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${CONFIG.API_KEY}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      return data.bars || [];
    } else {
      console.error(`Error obteniendo barras: ${response.status}`);
      console.error(await response.text());
      return null;
    }
  } catch (error) {
    console.error(`Error de conexion: ${error.message}`);
    return null;
  }
}

/**
 * Envia señales a la API
 * @param {Object} params - Parametros de la señal
 * @returns {Promise<boolean>} true si exito, false si error
 */
async function submitSignals({
  indicatorId,
  symbol,
  timeframe,
  indicatorName,
  points,
  lines = [],
  metadata = {},
}) {
  const url = `${CONFIG.API_URL}/api/external/indicators/${indicatorId}`;

  const payload = {
    symbol,
    timeframe,
    indicator_name: indicatorName,
    version: "1.0",
    points,
    lines,
    metadata,
  };

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${CONFIG.API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      const result = await response.json();
      console.log(`Señales enviadas: ${result.points_received} puntos`);
      console.log(`Expira: ${result.expires_at}`);
      return true;
    } else {
      console.error(`Error enviando señales: ${response.status}`);
      console.error(await response.text());
      return false;
    }
  } catch (error) {
    console.error(`Error de conexion: ${error.message}`);
    return false;
  }
}

// =============================================================================
// TU LOGICA DE SEÑALES - Modifica esta funcion
// =============================================================================

/**
 * Genera señales basadas en los datos OHLC
 *
 * MODIFICA ESTA FUNCION con tu estrategia de trading.
 *
 * @param {Array} bars - Lista de barras con time, open, high, low, close
 *                       bars[0] es la mas antigua, bars[bars.length-1] la mas reciente
 * @returns {Array} Lista de señales
 */
function generateSignals(bars) {
  const signals = [];

  // =========================================================================
  // EJEMPLO: Detectar Inside Bars y generar señal con Entry, SL, TP
  // Reemplaza esto con tu propia estrategia
  // =========================================================================

  for (let i = 2; i < bars.length; i++) {
    const prev = bars[i - 1];
    const curr = bars[i];

    // Detectar Inside Bar
    const isInsideBar = curr.high < prev.high && curr.low > prev.low;

    if (!isInsideBar) continue;

    // Determinar direccion
    const midPoint = (prev.high + prev.low) / 2;
    const isBullish = curr.close > midPoint;

    // IMPORTANTE: usar el timestamp real de la barra
    const barTime = curr.time;
    const entryPrice = curr.close;

    if (isBullish) {
      // Señal de COMPRA
      const stopLoss = prev.low - 0.0005;
      const tp1 = entryPrice + (entryPrice - stopLoss) * 1;
      const tp2 = entryPrice + (entryPrice - stopLoss) * 2;
      const tp3 = entryPrice + (entryPrice - stopLoss) * 3;

      signals.push(
        {
          time: barTime,
          type: "low",
          price: entryPrice,
          label: "BUY",
          color: "#3b82f6",
          shape: "arrowUp",
          size: 2,
        },
        {
          time: barTime,
          type: "low",
          price: stopLoss,
          label: "SL",
          color: "#ef4444",
          shape: "square",
          size: 1,
        },
        {
          time: barTime,
          type: "high",
          price: tp1,
          label: "TP1",
          color: "#22c55e",
          shape: "circle",
          size: 1,
        },
        {
          time: barTime,
          type: "high",
          price: tp2,
          label: "TP2",
          color: "#22c55e",
          shape: "circle",
          size: 1,
        },
        {
          time: barTime,
          type: "high",
          price: tp3,
          label: "TP3",
          color: "#22c55e",
          shape: "circle",
          size: 1,
        }
      );
    } else {
      // Señal de VENTA
      const stopLoss = prev.high + 0.0005;
      const tp1 = entryPrice - (stopLoss - entryPrice) * 1;
      const tp2 = entryPrice - (stopLoss - entryPrice) * 2;
      const tp3 = entryPrice - (stopLoss - entryPrice) * 3;

      signals.push(
        {
          time: barTime,
          type: "high",
          price: entryPrice,
          label: "SELL",
          color: "#f97316",
          shape: "arrowDown",
          size: 2,
        },
        {
          time: barTime,
          type: "high",
          price: stopLoss,
          label: "SL",
          color: "#ef4444",
          shape: "square",
          size: 1,
        },
        {
          time: barTime,
          type: "low",
          price: tp1,
          label: "TP1",
          color: "#22c55e",
          shape: "circle",
          size: 1,
        },
        {
          time: barTime,
          type: "low",
          price: tp2,
          label: "TP2",
          color: "#22c55e",
          shape: "circle",
          size: 1,
        },
        {
          time: barTime,
          type: "low",
          price: tp3,
          label: "TP3",
          color: "#22c55e",
          shape: "circle",
          size: 1,
        }
      );
    }
  }

  return signals;
}

// =============================================================================
// EJECUCION PRINCIPAL
// =============================================================================

async function runOnce() {
  console.log("=".repeat(60));
  console.log(`Signal Generator - ${new Date().toISOString()}`);
  console.log(`Symbol: ${CONFIG.SYMBOL} | Timeframe: ${CONFIG.TIMEFRAME}m`);
  console.log("=".repeat(60));

  // 1. Obtener datos
  console.log("\n1. Obteniendo datos OHLC...");
  const bars = await getBars(CONFIG.SYMBOL, CONFIG.TIMEFRAME, 500);

  if (!bars) {
    console.log("   ERROR: No se pudieron obtener los datos");
    return false;
  }
  console.log(`   OK: ${bars.length} barras obtenidas`);

  // 2. Generar señales
  console.log("\n2. Generando señales...");
  const signals = generateSignals(bars);
  console.log(`   OK: ${signals.length} señales generadas`);

  if (signals.length === 0) {
    console.log("   No hay señales para enviar");
    return true;
  }

  // 3. Contar tipos
  const buyCount = signals.filter((s) => s.label === "BUY").length;
  const sellCount = signals.filter((s) => s.label === "SELL").length;
  console.log(`   - BUY: ${buyCount}`);
  console.log(`   - SELL: ${sellCount}`);

  // 4. Enviar a la API
  console.log("\n3. Enviando señales a la API...");

  const success = await submitSignals({
    indicatorId: CONFIG.INDICATOR_ID,
    symbol: CONFIG.SYMBOL,
    timeframe: CONFIG.TIMEFRAME,
    indicatorName: CONFIG.INDICATOR_NAME,
    points: signals,
    metadata: {
      generated_at: new Date().toISOString(),
      total_signals: signals.length,
      buy_count: buyCount,
      sell_count: sellCount,
      strategy: "Inside Bar with Multi-TP",
    },
  });

  if (success) {
    console.log("\n" + "=".repeat(60));
    console.log("EXITO! Señales enviadas correctamente.");
    console.log("Las señales aparecen automaticamente en el chart.");
    console.log("=".repeat(60));
  }

  return success;
}

async function runContinuous(intervalMs = 300000) {
  console.log(`Iniciando modo continuo (cada ${intervalMs / 1000} segundos)`);
  console.log("Presiona Ctrl+C para detener\n");

  while (true) {
    try {
      await runOnce();
      console.log(`\nProxima ejecucion en ${intervalMs / 1000} segundos...\n`);
      await new Promise((resolve) => setTimeout(resolve, intervalMs));
    } catch (error) {
      console.error(`\nError: ${error.message}`);
      console.log(`Reintentando en ${intervalMs / 1000} segundos...\n`);
      await new Promise((resolve) => setTimeout(resolve, intervalMs));
    }
  }
}

// Main
const args = process.argv.slice(2);
if (args.includes("--continuous")) {
  const intervalIndex = args.indexOf("--continuous") + 1;
  const interval = args[intervalIndex] ? parseInt(args[intervalIndex]) * 1000 : 300000;
  runContinuous(interval);
} else {
  runOnce();
}
