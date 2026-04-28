import type { Family, FamilyCreate, Case, DashboardStats } from './types'

const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8082'

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error((body as { detail?: string }).detail ?? `HTTP ${res.status}`)
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

// ── Families ───────────────────────────────────────────────────────────────────

export async function listFamilies(search?: string): Promise<Family[]> {
  const qs = search ? `?search=${encodeURIComponent(search)}` : ''
  const data = await req<{ families: Family[] }>(`/families${qs}`)
  return data.families
}

export async function getFamily(phone: string): Promise<Family> {
  return req<Family>(`/families/${encodeURIComponent(phone)}`)
}

export async function createFamily(data: FamilyCreate): Promise<Family> {
  return req<Family>('/families', { method: 'POST', body: JSON.stringify(data) })
}

export async function updateFamily(phone: string, data: Partial<FamilyCreate>): Promise<Family> {
  return req<Family>(`/families/${encodeURIComponent(phone)}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteFamily(phone: string): Promise<void> {
  return req<void>(`/families/${encodeURIComponent(phone)}`, { method: 'DELETE' })
}

// ── Cases ──────────────────────────────────────────────────────────────────────

export async function listCases(limit = 50): Promise<Case[]> {
  const data = await req<{ cases: Case[] }>(`/cases?limit=${limit}`)
  return data.cases
}

export async function getCase(caseId: string): Promise<Case> {
  return req<Case>(`/cases/${caseId}`)
}

export async function getDashboardStats(): Promise<DashboardStats> {
  return req<DashboardStats>('/cases/stats')
}

// ── Outbound call ──────────────────────────────────────────────────────────────

export async function triggerCall(phone: string): Promise<{ call_sid: string; message: string }> {
  return req(`/voice/call-me?phone=${encodeURIComponent(phone)}`, { method: 'POST' })
}
