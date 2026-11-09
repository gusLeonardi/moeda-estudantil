from tests.test_moedas import aluno_payload, criar_participantes


def empresa_payload(endereco, **overrides):
    data = {
        "nome": "Empresa Demo",
        "email": "empresa@example.com",
        "cnpj": "11222333000181",
        "telefone": "3133334444",
        "endereco": endereco,
    }
    data.update(overrides)
    return data


def criar_empresa_vantagem(client, endereco, custo=100, ativa=True):
    empresa = client.post("/api/empresas", json=empresa_payload(endereco))
    assert empresa.status_code == 201
    vantagem = client.post(
        "/api/vantagens",
        json={
            "empresa_id": empresa.json()["id"],
            "nome": "Desconto Demo",
            "descricao": "Benefício fictício para testes",
            "custo": custo,
            "imagem_url": "/images/vantagem-demo.png",
            "ativa": ativa,
        },
    )
    assert vantagem.status_code == 201
    return empresa.json(), vantagem.json()


def creditar_aluno(client, professor_id, aluno_id, quantidade):
    response = client.post(
        "/api/moedas/transferencias",
        json={
            "professor_id": professor_id,
            "aluno_id": aluno_id,
            "quantidade": quantidade,
            "justificativa": "Crédito para teste de resgate",
        },
    )
    assert response.status_code == 201


def test_crud_e_desativacao_vantagem(client, endereco):
    empresa, vantagem = criar_empresa_vantagem(client, endereco)
    assert client.get("/api/vantagens?apenas_ativas=true").json()[0]["empresa_nome"] == empresa["nome"]
    updated = client.put(
        f"/api/vantagens/{vantagem['id']}",
        json={
            "nome": "Desconto Atualizado",
            "descricao": "Descrição atualizada",
            "custo": 120,
            "imagem_url": None,
            "ativa": True,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["custo"] == "120.00"
    disabled = client.post(f"/api/vantagens/{vantagem['id']}/desativar")
    assert disabled.status_code == 200 and disabled.json()["ativa"] is False
    assert client.get("/api/vantagens?apenas_ativas=true").json() == []


def test_resgate_valido_cupom_extrato_e_idempotencia(client, endereco):
    professor, aluno = criar_participantes(client, endereco)
    _, vantagem = criar_empresa_vantagem(client, endereco, custo=100)
    creditar_aluno(client, professor["id"], aluno["id"], 300)

    payload = {"aluno_id": aluno["id"], "vantagem_id": vantagem["id"], "idempotency_key": "pedido-demo-0001"}
    first = client.post("/api/resgates", json=payload)
    second = client.post("/api/resgates", json=payload)
    assert first.status_code == 201 and second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
    assert first.json()["codigo_cupom"] == second.json()["codigo_cupom"]
    assert len(first.json()["codigo_cupom"]) == 12
    assert client.get(f"/api/alunos/{aluno['id']}").json()["saldo"] == "200.00"

    extrato = client.get(f"/api/alunos/{aluno['id']}/extrato").json()
    assert extrato["movimentos"][0]["tipo"] == "RESGATE"
    assert extrato["movimentos"][0]["codigo_cupom"] == first.json()["codigo_cupom"]

    third = client.post(
        "/api/resgates",
        json={"aluno_id": aluno["id"], "vantagem_id": vantagem["id"], "idempotency_key": "pedido-demo-0002"},
    )
    assert third.status_code == 201
    assert third.json()["codigo_cupom"] != first.json()["codigo_cupom"]


def test_resgate_inativo_ou_sem_saldo_nao_debita(client, endereco):
    professor, aluno = criar_participantes(client, endereco)
    _, vantagem = criar_empresa_vantagem(client, endereco, custo=200)
    creditar_aluno(client, professor["id"], aluno["id"], 100)

    insufficient = client.post(
        "/api/resgates",
        json={"aluno_id": aluno["id"], "vantagem_id": vantagem["id"], "idempotency_key": "pedido-sem-saldo"},
    )
    assert insufficient.status_code == 409
    assert client.get(f"/api/alunos/{aluno['id']}").json()["saldo"] == "100.00"

    client.post(f"/api/vantagens/{vantagem['id']}/desativar")
    inactive = client.post(
        "/api/resgates",
        json={"aluno_id": aluno["id"], "vantagem_id": vantagem["id"], "idempotency_key": "pedido-inativo"},
    )
    assert inactive.status_code == 409
    assert client.get(f"/api/alunos/{aluno['id']}").json()["saldo"] == "100.00"


def test_debitos_competindo_nao_geram_saldo_negativo(client, endereco):
    from concurrent.futures import ThreadPoolExecutor

    professor, aluno = criar_participantes(client, endereco)
    _, vantagem = criar_empresa_vantagem(client, endereco, custo=80)
    creditar_aluno(client, professor["id"], aluno["id"], 100)

    payloads = [
        {"aluno_id": aluno["id"], "vantagem_id": vantagem["id"], "idempotency_key": "debito-competidor-a"},
        {"aluno_id": aluno["id"], "vantagem_id": vantagem["id"], "idempotency_key": "debito-competidor-b"},
    ]
    with ThreadPoolExecutor(max_workers=2) as executor:
        first, second = executor.map(lambda payload: client.post("/api/resgates", json=payload), payloads)
    assert sorted([first.status_code, second.status_code]) == [201, 409]
    assert client.get(f"/api/alunos/{aluno['id']}").json()["saldo"] == "20.00"
