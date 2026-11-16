## Pontif´ıcia Universidade Cat´olica de Minas Gerais Curso de Engenharia de Software Laborat´orio 3 - Segundo Semestre/2026 Pontos - 20,00 Disciplina: Projeto de Software Profa. Milena Menezes Ad˜ao

- 1 Sistema de Moeda Estudantil

Pretende-se desenvolver um sistema para estimular o reconhecimento do m´erito estudantil atrav´es de uma moeda virtual. Essa moeda pode ser distribu´ıda por professores aos seus alunos e trocada pelos alunos por produtos e descontos em empresas parceiras. Ap´os a an´alise inicial de requisitos do sistema, foram levantadas as seguintes informa¸c˜ oes:

## 2 Descri¸c˜ao do Sistema:

Os alunos que desejam ingressar no sistema de m´erito devem realizar um cadastro, indicando nome, email, CPF, RG, Endere¸co, Institui¸c˜ ao de Ensino e curso. As institui¸c˜ oes participantes j´a est˜ao pr´e- cadastradas no sistema, para que o aluno selecione. Os professores j´a estar˜ao pr´e-cadastrados no sistema (a institui¸c˜ ao envia a lista no momento da parceria). Cada professor ter´a armazenado o seu nome, CPF e departamento que est´a vinculado. E´ necess´ario deixar expl´ıcito que ele faz parte de uma institui¸c˜ ao. A cada semestre, os professores recebem um total de mil moedas, que podem ser distribu´ıdas aos seus alunos como forma de reconhecimento por bom comportamento, participa¸c˜ ao em aula, etcs. Esse total ´e acumul´avel no semestre (isto ´e, se o professor n˜ao distribuir todas as moedas num semestre, o total de 1.000 novas moedas ser´a adicionado ao seu saldo corrente). Para enviar moedas, o professor deve possuir saldo suficiente, indicando qual aluno dever´a receber o montante,

bem como o motivo pelo qual ele est´a sendo reconhecido (uma mensagem aberta, obrigat´oria).

Ao receber uma moeda, o aluno deve ser notificado por email. Professores e alunos devem ser capazes de consultar o extrato de sua conta, visualizando o total de moedas que ainda possui, bem como as transa¸c˜ oes que realizou (para o professor, o envio de moedas; para o aluno, recebimento ou troca de moedas). Para trocar moedas, o aluno deve selecionar uma das vantagens cadastradas no sistema. Elas incluem, por exemplo: desconto em restaurantes da universidade, desconto de mensalidade, ou compra de materiais espec´ıficos. Empresas que desejam realizar parceria tamb´em devem se cadastrar no sistema, incluindo as vantagens que deseja oferecer e o custo de cada uma dela (em moedas). Para cadastrar uma vantagem, a empresa parceira deve adicionar tamb´em uma descri¸c˜ ao e foto do produto.

Ao resgatar uma vantagem, o aluno deve ter o valor descontado do seu saldo. Um email de cupom deve ser enviado para que ele utilize na troca presencial. Um email tamb´em deve ser enviado ao parceiro, para que ele possa conferir a troca. Ambos os emails devem incluir um c´ odigo gerado pelo sistema, a fim de facilitar o processo de conferˆencia.

Por fim, alunos, professores e empresas parceiras precisam ter um login e uma senha cadastrados para acessar o sistema. Em todos os casos, um processo de autentica¸c˜ ao ´e necess´ario para realiza¸c˜ao dos requisitos.

- 3 Apresenta¸c˜ao Final:

Ao final da ´ultima sprint (Sprint 03), os alunos dever˜ ao apresentar o prot´otipo produzido para a Release 2, comparando-os com os modelos descritos inicialmente, bem como apresentando as modi- fica¸c˜ oes inseridas para o funcionamento adequado do software (conforme a especifica¸c˜ ao anterior). O sistema dever´a ser desenvolvido utilizando arquitetura MVC, e atendendo aos requisitos apresentados e cumprindo a modelagem produzida nas sprints iniciais do projeto. O reposit´orio GitHub deve es- tar atualizado, com todas as vers˜oes produzidas dos modelos UML e o c´ odigo final desenvolvido. A avalia¸c˜ ao final do projeto levar´a em considera¸c˜ ao os seguintes aspectos:


- Qualidade do sistema produzido (adequa¸c˜ ao aos requisitos apresentados);

- Alinhamento entre modelo (de classes e de arquitetura) e c´ odigo;

- Atualiza¸c˜ oes dos modelos conforme necessidade do projeto.

## 4 Processo de Desenvolvimento:

## Release 01:

## 4.1 Lab03S01

Modelagem do sistema: Diagrama de Casos de Uso, Hist´orias do Usu´ario, Diagrama de Classes e Diagrama de Componentes.

## 4.2 Lab03S02

Modelo ER, defini¸c˜ ao e implementa¸c˜ ao da estrat´egia de acesso ao banco de dados (ORM, Padr˜ ao DAO, etc), CRUDs de aluno e empresa parceira (vers˜ao inicial: front-end e comunica¸c˜ ao com back-end).

## 4.3 Lab03S03

CRUDs de aluno e empresa parceira (vers˜ao final), apresenta¸c˜ ao da arquitetura do sistema e camada de persistˆencia (obs.: preparar slides).

## Release 02:

## 4.4 Lab04S01

Desenvolver os Diagramas de Sequˆencia do projeto e o Diagrama de Vis˜ao Geral de Intera¸c˜ ao (nos padr˜oes UML). Implementa¸c˜ ao dos casos de uso restantes (aqueles que n˜ao foram desenvolvidos na realease anterior).

## 4.5 Lab04S02

Desenvolver Diagrama de Implanta¸c˜ ao. Al´em disso, a aplica¸c˜ ao deve ser implantada na nuvem, utili- zando preferencialmente Vercel e Render. (Os grupos que n˜ao desenvolveram interface grafica, dever˜ao desenvolver).

## 4.6 Lab04S03

Avalia¸c˜ ao. Cada grupo deve realizar a an´alise cr´ıtica de um projeto da turma. A an´alise consiste na entrega de um relat´orio de an´alise cr´ıtica do projeto, discutindo:

- arquitetura e tecnologias utilizadas

- organiza¸c˜ ao do GitHub

- dificuldade para configura¸c˜ ao do ambiente seguindo o README

- Apontar erros nos diagramas desenvolvidos

- Apontar erros no alinhamento entre o projeto do sistema desenvolvido e a implementa¸c˜ ao.

Al´em disso, o grupo deve identificar trˆes partes do c´ odigo que podem ser refatoradas de acordo com o padr˜ao GRASP, visando melhorar a compreens˜ao e manuten¸c˜ ao do sistema. A entrega das refatora¸c˜oes deve ser realizada via sistema de pull requests do GitHub, e documentadas no relat´orio (mostrando e descrevendo o c´ odigo antes e depois das mudan¸cas, refatora¸c˜ oes aplicadas, e justificativa). Os propriet´arios do projeto n˜ao precisam aceitar as contribui¸c˜ oes.


Aten¸c˜ao: semanalmente, todos os grupos dever˜ao apresentar o andamento das entregas durante a aula. A n˜ao participa¸c˜ao do grupo implicar´a na perda autom´atica de 50 por cento dos dos pontos da sprint.
