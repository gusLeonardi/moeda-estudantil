# Fluxos de moedas, vantagens e resgates

## Limite de segurança

Esta versão não possui autenticação nem autorização. Cadastro de professores, transferências, gestão de vantagens e resgates são fluxos administrativos de demonstração e devem permanecer restritos ao ambiente local.

## Transferência do professor para o aluno

1. A API valida professor, aluno, quantidade inteira positiva e justificativa.
2. O repository executa um `UPDATE` condicional: debita apenas quando `saldo >= quantidade`.
3. O saldo do aluno é creditado na mesma sessão.
4. A transferência é registrada com data, valor e justificativa.
5. Um único `commit` confirma todas as alterações.
6. Qualquer falha provoca `rollback`.

O débito condicional protege contra duas requisições concorrentes consumirem o mesmo saldo.

Diagrama editável: [fluxo-transferencia.mmd](fluxo-transferencia.mmd).

## Extratos

O extrato do professor apresenta saldo, total distribuído e transferências em ordem decrescente de data. O extrato do aluno combina recebimentos e resgates, também do mais recente para o mais antigo.

## Resgate

1. O aluno e a vantagem precisam existir.
2. A vantagem deve estar ativa.
3. O débito do aluno ocorre com `UPDATE` condicional.
4. O resgate registra custo histórico, empresa, vantagem e cupom.
5. `idempotency_key` impede processamento duplicado do mesmo pedido.
6. `codigo_cupom` é único.
7. A interface apresenta o cupom após o commit.

Vantagens não são excluídas pelo fluxo administrativo; são desativadas. As chaves estrangeiras com `RESTRICT` preservam transferências e resgates históricos.

Diagrama editável: [fluxo-resgate.mmd](fluxo-resgate.mmd).

## E-mail

Não existe infraestrutura de e-mail no projeto. Nenhum envio é simulado. O cupom permanece funcional na interface, e a notificação por e-mail fica documentada como pendência.
