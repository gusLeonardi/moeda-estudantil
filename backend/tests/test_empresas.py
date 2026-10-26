def empresa_payload(endereco, **overrides):
    data = {"nome":"Livraria Campus","email":"contato@livraria.com","cnpj":"12345678000199","telefone":"3133334444","endereco":endereco}
    data.update(overrides); return data


def test_crud_empresa(client, endereco):
    created = client.post("/api/empresas", json=empresa_payload(endereco))
    assert created.status_code == 201
    entity_id = created.json()["id"]
    assert client.get("/api/empresas").json()[0]["cnpj"] == "12345678000199"
    update = empresa_payload(endereco, nome="Livraria Universitária", email="novo@livraria.com")
    update.pop("cnpj")
    response = client.put(f"/api/empresas/{entity_id}", json=update)
    assert response.status_code == 200 and response.json()["nome"] == "Livraria Universitária"
    assert client.delete(f"/api/empresas/{entity_id}").status_code == 204
    assert client.get(f"/api/empresas/{entity_id}").status_code == 404


def test_cnpj_e_email_duplicados(client, endereco):
    assert client.post("/api/empresas", json=empresa_payload(endereco)).status_code == 201
    assert client.post("/api/empresas", json=empresa_payload(endereco, email="outra@empresa.com")).status_code == 409
    assert client.post("/api/empresas", json=empresa_payload(endereco, cnpj="98765432000188")).status_code == 409
