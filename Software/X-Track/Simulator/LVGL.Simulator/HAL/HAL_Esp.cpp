#include "HAL.h"
#include <uv.h>
#include <stdio.h>
#include <stdlib.h>
#include <cjson/cJSON.h>

static uv_loop_t * esp_loop;
static uv_tcp_t esp_socket;
static uv_connect_t esp_connect_req;

void HAL::esp_init()
{
    esp_loop = uv_default_loop();
    uv_tcp_init(esp_loop, &esp_socket);

    struct sockaddr_in dest;
    uv_ip4_addr("127.0.0.1", 12345, &dest);

    uv_tcp_connect(&esp_connect_req, &esp_socket, (struct sockaddr *)&dest, HAL::esp_on_connect);
}

void HAL::esp_update()
{
    // Ejecutar eventos de libuv usando UV_RUN_NOWAIT
    uv_run(esp_loop, UV_RUN_NOWAIT);
}

void HAL::esp_on_connect(uv_connect_t *req, int status) {
    //esp_api_client_t *esp_api = (esp_api_client_t *)req->handle;

    if (status < 0) {
        fprintf(stderr, "Error en la conexión al servidor: %s\n", uv_strerror(status));
    } else {
        // Asociar esp_api con stream->data antes de llamar a uv_read_start
        //esp_api->socket.data = esp_api;

        uv_read_start((uv_stream_t *)&esp_socket, HAL::esp_alloc_buffer, HAL::esp_on_read);
    }
}

void HAL::esp_on_read(uv_stream_t *stream, ssize_t nread, const uv_buf_t *buf) {
    //esp_api_client_t *esp_api = (esp_api_client_t *)stream->data;
    
    if (nread < 0) {
        if (nread == UV_EOF) {
            // El servidor cerró la conexión
            fprintf(stderr, "Conexión cerrada por el servidor\n");
        } else {
            fprintf(stderr, "Error al leer datos: %s\n", uv_strerror(nread));
        }
    } else if (nread > 0) {
        // Procesar la respuesta del servidor
        HAL::esp_process_response(buf->base);
    }

    // Liberar el búfer después de procesar los datos
    free(buf->base);
}

void HAL::esp_alloc_buffer(uv_handle_t *handle, size_t suggested_size, uv_buf_t *buf) {
    *buf = uv_buf_init((char*)malloc(suggested_size), suggested_size);
}

void HAL::esp_process_response(const char *response) {
    cJSON *json = cJSON_Parse(response);
    if (json != NULL) {
        fprintf(stderr, "%s\n", response);
        cJSON_Delete(json);
    } else {
        fprintf(stderr, "Error al analizar JSON\n");      
    }
}