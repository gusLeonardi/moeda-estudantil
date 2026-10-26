export type Endereco={id?:number;logradouro:string;numero:string;complemento?:string|null;bairro:string;cidade:string;estado:string;cep:string};
export type Instituicao={id:number;nome:string;sigla:string};
export type Aluno={id:number;nome:string;email:string;cpf:string;rg:string;curso:string;saldo:string;instituicao:Instituicao;endereco:Endereco};
export type AlunoCreate=Omit<Aluno,'id'|'saldo'|'instituicao'>&{instituicao_id:number};
export type AlunoUpdate=Omit<AlunoCreate,'cpf'>;
export type Empresa={id:number;nome:string;email:string;cnpj:string;telefone:string;endereco:Endereco};
export type EmpresaCreate=Omit<Empresa,'id'>;
export type EmpresaUpdate=Omit<EmpresaCreate,'cnpj'>;
