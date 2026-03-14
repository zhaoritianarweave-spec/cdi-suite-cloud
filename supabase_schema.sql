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

-- ===========================================================================
-- Subscriptions table — tracks user plan and Stripe billing
-- ===========================================================================

create table if not exists subscriptions (
    id bigint generated always as identity primary key,
    user_id uuid not null references auth.users(id) on delete cascade,
    plan text not null default 'free' check (plan in ('free', 'pro', 'enterprise')),
    stripe_customer_id text,
    stripe_subscription_id text,
    current_period_end timestamptz,
    status text not null default 'active' check (status in ('active', 'canceled', 'past_due', 'incomplete')),
    created_at timestamptz default now(),
    updated_at timestamptz default now(),
    constraint unique_user_subscription unique (user_id)
);

-- Index for quick user lookups
create index if not exists idx_subscriptions_user
    on subscriptions (user_id);

-- Index for Stripe webhook lookups
create index if not exists idx_subscriptions_stripe
    on subscriptions (stripe_customer_id);

-- Enable RLS
alter table subscriptions enable row level security;

-- Users can read their own subscription
create policy "Users can read own subscription"
    on subscriptions for select
    using (auth.uid() = user_id);

-- Only service role (backend/webhook) can insert/update subscriptions
-- App code uses the Supabase service role key for writes
create policy "Service role can manage subscriptions"
    on subscriptions for all
    using (auth.role() = 'service_role');
