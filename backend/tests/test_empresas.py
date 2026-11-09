def empresa_payload(endereco, **overrides):
    data = {"nome":"Livraria Campus","email":"contato@livraria.com","cnpj":"11222333000181","telefone":"3133334444","endereco":endereco}
    data.update(overrides); return data


def test_crud_empresa(client, endereco):
    created = client.post("/api/empresas", json=empresa_payload(endereco))
    assert created.status_code == 201
    entity_id = created.json()["id"]
    assert client.get("/api/empresas").json()[0]["cnpj"] == "11222333000181"
    update = empresa_payload(endereco, nome="Livraria Universitária", email="novo@livraria.com")
    update.pop("cnpj")
    response = client.put(f"/api/empresas/{entity_id}", json=update)
    assert response.status_code == 200 and response.json()["nome"] == "Livraria Universitária"
    assert client.delete(f"/api/empresas/{entity_id}").status_code == 204
    assert client.get(f"/api/empresas/{entity_id}").status_code == 404


def test_cnpj_e_email_duplicados(client, endereco):
    assert client.post("/api/empresas", json=empresa_payload(endereco)).status_code == 201
    assert client.post("/api/empresas", json=empresa_payload(endereco, email="outra@empresa.com")).status_code == 409
    assert client.post("/api/empresas", json=empresa_payload(endereco, cnpj="11444777000161")).status_code == 409


def test_validacoes_busca_e_campos_protegidos(client, endereco):
    assert client.post("/api/empresas", json=empresa_payload(endereco, cnpj="12345678000199")).status_code == 422
    created = client.post("/api/empresas", json=empresa_payload(endereco)).json()
    assert len(client.get("/api/empresas?busca=contato@livraria.com").json()) == 1
    assert len(client.get("/api/empresas?busca=11.222.333/0001-81").json()) == 1

    update = empresa_payload(endereco)
    update.pop("cnpj")
    update["cnpj"] = "11444777000161"
    assert client.put(f"/api/empresas/{created['id']}", json=update).status_code == 200
    assert client.get(f"/api/empresas/{created['id']}").json()["cnpj"] == "11222333000181"


def test_empresa_inexistente(client, endereco):
    update = empresa_payload(endereco)
    update.pop("cnpj")
    assert client.get("/api/empresas/999").status_code == 404
    assert client.put("/api/empresas/999", json=update).status_code == 404
    assert client.delete("/api/empresas/999").status_code == 404
