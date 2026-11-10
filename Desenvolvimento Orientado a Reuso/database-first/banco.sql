-- Parte III (Database First): banco de exemplo do Driftor com duas tabelas.
-- O banco vem primeiro; as classes e telas são geradas a partir dele.

create schema if not exists dbfirst;

create table if not exists dbfirst.empresas (
    id     integer generated always as identity primary key,
    nome   varchar(80)  not null,
    cnpj   varchar(18)  not null unique,
    setor  varchar(60)  not null
);

create table if not exists dbfirst.maquinas (
    id          integer generated always as identity primary key,
    empresa_id  integer      not null references dbfirst.empresas(id),
    nome        varchar(80)  not null,
    tag         varchar(20)  not null,
    tipo        varchar(40)  not null,
    situacao    varchar(20)  not null default 'ativa',
    criada_em   date         not null default current_date
);

insert into dbfirst.empresas (nome, cnpj, setor)
select * from (values
    ('Alfa',  '00.000.002/0001-80', 'Metalurgia'),
    ('Beta',  '00.000.003/0001-25', 'Metalurgia'),
    ('Gama',  '00.000.004/0001-70', 'Metalurgia'),
    ('Delta', '00.000.005/0001-14', 'Metalurgia')
) v(nome, cnpj, setor)
where not exists (select 1 from dbfirst.empresas);

insert into dbfirst.maquinas (empresa_id, nome, tag, tipo)
select e.id, v.nome, v.tag, 'torno'
from (values
    ('Alfa', 'Torno 01 · ST_20',        'ALF-01'),
    ('Alfa', 'Torno 02 · DR_20',        'ALF-02'),
    ('Alfa', 'Torno 03 · DR_MS_20',     'ALF-03'),
    ('Alfa', 'Torno 04 · DR_MS_ST_20',  'ALF-04'),
    ('Gama', 'Torno 01 · DR_MS_04',     'GAM-01'),
    ('Gama', 'Torno 02 · DR_MS_ST_09',  'GAM-02')
) v(empresa, nome, tag)
join dbfirst.empresas e on e.nome = v.empresa
where not exists (select 1 from dbfirst.maquinas);
