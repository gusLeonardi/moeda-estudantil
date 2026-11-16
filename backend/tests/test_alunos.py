from tests.test_moedas import professor_payload, provisionar_professor


def aluno_payload(endereco, **overrides):
    data = {"nome":"Ana Souza","email":"ana@pucminas.br","senha":"Senha-Forte-Teste-123!","cpf":"52998224725","rg":"MG1234567","curso":"Engenharia de Software","instituicao_id":1,"endereco":endereco}
    data.update(overrides); return data


def test_crud_aluno(client, endereco):
    created = client.post("/api/alunos", json=aluno_payload(endereco))
    assert created.status_code == 201
    entity_id = created.json()["id"]
    assert created.json()["saldo"] == "0.00"
    assert client.get("/api/alunos").json()[0]["nome"] == "Ana Souza"
    assert client.get(f"/api/alunos/{entity_id}").status_code == 200
    update = aluno_payload(endereco, nome="Ana Carolina", email="carolina@pucminas.br")
    update.pop("cpf")
    response = client.put(f"/api/alunos/{entity_id}", json=update)
    assert response.status_code == 200 and response.json()["nome"] == "Ana Carolina"
    assert client.delete(f"/api/alunos/{entity_id}").status_code == 204
    assert client.get(f"/api/alunos/{entity_id}").status_code == 401


def test_duplicidades_e_instituicao(client, endereco):
    assert client.post("/api/alunos", json=aluno_payload(endereco)).status_code == 201
    assert client.post("/api/alunos", json=aluno_payload(endereco, email="outra@pucminas.br")).status_code == 409
    assert client.post("/api/alunos", json=aluno_payload(endereco, cpf="11144477735")).status_code == 409
    assert client.post("/api/alunos", json=aluno_payload(endereco, email="nova@pucminas.br", cpf="11144477735", instituicao_id=999)).status_code == 404


def test_cadastro_publico_de_aluno_recusa_jwt_autenticado(client, endereco):
    original = client.post("/api/alunos", json=aluno_payload(endereco))
    assert original.status_code == 201
    token = client.post("/api/auth/login", json={"email": "ana@pucminas.br", "senha": "Senha-Forte-Teste-123!"}).json()["access_token"]

    second = aluno_payload(endereco, nome="Outra Aluna", email="outra@pucminas.br", cpf="11144477735")
    assert client.post("/api/alunos", json=second, headers={"Authorization": f"Bearer {token}"}).status_code == 403
    assert client.post("/api/alunos", json=second, headers={"Authorization": "Bearer token-invalido"}).status_code == 401
    own_records = client.get("/api/alunos", headers={"Authorization": f"Bearer {token}"}).json()
    assert [record["id"] for record in own_records] == [original.json()["id"]]


def test_busca_aluno(client, endereco):
    client.post("/api/alunos", json=aluno_payload(endereco))
    assert len(client.get("/api/alunos?busca=ana").json()) == 1
    assert len(client.get("/api/alunos?busca=529.982.247-25").json()) == 1
    assert len(client.get("/api/alunos?busca=software").json()) == 1
    assert len(client.get("/api/alunos?busca=PUC").json()) == 1
    assert client.get("/api/alunos?busca=inexistente").json() == []


def test_validacoes_e_campos_protegidos(client, endereco):
    invalid = aluno_payload(endereco, cpf="12345678901")
    assert client.post("/api/alunos", json=invalid).status_code == 422
    assert client.post("/api/alunos", json=aluno_payload(endereco, email="invalido")).status_code == 422

    created = client.post("/api/alunos", json=aluno_payload(endereco)).json()
    update = aluno_payload(endereco)
    update.pop("cpf")
    update["saldo"] = "999.00"
    update["cpf"] = "11144477735"
    assert client.put(f"/api/alunos/{created['id']}", json=update).status_code == 200
    persisted = client.get(f"/api/alunos/{created['id']}").json()
    assert persisted["cpf"] == "52998224725"
    assert persisted["saldo"] == "0.00"


def test_indicadores_dashboard(client, endereco):
    assert client.get("/api/dashboard/indicadores").status_code == 401
    client.post("/api/alunos", json=aluno_payload(endereco))
    assert client.get("/api/dashboard/indicadores").status_code == 403
    provisionar_professor(client, professor_payload(endereco))
    token = client.post("/api/auth/login", json={"email": "professor@example.com", "senha": "Senha-Forte-Teste-123!"}).json()["access_token"]
    response = client.get("/api/dashboard/indicadores", headers={"Authorization": f"Bearer {token}"})
    assert response.json() == {"total_alunos": 1}


def test_registros_inexistentes(client, endereco):
    update = aluno_payload(endereco)
    update.pop("cpf")
    assert client.get("/api/alunos/999").status_code == 401
    assert client.put("/api/alunos/999", json=update).status_code == 401
    assert client.delete("/api/alunos/999").status_code == 401
