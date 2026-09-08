from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .analyzer import get_integrated_market_strategy

@require_GET
def integrated_strategy_api(request):
    try:
        n = float(request.GET.get('n', 90))
        p = float(request.GET.get('p', 42))
        k = float(request.GET.get('k', 43))
        temp = float(request.GET.get('temperature', 20.8))
        hum = float(request.GET.get('humidity', 82.0))
        ph = float(request.GET.get('ph', 6.5))
        rain = float(request.GET.get('rainfall', 202.9))
        
        result = get_integrated_market_strategy(n, p, k, temp, hum, ph, rain)
        return JsonResponse({'status': 'success', 'data': result})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
