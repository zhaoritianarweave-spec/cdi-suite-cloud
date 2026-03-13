-- Run this in Supabase SQL Editor to create the usage_logs table
-- This table tracks API calls per user for rate limiting

create table if not exists usage_logs (
    id bigint generated always as identity primary key,
    user_id uuid not null references auth.users(id) on delete cascade,
    tab text not null,
    model text default '',
    created_at timestamptz default now()
);

-- Index for efficient monthly queries
create index if not exists idx_usage_user_month
    on usage_logs (user_id, created_at desc);

-- Enable RLS (Row Level Security)
alter table usage_logs enable row level security;

-- Users can only read/insert their own records
create policy "Users can insert own usage"
    on usage_logs for insert
    with check (auth.uid() = user_id);

create policy "Users can read own usage"
    on usage_logs for select
    using (auth.uid() = user_id);
