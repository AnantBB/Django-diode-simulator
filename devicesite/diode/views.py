import math
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from .simulations import parse_constants

def safe_float(value, default=0.0, min_nonzero=None):
    try:
        val = float(value)
        if val == 0.0 and min_nonzero is not None:
            return min_nonzero
        return val
    except (TypeError, ValueError):
        return default

def diode_view(request):
    """Main diode simulation view."""
    diode_name = request.GET.get("diode", "1N4148")
    constants = parse_constants(diode_name)
    
           
    Vt = constants.get("Vt", 0.025)   # volts
    Vapp = constants.get("Vapp", 0.0)
    Is = constants.get("Is", 1e-14)
    Rs = constants.get("Rs", 10)

    context = {
        "diode": diode_name,
        "Nd": float(constants["Nd"]) / 1e12, # µm⁻³  
        "Na": float(constants["Na"]) / 1e12, # µm⁻³ 
        "ni": float(constants["ni"]), # µm⁻³
        "Vt": int(Vt * 1000), # numeric mV       
        "Vapp": Vapp,
        "Is": Is,
        "Rs": Rs,
        # outputs blank initially 
        "Vbi": "",
        "Wn": "",
        "Wp": "",
        "Id": "",
        "Vterm": "",
        "Ileak": "",
    }
    return render(request, "diode/diode.html", context)

@csrf_exempt
def calculate(request):
    if request.method == "POST":
        q = 1.6e-19
        k = 1.38e-23         # Boltzmann constant (J/K)
        T = 300              # temperature (K)
        eps_si = 11.7 * 8.85e-14  # F/cm
        Vt_volts = 0.025          # numeric mV
        a_cm = 5.43e-8            # silicon lattice constant in cm        
        n=1.0
        Is=1e-12         
        Rs=10

        diode_name = request.POST.get("diode", "1N4148") 
        constants = parse_constants(diode_name)        
        Nd_cm3 = safe_float(request.POST.get("Nd"), constants["Nd"])          
        Na_cm3 = safe_float(request.POST.get("Na"), constants["Na"]) 
        ni_cm3 = safe_float(request.POST.get("ni"), constants["ni"])

        if "ni" in request.POST:            
            Vbi_volts = (Vt_volts * math.log((Na_cm3 * Nd_cm3) / (ni_cm3 * ni_cm3)))*1000
            return JsonResponse({"Vbi": Vbi_volts})

        if "Vapp" in request.POST:            
            Vbi_volts = safe_float(request.POST.get("Vbi"), default=0.7)
            Vapp_volts = safe_float(request.POST.get("Vapp"), default=0.0)
            W_total_cm = math.sqrt((2 * eps_si * (Vbi_volts + Vapp_volts) / q) *
                                   ((Na_cm3 + Nd_cm3) / (Na_cm3 * Nd_cm3)))
            Wn_um = (W_total_cm * Na_cm3 / (Na_cm3 + Nd_cm3))/a_cm           
            return JsonResponse({"Wn": Wn_um})

        if "Wn" in request.POST:            
            Vbi_volts = safe_float(request.POST.get("Vbi"), default=0.7)
            Vapp_volts = safe_float(request.POST.get("Vapp"), default=0.0)
            W_total_cm = math.sqrt((2 * eps_si * (Vbi_volts + Vapp_volts) / q) *
                                   ((Na_cm3 + Nd_cm3) / (Na_cm3 * Nd_cm3)))
            Wp_um = (W_total_cm * Nd_cm3 / (Na_cm3 + Nd_cm3))/a_cm           
            return JsonResponse({"Wp": Wp_um})
        
        if "Id" in request.POST:
            Vt = (k * T) / q
            Vbi_volts = safe_float(request.POST.get("Vbi"), default=0.7)
            Vapp_volts = safe_float(request.POST.get("Vapp"), default=0.0)
            Vj = Vbi_volts - Vapp_volts
            Id = Is * (math.exp(Vj / (n * Vt)) - 1)
            Vterm = Id * Rs 
            Ileak = Id
            return JsonResponse({"Id": Id, "Vterm": Vterm, "Ileak": Ileak}) 


    return JsonResponse({"error": "Invalid request"}, status=400)


def diode_constants(request):
    diode_name = request.GET.get("diode", "1N4148")
    constants = parse_constants(diode_name)
    return JsonResponse(constants)
