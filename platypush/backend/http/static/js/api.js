function execute(request, timeout=60000) {
    var additionalPayload = {};

    if (!('target' in request) || !request['target']) {
        request['target'] = 'localhost';
    }

    if (!('type' in request) || !request['type']) {
        request['type'] = 'request';
    }

    if (window.config.token) {
        additionalPayload.headers = {
            'X-Token': window.config.token
        };
    }

    if (timeout) {
        additionalPayload.timeout = timeout;
    }

    return new Promise((resolve, reject) => {
        axios.post('/execute', request, additionalPayload)
            .then((response) => {
                response = response.data.response;
                if (!response.errors.length) {
                    resolve(response.output);
                } else {
                    const error = response.errors[0];
                    createNotification({
                        text: error,
                        error: true,
                    });

                    reject(error);
                }
            })
            .catch((error) => {
                createNotification({
                    text: error,
                    error: true,
                });

                reject(error);
            });
    });
}

function request(action, args={}, timeout=60000) {
    return execute({
        type: 'request',
        action: action,
        args: args,
    });
}

