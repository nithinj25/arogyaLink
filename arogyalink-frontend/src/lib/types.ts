export type Language = 'en-IN' | 'hi-IN' | 'kn-IN' | 'te-IN'
export type AgentStatus = 'pending' | 'active' | 'complete' | 'error'
export type Gender = 'M' | 'F' | 'other'

export interface FamilyMember {
  id: string
  name: string
  age: number
  gender: Gender
  relationship: string
  conditions: string[]
  allergies: string[]
  blood_group: string | null
  medications: string[]
}

export interface Family {
  phone: string
  primary_name: string
  address: string
  village: string
  district: string
  state: string
  pin: string | null
  language: Language
  members: FamilyMember[]
  call_count: number
  last_call_at: number | null
  created_at: number | null
  updated_at: number | null
}

export interface FamilyCreate extends Omit<Family, 'call_count' | 'last_call_at' | 'created_at' | 'updated_at'> {}

export interface ConversationMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ExtractedInfo {
  patient_name?: string | null
  patient_member_id?: string | null
  symptom?: string | null
  severity?: string | null
  patient_profile?: string | null
  location?: string | null
}

export interface AgentStatuses {
  orchestrator: AgentStatus
  triage: AgentStatus
  location: AgentStatus
  dispatch: AgentStatus
  comms: AgentStatus
}

export interface Case {
  case_id: string
  phone: string
  source: 'voice' | 'whatsapp' | 'sms' | 'voice_reg'
  lang: Language
  state: string
  agent_statuses: AgentStatuses
  conversation_history: ConversationMessage[]
  extracted_info: ExtractedInfo
  triage_result?: Record<string, unknown>
  family_phone?: string | null
  family_name?: string | null
  created_at: number
  updated_at: number
}

export interface DashboardStats {
  total_cases: number
  today_cases: number
  active_calls: number
}
