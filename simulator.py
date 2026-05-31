"""
Simulador de sensores — Smart Campus
Envia leituras realistas para a API de X em X segundos.

Uso:
    python simulator.py                        # usa defaults
    python simulator.py --interval 5           # leitura a cada 5s
    python simulator.py --url http://localhost:8000
    python simulator.py --setup                # cria edifícios/salas/sensores e sai
"""
import asyncio
import httpx
import argparse
import random
import math
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000"
INTERVAL = 10  # segundos entre ciclos de leituras

# ── Dados do campus ───────────────────────────────────────────────────────────

BUILDINGS = [
    {"id": "H", "name": "Edifício H", "description": "Edifício de Engenharia Informática",
     "latitude": 39.6041, "longitude": -8.4128},
    {"id": "A", "name": "Edifício A", "description": "Edifício de Administração",
     "latitude": 39.6035, "longitude": -8.4120},
]

ROOMS = [
    {"id": "H216", "name": "Sala H216", "floor": 2, "capacity": 30, "type": "classroom", "building_id": "H"},
    {"id": "H218", "name": "Sala H218", "floor": 2, "capacity": 25, "type": "classroom", "building_id": "H"},
    {"id": "H101", "name": "Laboratório H101", "floor": 1, "capacity": 20, "type": "lab",       "building_id": "H"},
    {"id": "H301", "name": "Sala H301", "floor": 3, "capacity": 40, "type": "classroom", "building_id": "H"},
    {"id": "A201", "name": "Anfiteatro A201", "floor": 2, "capacity": 120, "type": "auditorium", "building_id": "A"},
    {"id": "A102", "name": "Sala A102", "floor": 1, "capacity": 30, "type": "classroom", "building_id": "A"},
]

# sensor_id → (tipo, unidade, valor_base, variação_max)
SENSORS = {
    # H216
    "temp-h216":  ("temperature", "°C",      22.0, 4.0),
    "hum-h216":   ("humidity",    "%",        50.0, 15.0),
    "co2-h216":   ("co2",         "ppm",     600.0, 300.0),
    "occ-h216":   ("occupancy",   "pessoas",  15.0, 15.0),
    "light-h216": ("light",       "lux",     300.0, 200.0),
    # H218
    "temp-h218":  ("temperature", "°C",      21.0, 4.0),
    "hum-h218":   ("humidity",    "%",        48.0, 12.0),
    "co2-h218":   ("co2",         "ppm",     550.0, 250.0),
    "occ-h218":   ("occupancy",   "pessoas",  10.0, 10.0),
    # H101
    "temp-h101":  ("temperature", "°C",      23.0, 5.0),
    "hum-h101":   ("humidity",    "%",        55.0, 20.0),
    "co2-h101":   ("co2",         "ppm",     700.0, 400.0),
    "occ-h101":   ("occupancy",   "pessoas",  12.0, 12.0),
    "light-h101": ("light",       "lux",     500.0, 300.0),
    # H301
    "temp-h301":  ("temperature", "°C",      20.0, 3.0),
    "co2-h301":   ("co2",         "ppm",     500.0, 200.0),
    "occ-h301":   ("occupancy",   "pessoas",  20.0, 20.0),
    # A201
    "temp-a201":  ("temperature", "°C",      24.0, 6.0),
    "hum-a201":   ("humidity",    "%",        52.0, 18.0),
    "co2-a201":   ("co2",         "ppm",     800.0, 500.0),
    "occ-a201":   ("occupancy",   "pessoas",  60.0, 60.0),
    # A102
    "temp-a102":  ("temperature", "°C",      21.5, 3.5),
    "co2-a102":   ("co2",         "ppm",     480.0, 180.0),
    "occ-a102":   ("occupancy",   "pessoas",  15.0, 15.0),
}

# Mapear sensor → sala para o POST /sensors
SENSOR_ROOMS = {
    "temp-h216": "H216", "hum-h216": "H216", "co2-h216": "H216",
    "occ-h216":  "H216", "light-h216": "H216",
    "temp-h218": "H218", "hum-h218": "H218", "co2-h218": "H218", "occ-h218": "H218",
    "temp-h101": "H101", "hum-h101": "H101", "co2-h101": "H101",
    "occ-h101":  "H101", "light-h101": "H101",
    "temp-h301": "H301", "co2-h301": "H301", "occ-h301": "H301",
    "temp-a201": "A201", "hum-a201": "A201", "co2-a201": "A201", "occ-a201": "A201",
    "temp-a102": "A102", "co2-a102": "A102", "occ-a102": "A102",
}

# ── Estado interno (deriva gradual) ──────────────────────────────────────────
_state: dict[str, float] = {}


def _init_state():
    for sid, (_, _, base, _) in SENSORS.items():
        _state[sid] = base


def _next_value(sensor_id: str, cycle: int) -> float:
    """
    Gera valor realista com:
    - deriva sinusoidal (simula variação ao longo do dia)
    - ruído gaussiano pequeno
    - limites físicos por tipo
    """
    stype, _, base, variation = SENSORS[sensor_id]

    # Onda lenta (período ~60 ciclos) + ruído
    drift = math.sin(cycle * 0.1) * (variation * 0.4)
    noise = random.gauss(0, variation * 0.1)
    value = base + drift + noise

    # Limites físicos
    if stype == "temperature":
        value = max(10.0, min(40.0, value))
    elif stype == "humidity":
        value = max(20.0, min(95.0, value))
    elif stype == "co2":
        value = max(350.0, min(2000.0, value))
    elif stype == "occupancy":
        value = max(0.0, min(ROOMS[0]["capacity"], abs(value)))
    elif stype == "light":
        value = max(0.0, min(1000.0, value))

    _state[sensor_id] = value
    return round(value, 1)


# ── Setup: criar edifícios, salas e sensores na API ───────────────────────────

async def setup(client: httpx.AsyncClient):
    print("\nA criar estrutura do campus na API...\n")

    for b in BUILDINGS:
        r = await client.post(f"{BASE_URL}/api/buildings/", json=b)
        if r.status_code == 201:
            print(f"  [OK] Edificio {b['id']} criado")
        elif r.status_code == 409:
            print(f"  [--] Edificio {b['id']} já existe")
        else:
            print(f"  [ERRO] Edificio {b['id']}: {r.status_code} {r.text}")

    for room in ROOMS:
        r = await client.post(f"{BASE_URL}/api/rooms/", json=room)
        if r.status_code == 201:
            print(f"  [OK] Sala {room['id']} criada")
        elif r.status_code == 409:
            print(f"  [--] Sala {room['id']} já existe")
        else:
            print(f"  [ERRO] Sala {room['id']}: {r.status_code} {r.text}")

    for sid, (stype, unit, _, _) in SENSORS.items():
        payload = {
            "id": sid,
            "type": stype,
            "unit": unit,
            "description": f"Sensor de {stype} — {SENSOR_ROOMS[sid]}",
            "active": True,
            "room_id": SENSOR_ROOMS[sid],
        }
        r = await client.post(f"{BASE_URL}/api/sensors/", json=payload)
        if r.status_code == 201:
            print(f"  [OK] Sensor {sid} criado")
        elif r.status_code == 409:
            print(f"  [--] Sensor {sid} já existe")
        else:
            print(f"  [ERRO] Sensor {sid}: {r.status_code} {r.text}")

    print("\nSetup concluido!\n")


# ── Ciclo de simulação ────────────────────────────────────────────────────────

async def send_reading(client: httpx.AsyncClient, sensor_id: str, value: float):
    payload = {
        "sensor_id": sensor_id,
        "value": value,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        r = await client.post(f"{BASE_URL}/api/readings/", json=payload)
        return r.status_code == 201
    except Exception:
        return False


async def simulate(interval: int):
    _init_state()
    cycle = 0

    print(f"Simulador iniciado — {len(SENSORS)} sensores, ciclo a cada {interval}s")
    print(f"   API: {BASE_URL}")
    print("   Ctrl+C para parar\n")

    async with httpx.AsyncClient(timeout=10) as client:
        # Verificar que a API está online
        try:
            r = await client.get(f"{BASE_URL}/health")
            r.raise_for_status()
            print("API online\n")
        except Exception:
            print("ERRO: API nao responde. Certifica-te que o uvicorn está a correr.")
            return

        while True:
            cycle += 1
            now = datetime.now().strftime("%H:%M:%S")
            ok = fail = 0

            tasks = []
            for sid in SENSORS:
                value = _next_value(sid, cycle)
                tasks.append(send_reading(client, sid, value))

            results = await asyncio.gather(*tasks)
            ok = sum(results)
            fail = len(results) - ok

            stype_summary = {}
            for sid, (stype, unit, _, _) in SENSORS.items():
                if stype not in stype_summary:
                    stype_summary[stype] = []
                stype_summary[stype].append(_state[sid])

            print(f"[{now}] Ciclo {cycle:04d} — [OK] {ok} leituras  [ERRO] {fail} erros")
            for stype, vals in stype_summary.items():
                avg = sum(vals) / len(vals)
                unit = next(u for _, (t, u, _, _) in SENSORS.items() if t == stype)
                print(f"   {stype:<12} média={avg:.1f} {unit}")
            print()

            await asyncio.sleep(interval)


# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    global BASE_URL
    parser = argparse.ArgumentParser(description="Simulador de sensores — Smart Campus")
    parser.add_argument("--interval", type=int, default=INTERVAL, help="Segundos entre ciclos")
    parser.add_argument("--url", default=BASE_URL, help="URL base da API")
    parser.add_argument("--setup", action="store_true", help="Criar edifícios/salas/sensores e sair")
    args = parser.parse_args()

    BASE_URL = args.url

    async with httpx.AsyncClient(timeout=10) as client:
        if args.setup:
            await setup(client)
            return

    # Setup automático + simulação
    async with httpx.AsyncClient(timeout=10) as client:
        await setup(client)

    await simulate(args.interval)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nSimulador parado.")