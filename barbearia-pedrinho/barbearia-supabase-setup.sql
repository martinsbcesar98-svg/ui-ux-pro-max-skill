-- ═══════════════════════════════════════════════════════════════
-- BARBEARIA DO PEDRINHO — Configuração da base de dados Supabase
-- ═══════════════════════════════════════════════════════════════
--
-- COMO USAR:
-- 1. Cria uma conta gratuita em https://supabase.com
-- 2. Cria um novo projeto (guarda a password do projeto)
-- 3. No menu lateral: SQL Editor -> New query
-- 4. Cola TODO este ficheiro e clica em "Run"
-- 5. Vai a: Project Settings -> API
--    - Copia o "Project URL"      -> cola em CONFIG.SUPABASE_URL no HTML
--    - Copia a chave "anon public" -> cola em CONFIG.SUPABASE_ANON_KEY no HTML
-- 6. Abre o barbearia-pedrinho.html. O ponto verde no topo confirma a nuvem.
--
-- Sem estas chaves, o sistema funciona na mesma (guarda no telemóvel).
-- ═══════════════════════════════════════════════════════════════

-- Tabela de cortes
create table if not exists public.cortes (
  id          bigint generated always as identity primary key,
  barbeiro    text not null,
  cliente     text not null,
  data        date not null,
  serv_key    text,
  serv_nome   text not null,
  valor       numeric not null default 0,
  com_barba   boolean not null default false,
  obs         text,
  created_at  timestamptz not null default now()
);
create index if not exists idx_cortes_barbeiro on public.cortes (barbeiro);
create index if not exists idx_cortes_data     on public.cortes (data);

-- Tabela de clientes
create table if not exists public.clientes (
  id          bigint generated always as identity primary key,
  barbeiro    text not null,
  nome        text not null,
  tel         text,
  preferencia text,
  created_at  timestamptz not null default now()
);
create index if not exists idx_clientes_barbeiro on public.clientes (barbeiro);

-- ───────────────────────────────────────────────────────────────
-- SEGURANÇA (Row Level Security)
-- ───────────────────────────────────────────────────────────────
-- Esta app usa login ao nível da aplicação (não usa Supabase Auth),
-- por isso as tabelas são acedidas com a chave "anon".
-- A configuração abaixo PERMITE leitura/escrita com a chave anon.
--
-- ⚠️  IMPORTANTE: isto significa que quem tiver o ficheiro HTML e as
--     chaves consegue ler/escrever os dados. Para uma barbearia com
--     equipa de confiança e ficheiro privado, é um compromisso aceitável.
--     NÃO publiques o HTML com as chaves num site público.
--
-- Se mais tarde quiseres segurança forte por barbeiro, migra para
-- Supabase Auth + políticas por utilizador. Fica como evolução futura.

alter table public.cortes   enable row level security;
alter table public.clientes enable row level security;

drop policy if exists cortes_anon_all   on public.cortes;
drop policy if exists clientes_anon_all on public.clientes;

create policy cortes_anon_all   on public.cortes   for all using (true) with check (true);
create policy clientes_anon_all on public.clientes for all using (true) with check (true);
