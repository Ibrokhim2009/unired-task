from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from jsonrpcserver import dispatch
import json
import transfer.rpc




@csrf_exempt
def jsonrpc_view(request):
    print("Kelyabdimi o'zi?", request.method)
    if request.method == 'POST':
        try:
            raw_body = request.body.decode('utf-8')
            response = dispatch(raw_body)
            print("\n\n\n\n javobi  \n\n\n", response)

            return HttpResponse(response, content_type='application/json')

        except json.JSONDecodeError as e:
            return HttpResponse(
                json.dumps({'error': {'code': -32700, 'message': 'Parse error', 'data': str(e)}}),
                content_type='application/json',
                status=400
            )

        except UnicodeDecodeError as e:
            return HttpResponse(
                json.dumps({'error': {'code': -32700, 'message': 'Invalid encoding', 'data': str(e)}}),
                content_type='application/json',
                status=400
            )

    return HttpResponse(
        json.dumps({'error': {'code': -32601, 'message': 'Method not found'}}),
        content_type='application/json',
        status=405
    )

