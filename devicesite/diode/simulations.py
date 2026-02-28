import math

# Constants
q = 1.6e-19          # charge of electron (C)
eps0 = 8.85e-14      # permittivity of free space (F/cm)
eps_si = 11.7 * eps0 # permittivity of silicon (F/cm)
k = 1.38e-23         # Boltzmann constant (J/K)
T = 300              # temperature (K)
ni = 1.5e10          # intrinsic carrier concentration (cm^-3)

def simulate_diode(voltage, Rs, Is=1e-12, n=1.0, Vt=0.025):    
    Id = Is * (math.exp(voltage / (n * Vt)) - 1)    
    Vdrop = Id * Rs   
    Vterminal = voltage - Vdrop
    leakage_current = -Is * 1e6  # µA
    return {"bias_voltage": voltage,"series_resistance": Rs,"saturation_current": Is,"ideality_factor": n,
        "thermal_voltage": Vt,"diode_current": Id,"terminal_voltage": Vterminal,"leakage_current": leakage_current
    }

def depletion_width(Na, Nd, Vbi=0.7, Vapp=0.0):   
    Vj = Vbi + Vapp
    W_total = math.sqrt((2 * eps_si * Vj / q) * ((Na + Nd) / (Na * Nd)))
    Wn = W_total * (Na / (Na + Nd))
    Wp = W_total * (Nd / (Na + Nd))
    return {"Wn": Wn, "Wp": Wp}

def built_in_potential(Na, Nd, T=300):    
    Vt = (k * T) / q   # thermal voltage
    Vbi = Vt * math.log((Na * Nd) / (ni**2))
    return Vbi

DIODE_DATABASE = {
    "1N4148": "Is=1e-12,n=1.0,Rs=10,Nd=1e17,Na=1e18,ni=1e10",
    "power": "Is=1e-8,n=1.2,Rs=0.5,Nd=1e15,Na=1e17,ni=1e10",
    "led": "Is=1e-14,n=2.0,Rs=20,Nd=1e17,Na=1e17,ni=1e10"
}

# utils.py or inside views.py
def parse_constants(diode_name):
    constants_str = DIODE_DATABASE.get(diode_name)
    if not constants_str:
        return {}

    constants = {}
    for item in constants_str.split(","):
        key, val = item.split("=")
        constants[key] = float(val)
    return constants

def calculate_diode(Na, Nd, ni, Vapp, Rs=0, Is=1e-12, n=1.0, T=300):
    # Thermal voltage
    Vt = (k * T) / q

    # Built-in potential
    Vbi = Vt * math.log((Na * Nd) / (ni**2))

    # Depletion widths
    Vj = Vbi - Vapp
    W_total = math.sqrt((2 * eps_si * Vj / q) * ((Na + Nd) / (Na * Nd)))
    Wn = W_total * (Na / (Na + Nd))
    Wp = W_total * (Nd / (Na + Nd))
    # Diode current at given bias 
    Id = Is * (math.exp(Vj / (n * Vt)) - 1) 
    Vdrop = Id * Rs 
    Vterminal = Vapp - Vdrop
    # Format outputs for frontend
    a_cm = 5.43e-8  # lattice constant in cm
    return {
        "Vbi": round(Vbi * 1000, 1),          # mV
        "Wn": f"{(Wn / a_cm):.3e}",           # multiples of a
        "Wp": f"{(Wp / a_cm):.3e}",
        "ni": f"{(ni / 1e12):.2e} /µm³",      # converted density        
        "Rs": Rs,
        "Id": f"{Id:.3e} A", # NEW field 
        "Vterminal": round(Vterminal, 3),
        "Vapp": Vapp,
        "Is": Is,
        "n": n
    }
