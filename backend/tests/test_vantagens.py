from tests.test_moedas import aluno_payload, criar_participantes


def empresa_payload(endereco, **overrides):
    data = {
        "nome": "Empresa Demo",
        "email": "empresa@example.com",
        "senha": "Senha-Forte-Teste-123!",
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
            "imagem_url": "https://images.example.test/vantagem-demo.png",
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


def test_vantagem_requires_public_https_image_url(client, endereco):
    company = client.post("/api/empresas", json=empresa_payload(endereco)).json()
    payload = {
        "empresa_id": company["id"], "nome": "Oferta segura", "descricao": "Beneficio com imagem",
        "custo": 5, "ativa": True,
    }
    for invalid_url in ("/images/item.png", "http://images.example.test/item.png", "https://127.0.0.1/item.png"):
        assert client.post("/api/vantagens", json={**payload, "imagem_url": invalid_url}).status_code == 422
    valid = client.post("/api/vantagens", json={**payload, "imagem_url": "https://cdn.example.test/item.png"})
    assert valid.status_code == 201


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


def criar_empresa_autenticada(client, endereco, email, nome, cnpj):
    created = client.post("/api/empresas", json=empresa_payload(endereco, nome=nome, email=email, cnpj=cnpj))
    assert created.status_code == 201
    login = client.post("/api/auth/login", json={"email": email, "senha": "Senha-Forte-Teste-123!"})
    assert login.status_code == 200
    return created.json(), {"Authorization": f"Bearer {login.json()['access_token']}"}


def payload_vantagem(nome):
    return {
        "nome": nome,
        "descricao": f"Benefício da {nome}",
        "custo": 10,
        "imagem_url": "https://images.example.test/oferta.png",
        "ativa": True,
    }


def test_isolamento_de_vantagens_entre_empresas(client, endereco):
    empresa_a, headers_a = criar_empresa_autenticada(client, endereco, "a@example.com", "Empresa A", "11222333000181")
    empresa_b, headers_b = criar_empresa_autenticada(client, endereco, "b@example.com", "Empresa B", "11444777000161")

    vantagem_a = client.post("/api/vantagens", json={**payload_vantagem("Vantagem A"), "empresa_id": empresa_b["id"]}, headers=headers_a)
    vantagem_b = client.post("/api/vantagens", json={**payload_vantagem("Vantagem B"), "empresa_id": empresa_a["id"]}, headers=headers_b)
    assert vantagem_a.status_code == vantagem_b.status_code == 201
    a, b = vantagem_a.json(), vantagem_b.json()
    assert a["empresa_id"] == empresa_a["id"]
    assert b["empresa_id"] == empresa_b["id"]

    assert {x["id"] for x in client.get("/api/vantagens/minhas?empresa_id=" + str(empresa_b["id"]), headers=headers_a).json()} == {a["id"]}
    assert {x["id"] for x in client.get("/api/vantagens/minhas", headers=headers_b).json()} == {b["id"]}
    assert {x["id"] for x in client.get("/api/vantagens?empresa_id=" + str(empresa_b["id"]), headers=headers_a).json()} == {a["id"]}

    update = {"nome": "Atualizada pela A", "descricao": "Atualização permitida", "custo": 11, "imagem_url": "https://images.example.test/updated.png", "ativa": True}
    assert client.put(f"/api/vantagens/{a['id']}", json=update, headers=headers_a).status_code == 200
    assert client.put(f"/api/vantagens/{b['id']}", json=update, headers=headers_a).status_code == 404
    assert client.put(f"/api/vantagens/{a['id']}", json=update, headers=headers_b).status_code == 404
    assert client.post(f"/api/vantagens/{b['id']}/desativar", headers=headers_a).status_code == 404
    assert client.post(f"/api/vantagens/{a['id']}/ativar", headers=headers_b).status_code == 404
    assert client.post(f"/api/vantagens/{b['id']}/ativar", headers=headers_a).status_code == 404
    assert client.post(f"/api/vantagens/{a['id']}/desativar", headers=headers_b).status_code == 404
    assert client.delete(f"/api/vantagens/{b['id']}", headers=headers_a).status_code == 404
    assert client.delete(f"/api/vantagens/{a['id']}", headers=headers_b).status_code == 404
    assert client.post(f"/api/vantagens/{a['id']}/desativar", headers=headers_a).status_code == 200
    assert client.post(f"/api/vantagens/{a['id']}/ativar", headers=headers_a).status_code == 200
    assert client.delete(f"/api/vantagens/{a['id']}", headers=headers_a).status_code == 204


def test_catalogo_de_aluno_e_cupom_escopado_a_empresa_dona(client, endereco):
    empresa_a, headers_a = criar_empresa_autenticada(client, endereco, "cupons-a@example.com", "Empresa A", "11222333000181")
    empresa_b, headers_b = criar_empresa_autenticada(client, endereco, "cupons-b@example.com", "Empresa B", "11444777000161")
    vantagem_a = client.post("/api/vantagens", json=payload_vantagem("Oferta A"), headers=headers_a).json()
    vantagem_b = client.post("/api/vantagens", json=payload_vantagem("Oferta B"), headers=headers_b).json()

    professor, aluno = criar_participantes(client, endereco)
    creditar_aluno(client, professor["id"], aluno["id"], 100)
    catalog_headers = client.post("/api/auth/login", json={"email": "aluno@example.com", "senha": "Senha-Forte-Teste-123!"})
    assert catalog_headers.status_code == 200
    aluno_headers = {"Authorization": f"Bearer {catalog_headers.json()['access_token']}"}
    catalog = client.get("/api/vantagens/catalogo?empresa_id=" + str(empresa_a["id"]), headers=aluno_headers)
    assert catalog.status_code == 200
    assert {item["id"] for item in catalog.json()} == {vantagem_a["id"], vantagem_b["id"]}
    assert client.get(f"/api/vantagens/{vantagem_a['id']}", headers=aluno_headers).status_code == 200

    resgate_a = client.post("/api/resgates", json={"aluno_id": aluno["id"], "vantagem_id": vantagem_a["id"], "idempotency_key": "cupom-isolado-a"})
    resgate_b = client.post("/api/resgates", json={"aluno_id": aluno["id"], "vantagem_id": vantagem_b["id"], "idempotency_key": "cupom-isolado-b"})
    assert resgate_a.status_code == resgate_b.status_code == 201
    code_a, code_b = resgate_a.json()["codigo_cupom"], resgate_b.json()["codigo_cupom"]

    own_coupon = client.post("/api/cupons/consultar", json={"empresa_id": empresa_b["id"], "codigo_cupom": code_a}, headers=headers_a)
    assert own_coupon.status_code == 200 and own_coupon.json()["empresa_id"] == empresa_a["id"]
    assert client.post("/api/cupons/consultar", json={"empresa_id": empresa_a["id"], "codigo_cupom": code_b}, headers=headers_a).status_code == 404
    assert client.post("/api/cupons/consultar", json={"codigo_cupom": code_a}, headers=headers_b).status_code == 404
    assert client.post("/api/cupons/validar", json={"empresa_id": empresa_a["id"], "codigo_cupom": code_b}, headers=headers_a).status_code == 404
    validated = client.post("/api/cupons/validar", json={"empresa_id": empresa_a["id"], "codigo_cupom": code_b}, headers=headers_b)
    assert validated.status_code == 200 and validated.json()["empresa_id"] == empresa_b["id"]

    assert client.delete(f"/api/vantagens/{vantagem_a['id']}", headers=headers_a).status_code == 409
    assert client.post("/api/cupons/consultar", json={"codigo_cupom": code_a}, headers=headers_a).status_code == 200
