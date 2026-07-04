-- ===============================================================
-- BARBEARIA DO PEDRINHO - Configuracao da base de dados Supabase
-- ===============================================================
-- COMO USAR:
-- 1. Cria conta gratuita em https://supabase.com
-- 2. Cria um novo projeto (guarda a password do projeto)
-- 3. Menu lateral: SQL Editor -> New query
-- 4. Cola TODO este ficheiro e clica em "Run"
-- 5. Menu: Project Settings -> API
--    - Copia o "Project URL"       -> CONFIG.SUPABASE_URL no HTML
--    - Copia a chave "anon public"  -> CONFIG.SUPABASE_ANON_KEY no HTML
-- 6. Abre o HTML. O ponto verde no topo confirma a nuvem.
-- Sem estas chaves, o sistema funciona na mesma (guarda no telemovel).
-- ===============================================================

create table if not exists public.cortes (
  id bigint generated always as identity primary key,
  barbeiro text not null,
  cliente text not null,
  data date not null,
  serv_key text,
  serv_nome text not null,
  valor numeric not null default 0,
  com_barba boolean not null default false,
  obs text,
  created_at timestamptz not null default now()
);

create table if not exists public.clientes (
  id bigint generated always as identity primary key,
  barbeiro text not null,
  nome text not null,
  tel text,
  preferencia text,
  created_at timestamptz not null default now()
);

create index if not exists idx_cortes_barbeiro on public.cortes (barbeiro);
create index if not exists idx_cortes_data on public.cortes (data);
create index if not exists idx_clientes_barbeiro on public.clientes (barbeiro);

-- Seguranca (Row Level Security).
-- Esta app usa login ao nivel da aplicacao (nao usa Supabase Auth),
-- por isso permite leitura/escrita com a chave anon.
-- Para um teste privado e uma equipa de confianca e um compromisso aceitavel.
alter table public.cortes enable row level security;
alter table public.clientes enable row level security;

drop policy if exists cortes_anon_all on public.cortes;
drop policy if exists clientes_anon_all on public.clientes;

create policy cortes_anon_all on public.cortes for all using (true) with check (true);
create policy clientes_anon_all on public.clientes for all using (true) with check (true);
