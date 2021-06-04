async function fetchApi(route, parameter = '', parameterValue = '') {
    let response;

    if (parameter === '' && parameterValue === '') {
        response = await fetch('http://localhost/api/' + route);
    } else {
        response = await fetch('http://localhost/api/' + route + '?' + parameter + '=' + parameterValue);
    }

    return await response.json();
}
