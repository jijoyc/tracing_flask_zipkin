from flask import Flask, request
import requests
from py_zipkin.zipkin import zipkin_span, create_http_headers_for_new_span, ZipkinAttrs, Kind, zipkin_client_span
from py_zipkin.request_helpers import create_http_headers
from py_zipkin.encoding import Encoding
from flask_zipkin import Zipkin

app = Flask("api_01")
zipkin = Zipkin(app, sample_rate=10)
app.config['ZIPKIN_DSN'] = "http://127.0.0.1:9411/api/v1/spans"
print(app.name)



def default_handler(encoded_span):
    body = encoded_span

    # decoded = _V1ThriftDecoder.decode_spans(encoded_span)
    app.logger.debug("body %s", body)

    # return requests.post(
    #     "http://zipkin:9411/api/v1/spans",
    #     data=body,
    #     headers={'Content-Type': 'application/x-thrift'},
    # )

    return requests.post(
        "http://zipkin:9411/api/v2/spans",
        data=body,
        headers={'Content-Type': 'application/json'},
    )


@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())


# @zipkin_client_span(service_name='api_01', span_name='call_api_02')
def call_api_02():
    headers = create_http_headers_for_new_span()
    requests.get('http://api_02:5000/', headers=headers)
    return 'OK'


# @zipkin_client_span(service_name='api_01', span_name='call_api_03_FROM_01')
def call_api_03():
    headers = create_http_headers_for_new_span()
    requests.get('http://api_03:5000/', headers=headers)
    return 'OK'


@app.route('/')
def index():
    with zipkin_span(
        service_name='api_01',
        span_name='index_api_01',
        transport_handler=default_handler,
        port=5000,
        sample_rate=100,
        encoding=Encoding.V2_JSON
    ):  
        print(app.name)
        call_api_02()
        call_api_03()
    return 'OK', 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)



