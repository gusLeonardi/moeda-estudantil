def aluno_payload(endereco, **overrides):
    data = {"nome":"Ana Souza","email":"ana@pucminas.br","cpf":"12345678901","rg":"MG1234567","curso":"Engenharia de Software","instituicao_id":1,"endereco":endereco}
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
    assert client.get(f"/api/alunos/{entity_id}").status_code == 404


def test_duplicidades_e_instituicao(client, endereco):
    assert client.post("/api/alunos", json=aluno_payload(endereco)).status_code == 201
    assert client.post("/api/alunos", json=aluno_payload(endereco, email="outra@pucminas.br")).status_code == 409
    assert client.post("/api/alunos", json=aluno_payload(endereco, cpf="98765432100")).status_code == 409
    assert client.post("/api/alunos", json=aluno_payload(endereco, email="nova@pucminas.br", cpf="98765432100", instituicao_id=999)).status_code == 404


def test_busca_aluno(client, endereco):
    client.post("/api/alunos", json=aluno_payload(endereco))
    assert len(client.get("/api/alunos?busca=ana").json()) == 1
    assert client.get("/api/alunos?busca=inexistente").json() == []
