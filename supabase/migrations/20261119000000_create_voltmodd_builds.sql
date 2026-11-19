begin;

-- The table stays outside the exposed Data API schemas. The public RPCs use
-- the caller's identity and privileges, including the table's RLS policies.
create schema voltmodd;
revoke all on schema voltmodd from public, anon, authenticated, service_role;
grant usage on schema voltmodd to authenticated;

create table voltmodd.builds (
  owner_id uuid not null references auth.users (id) on delete cascade,
  id text not null check (char_length(id) between 1 and 100 and btrim(id) <> ''),
  payload jsonb not null,
  revision bigint not null check (revision between 1 and 9007199254740991),
  updated_at bigint not null check (updated_at between 0 and 9007199254740991),
  primary key (owner_id, id),
  check (
    jsonb_typeof(payload) = 'object'
    and coalesce(payload ->> 'id', '') = id
    and jsonb_typeof(payload -> 'id') = 'string'
    and coalesce(char_length(payload ->> 'name'), 0) between 1 and 150
    and btrim(payload ->> 'name') <> ''
    and jsonb_typeof(payload -> 'name') = 'string'
    and coalesce(payload ->> 'type', '') in ('bike', 'scooter')
    and coalesce(payload ->> 'mode', '') in ('new', 'rebuild')
    and coalesce(payload -> 'updated' = to_jsonb(updated_at), false)
    and coalesce(jsonb_typeof(payload -> 'selected'), '') = 'object'
  )
);

create index builds_owner_updated on voltmodd.builds (owner_id, updated_at desc, id);

alter table voltmodd.builds enable row level security;
revoke all on voltmodd.builds from public, anon, authenticated, service_role;
grant select, insert, delete on voltmodd.builds to authenticated;
grant update (payload, revision, updated_at) on voltmodd.builds to authenticated;

create policy builds_select_own on voltmodd.builds for select to authenticated
  using ((select auth.uid()) = owner_id);
create policy builds_insert_own on voltmodd.builds for insert to authenticated
  with check ((select auth.uid()) = owner_id);
create policy builds_update_own on voltmodd.builds for update to authenticated
  using ((select auth.uid()) = owner_id)
  with check ((select auth.uid()) = owner_id);
create policy builds_delete_own on voltmodd.builds for delete to authenticated
  using ((select auth.uid()) = owner_id);

create function public.voltmodd_list_builds()
returns jsonb
language sql
stable security invoker
set search_path = ''
as $$
  select coalesce(
    jsonb_agg(
      b.payload || jsonb_build_object('revision', b.revision)
      order by b.updated_at desc, b.id
    ),
    '[]'::jsonb
  )
  from voltmodd.builds as b
  where b.owner_id = (select auth.uid());
$$;

create function public.voltmodd_save_build(p_build jsonb, p_expected_revision bigint)
returns jsonb
language plpgsql
security invoker
set search_path = ''
as $$
declare
  owner uuid := auth.uid();
  build_id text := p_build ->> 'id';
  updated_ms bigint := floor(extract(epoch from clock_timestamp()) * 1000);
  next_payload jsonb := jsonb_set(p_build - 'revision', '{updated}', to_jsonb(updated_ms));
  saved_payload jsonb;
  saved_revision bigint;
begin
  if p_expected_revision not between 0 and 9007199254740991 then
    raise exception 'Expected a nonnegative revision' using errcode = '22023';
  end if;

  if p_expected_revision > 0 then
    update voltmodd.builds as b
    set payload = next_payload, revision = b.revision + 1, updated_at = updated_ms
    where b.owner_id = owner and b.id = build_id and b.revision = p_expected_revision
    returning b.payload, b.revision into saved_payload, saved_revision;
  else
    insert into voltmodd.builds as b (owner_id, id, payload, revision, updated_at)
    values (owner, build_id, next_payload, 1, updated_ms)
    on conflict (owner_id, id) do update
      set payload = excluded.payload, revision = b.revision + 1, updated_at = excluded.updated_at
      where p_expected_revision is null
    returning b.payload, b.revision into saved_payload, saved_revision;
  end if;

  if saved_revision is null then
    select b.revision into saved_revision
    from voltmodd.builds as b
    where b.owner_id = owner and b.id = build_id;
    return jsonb_build_object('conflict', coalesce(saved_revision, 0));
  end if;

  return jsonb_build_object(
    'build', saved_payload || jsonb_build_object('revision', saved_revision),
    'created', saved_revision = 1
  );
end;
$$;

create function public.voltmodd_import_builds(p_builds jsonb)
returns jsonb
language plpgsql
security invoker
set search_path = ''
as $$
declare
  owner uuid := auth.uid();
  total integer;
  imported integer;
begin
  if jsonb_typeof(p_builds) is distinct from 'array' then
    raise exception 'Expected an array of builds' using errcode = '22023';
  end if;
  total := jsonb_array_length(p_builds);
  if total > 500 then
    raise exception 'Expected at most 500 builds' using errcode = '22023';
  end if;

  -- Keep the first legacy copy when a request repeats an ID. Insert in stable
  -- ID order so concurrent imports acquire overlapping locks in the same order.
  insert into voltmodd.builds (owner_id, id, payload, revision, updated_at)
  select owner, item ->> 'id', item - 'revision', 1, (item ->> 'updated')::bigint
  from (
    select distinct on (item ->> 'id') item
    from jsonb_array_elements(p_builds) with ordinality as entries(item, position)
    order by item ->> 'id', position
  ) as first_copy
  order by item ->> 'id'
  on conflict (owner_id, id) do nothing;

  get diagnostics imported = row_count;
  return jsonb_build_object(
    'builds', public.voltmodd_list_builds(),
    'imported', imported,
    'skipped', total - imported
  );
end;
$$;

create function public.voltmodd_delete_build(p_id text)
returns boolean
language sql
security invoker
set search_path = ''
as $$
  with deleted as (
    delete from voltmodd.builds
    where owner_id = (select auth.uid()) and id = p_id
    returning 1
  )
  select exists (select 1 from deleted);
$$;

revoke all on function public.voltmodd_list_builds() from public, anon, authenticated, service_role;
revoke all on function public.voltmodd_save_build(jsonb, bigint) from public, anon, authenticated, service_role;
revoke all on function public.voltmodd_import_builds(jsonb) from public, anon, authenticated, service_role;
revoke all on function public.voltmodd_delete_build(text) from public, anon, authenticated, service_role;
grant execute on function public.voltmodd_list_builds() to authenticated;
grant execute on function public.voltmodd_save_build(jsonb, bigint) to authenticated;
grant execute on function public.voltmodd_import_builds(jsonb) to authenticated;
grant execute on function public.voltmodd_delete_build(text) to authenticated;

commit;
