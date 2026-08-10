# ============================================================
# SOLAR HEART - SIMULATION DATA ENGINE
# Developed by Shashank Mani
# OPC-UA Integration: Later
# ============================================================

import random
import math
from datetime import datetime


# ============================================================
# BASIC HELPERS
# ============================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def fluctuate(base, variation):
    return round(
        base + random.uniform(-variation, variation),
        2
    )


# ============================================================
# PLANT DATA
# ============================================================

def get_plant_data():
    hour = datetime.now().hour

    # Simple day/night simulation
    if 6 <= hour <= 18:
        solar_factor = max(
            0.1,
            math.sin((hour - 6) / 12 * math.pi)
        )
    else:
        solar_factor = 0.02

    irradiance = clamp(
        900 * solar_factor + random.uniform(-30, 30),
        0,
        1100
    )

    ambient_temp = fluctuate(35, 3)
    module_temp = fluctuate(
        ambient_temp + irradiance * 0.015,
        3
    )

    wind_speed = fluctuate(5, 2)

    return {
        "irradiance": round(irradiance, 2),
        "ambient_temp": round(ambient_temp, 2),
        "module_temp": round(module_temp, 2),
        "wind_speed": round(max(0, wind_speed), 2),
    }


# ============================================================
# INVERTER DATA
# Each inverter has 3 Units
# ============================================================

def get_inverter_data(
    inverter_no,
    units=3
):

    plant = get_plant_data()

    inverter_load = random.uniform(
        0.70,
        1.00
    )

    active_power = (
        250
        * inverter_load
        * (plant["irradiance"] / 1000)
    )

    reactive_power = active_power * random.uniform(
        0.10,
        0.30
    )

    apparent_power = math.sqrt(
        active_power ** 2
        + reactive_power ** 2
    )

    power_factor = (
        active_power / apparent_power
        if apparent_power > 0
        else 1
    )

    data = {

        # Identity
        "inverter_no": inverter_no,
        "status": random.choice(
            [
                "RUNNING",
                "RUNNING",
                "RUNNING",
                "STANDBY"
            ]
        ),

        # AC
        "ac_voltage_ry": fluctuate(598, 5),
        "ac_voltage_yb": fluctuate(594, 5),
        "ac_voltage_br": fluctuate(593, 5),

        "ac_current_r": fluctuate(245, 10),
        "ac_current_y": fluctuate(245, 10),
        "ac_current_b": fluctuate(246, 10),

        # AC Power
        "active_power": round(
            max(0, active_power),
            2
        ),

        "reactive_power": round(
            max(0, reactive_power),
            2
        ),

        "apparent_power": round(
            max(0, apparent_power),
            2
        ),

        "power_factor": round(
            clamp(power_factor, 0, 1),
            3
        ),

        "frequency": fluctuate(
            50.00,
            0.05
        ),

        # DC
        "dc_voltage": fluctuate(
            1228,
            15
        ),

        "dc_current": fluctuate(
            200,
            20
        ),

        "dc_power": round(
            max(0, active_power * 1.03),
            2
        ),

        # Temperature
        "internal_temperature": fluctuate(
            37,
            2
        ),

        "temperature_1": fluctuate(
            47,
            3
        ),

        "temperature_2": fluctuate(
            46,
            3
        ),

        "temperature_3": fluctuate(
            47,
            3
        ),

        "temperature_4": fluctuate(
            46,
            3
        ),

        "temperature_5": fluctuate(
            47,
            3
        ),

        "temperature_6": fluctuate(
            46,
            3
        ),

        # Performance
        "efficiency": fluctuate(
            98.0,
            1.0
        ),

        "today_energy": fluctuate(
            1350,
            100
        ),

        "monthly_energy": fluctuate(
            37200,
            500
        ),

        "total_energy": fluctuate(
            491,
            10
        ),

        "today_grid_connected_min": random.randint(
            500,
            800
        ),

        "total_run_hours": fluctuate(
            2500,
            50
        ),

        "co2_reduction": fluctuate(
            894000,
            5000
        ),

        "peak_kw": fluctuate(
            1660,
            30
        ),

        "inverter_pr": fluctuate(
            95,
            2
        ),

        "inverter_cpr": fluctuate(
            96,
            2
        ),

        "availability": fluctuate(
            98,
            1
        ),

        "breakdown_loss": fluctuate(
            0,
            1
        ),

        "breakdown_minutes": random.randint(
            0,
            10
        ),
    }

    # ========================================================
    # UNIT DATA
    # ========================================================

    data["units"] = []

    for unit_no in range(1, units + 1):

        unit_power = max(
            0,
            active_power / units
            + random.uniform(-5, 5)
        )

        unit = {

            "unit_no": unit_no,

            "dc_voltage": fluctuate(
                1228,
                10
            ),

            "dc_current": fluctuate(
                200,
                15
            ),

            "dc_power": round(
                unit_power,
                2
            ),

            "ac_voltage": fluctuate(
                595,
                5
            ),

            "ac_current": fluctuate(
                245,
                10
            ),

            "power": round(
                unit_power,
                2
            ),

            "status": random.choice(
                [
                    "RUNNING",
                    "RUNNING",
                    "RUNNING",
                    "STOP"
                ]
            ),

            "temperature": fluctuate(
                45,
                3
            )
        }

        data["units"].append(unit)

    return data


# ============================================================
# SCB DATA
# ============================================================

def get_scb_data(scb_no):

    return {

        "scb_no": scb_no,

        "current": fluctuate(
            32,
            5
        ),

        "voltage": fluctuate(
            1100,
            20
        ),

        "power": fluctuate(
            35,
            5
        ),

        "status": random.choice(
            [
                "HEALTHY",
                "HEALTHY",
                "HEALTHY",
                "FAULT"
            ]
        )
    }


# ============================================================
# MFM DATA
# ============================================================

def get_mfm_data():

    voltage = fluctuate(
        33.0,
        0.5
    )

    current = fluctuate(
        425,
        20
    )

    active_power = fluctuate(
        242,
        10
    )

    reactive_power = fluctuate(
        62,
        5
    )

    apparent_power = math.sqrt(
        active_power ** 2
        + reactive_power ** 2
    )

    return {

        "voltage_kv": voltage,

        "current_a": current,

        "active_power_mw": active_power,

        "reactive_power_mvar": reactive_power,

        "apparent_power_mva": round(
            apparent_power,
            2
        ),

        "power_factor": round(
            active_power / apparent_power,
            3
        ),

        "frequency_hz": fluctuate(
            50,
            0.05
        ),

        "energy_mwh": fluctuate(
            244,
            5
        )
    }


# ============================================================
# RELAY DATA
# ============================================================

def get_relay_data():

    signals = [

        "50 Operated",
        "51 Operated",
        "50N Operated",
        "51N Operated",
        "95_1 Operated",
        "95_2 Operated",
        "59 Operated",
        "27 Operated",
        "86 Operated",
        "Remote",
        "Spring Charge",
        "Test",
        "Service",
        "Earth Switch",
        "Communication Error"
    ]

    result = {}

    for signal in signals:

        # Mostly healthy/off
        result[signal] = random.choice(
            [
                False,
                False,
                False,
                False,
                True
            ]
        )

    return result


# ============================================================
# ANNUNCIATOR DATA
# ============================================================

def get_annunciator_data():

    signals = [

        "OC & EF TRIP",
        "MST TRIP",
        "LV3 WTI TRIP",
        "LV4 WTI ALM",
        "TCS OPTD",
        "AC FAIL",
        "LV4 WTI TRIP",
        "HV WTI ALM",
        "DC FAIL",
        "DIFF. OPTD",
        "HV WTI TRIP",
        "OTI ALM",
        "PT FUSE",
        "LV1 WTI ALM",
        "OTI TRIP",
        "BUCH ALM",
        "LV1 WTI TRIP",
        "LV2 WTI ALM",
        "BUCH TRIP",
        "MOG ALM",
        "LV2 WTI TRIP",
        "LV3 WTI ALM",
        "PRV TRIP 1",
        "PRV TRIP 2"
    ]

    result = {}

    for signal in signals:

        result[signal] = random.choice(
            [
                False,
                False,
                False,
                False,
                False,
                True
            ]
        )

    return result


# ============================================================
# DI / DO DATA
# ============================================================

def get_dido_data():

    return {

        "CB Trip": random.choice(
            [False, False, False, False, True]
        ),

        "CB Close": random.choice(
            [True, True, True, False]
        ),

        "CB Open": random.choice(
            [False, False, False, True]
        ),

        "Breaker Healthy": True,

        "Aux MCCB-1": random.choice(
            [True, False]
        ),

        "Aux MCCB-2": random.choice(
            [True, False]
        ),

        "Relay Fail": random.choice(
            [False, False, False, True]
        )
    }


# ============================================================
# COMPLETE HT PANEL
# ============================================================

def get_ht_panel_data():

    return {

        "mfm": get_mfm_data(),

        "relay": get_relay_data(),

        "annunciator": get_annunciator_data(),

        "dido": get_dido_data()
    }