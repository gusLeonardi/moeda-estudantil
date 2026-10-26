# Modelo Entidade-Relacionamento — Sprint 2

O modelo implementado usa `usuarios` como supertipo para identidade, e-mail e a futura autenticação. `alunos` e `empresas_parceiras` são especializações 1:0..1 com chave primária também estrangeira. Cada usuário tem exatamente um endereço e cada aluno pertence a uma instituição.

## Restrições

- `usuarios.email`, `alunos.cpf`, `empresas_parceiras.cnpj`, `instituicoes_ensino.nome` e `instituicoes_ensino.sigla` são únicos.
- `usuarios.tipo` aceita apenas `ALUNO` ou `EMPRESA`.
- `alunos.saldo` começa em zero e não aparece nos schemas de criação/atualização.
- exclusão de usuário remove sua especialização e endereço; a instituição é protegida por `RESTRICT`.
- CPF, CNPJ e CEP são persistidos apenas com dígitos.

O diagrama renderizável está em [modelo-er.mmd](modelo-er.mmd).

## Relação com a Sprint 1

Os documentos `Lab03S01-modelagem.pdf` (8 páginas) e `LABORATORIO_3_LAB_DESENVOLVIMENTO_DE_SOFTWARE.pdf` (2 páginas) foram revisados. As entidades `Usuario`, `Aluno`, `EmpresaParceira`, `InstituicaoEnsino` e `Endereco` preservam o núcleo cadastral e a decisão da Sprint 1 de centralizar identidade/autenticação em `Usuario`. A especialização relacional por PK/FK materializa a herança do diagrama de classes.

A modelagem original prevê login/senha para todos os perfis. Nesta versão inicial, `senha_hash` reserva a persistência segura, mas login e autenticação foram conscientemente adiados: expor um login sem rotas protegidas criaria uma falsa sensação de segurança. O campo deverá se tornar obrigatório quando OAuth2/JWT, hash forte e autorização por perfil forem entregues.

## Limite da Sprint 2

`Professor`, `Vantagem`, `Transacao`, `TransacaoEnvio` e `TransacaoResgate` permanecem planejados para a Sprint 3, exatamente como extensões do modelo de classes. Não foram criadas tabelas vazias nem regras fictícias para envio, extrato, resgate ou crédito semestral. `senha_hash` apenas reserva a estrutura de autenticação; nenhum login foi simulado.
