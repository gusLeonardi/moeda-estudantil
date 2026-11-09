def aluno_payload(endereco, **overrides):
    data = {
        "nome": "Aluno Demo",
        "email": "aluno@example.com",
        "cpf": "52998224725",
        "rg": "MG1234567",
        "curso": "Engenharia de Software",
        "instituicao_id": 1,
        "endereco": endereco,
    }
    data.update(overrides)
    return data


def professor_payload(endereco, **overrides):
    data = {
        "nome": "Professor Demo",
        "email": "professor@example.com",
        "cpf": "11144477735",
        "departamento": "Computação",
        "instituicao_id": 1,
        "endereco": endereco,
    }
    data.update(overrides)
    return data


def criar_participantes(client, endereco):
    professor = client.post("/api/professores", json=professor_payload(endereco))
    aluno = client.post("/api/alunos", json=aluno_payload(endereco))
    assert professor.status_code == 201
    assert aluno.status_code == 201
    return professor.json(), aluno.json()


def test_crud_professor_e_saldo_inicial(client, endereco):
    response = client.post("/api/professores", json=professor_payload(endereco))
    assert response.status_code == 201
    professor = response.json()
    assert professor["saldo"] == "1000.00"
    assert client.get("/api/professores").json()[0]["cpf"] == "11144477735"

    update = professor_payload(endereco, nome="Professor Atualizado", email="atualizado@example.com")
    update.pop("cpf")
    update["saldo"] = "999999.00"
    update["cpf"] = "52998224725"
    changed = client.put(f"/api/professores/{professor['id']}", json=update)
    assert changed.status_code == 200
    assert changed.json()["nome"] == "Professor Atualizado"
    assert changed.json()["cpf"] == "11144477735"
    assert changed.json()["saldo"] == "1000.00"


def test_professor_duplicado_e_instituicao_inexistente(client, endereco):
    assert client.post("/api/professores", json=professor_payload(endereco)).status_code == 201
    duplicate = professor_payload(endereco, email="outro@example.com")
    assert client.post("/api/professores", json=duplicate).status_code == 409
    missing = professor_payload(endereco, cpf="52998224725", email="novo@example.com", instituicao_id=999)
    assert client.post("/api/professores", json=missing).status_code == 404


def test_transferencia_e_extratos(client, endereco):
    professor, aluno = criar_participantes(client, endereco)
    transfer = client.post(
        "/api/moedas/transferencias",
        json={
            "professor_id": professor["id"],
            "aluno_id": aluno["id"],
            "quantidade": 150,
            "justificativa": "Excelente participação no projeto",
        },
    )
    assert transfer.status_code == 201
    assert transfer.json()["quantidade"] == "150.00"

    professor_after = client.get(f"/api/professores/{professor['id']}").json()
    aluno_after = client.get(f"/api/alunos/{aluno['id']}").json()
    assert professor_after["saldo"] == "850.00"
    assert aluno_after["saldo"] == "150.00"

    extrato_professor = client.get(f"/api/professores/{professor['id']}/extrato").json()
    assert extrato_professor["total_distribuido"] == "150.00"
    assert extrato_professor["transferencias"][0]["aluno_nome"] == aluno["nome"]

    extrato_aluno = client.get(f"/api/alunos/{aluno['id']}/extrato").json()
    assert extrato_aluno["saldo"] == "150.00"
    assert extrato_aluno["movimentos"][0]["professor_nome"] == professor["nome"]


def test_transferencia_invalida_nao_altera_saldos(client, endereco):
    professor, aluno = criar_participantes(client, endereco)
    for quantidade in (0, -1):
        assert client.post(
            "/api/moedas/transferencias",
            json={"professor_id": professor["id"], "aluno_id": aluno["id"], "quantidade": quantidade, "justificativa": "Teste"},
        ).status_code == 422
    assert client.post(
        "/api/moedas/transferencias",
        json={"professor_id": professor["id"], "aluno_id": aluno["id"], "quantidade": 10, "justificativa": "   "},
    ).status_code == 422

    insufficient = client.post(
        "/api/moedas/transferencias",
        json={"professor_id": professor["id"], "aluno_id": aluno["id"], "quantidade": 1001, "justificativa": "Valor excessivo"},
    )
    assert insufficient.status_code == 409
    assert client.get(f"/api/professores/{professor['id']}").json()["saldo"] == "1000.00"
    assert client.get(f"/api/alunos/{aluno['id']}").json()["saldo"] == "0.00"
    assert client.get(f"/api/professores/{professor['id']}/extrato").json()["transferencias"] == []


def test_transferencias_concorrentes_nao_deixam_saldo_negativo(client, endereco):
    from concurrent.futures import ThreadPoolExecutor

    professor, aluno = criar_participantes(client, endereco)
    payload = {
        "professor_id": professor["id"],
        "aluno_id": aluno["id"],
        "quantidade": 600,
        "justificativa": "Tentativa concorrente",
    }
    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(lambda _: client.post("/api/moedas/transferencias", json=payload), range(2)))
    assert sorted(response.status_code for response in responses) == [201, 409]
    assert client.get(f"/api/professores/{professor['id']}").json()["saldo"] == "400.00"
    assert client.get(f"/api/alunos/{aluno['id']}").json()["saldo"] == "600.00"
