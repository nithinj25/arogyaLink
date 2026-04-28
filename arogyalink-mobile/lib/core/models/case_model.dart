class ExtractedInfo {
  final String? symptom;
  final String? severity;
  final String? location;
  final String? patientName;
  final String? patientProfile;

  const ExtractedInfo({
    this.symptom,
    this.severity,
    this.location,
    this.patientName,
    this.patientProfile,
  });

  factory ExtractedInfo.fromJson(Map<String, dynamic> j) => ExtractedInfo(
    symptom:        j['symptom'] as String?,
    severity:       j['severity'] as String?,
    location:       j['location'] as String?,
    patientName:    j['patient_name'] as String?,
    patientProfile: j['patient_profile'] as String?,
  );
}

class ConversationMessage {
  final String role;
  final String content;
  const ConversationMessage({required this.role, required this.content});

  factory ConversationMessage.fromJson(Map<String, dynamic> j) =>
      ConversationMessage(role: j['role'] as String, content: j['content'] as String);
}

class CaseModel {
  final String caseId;
  final String phone;
  final String lang;
  final String source;
  final String state;
  final int createdAt;
  final String? familyName;
  final String? familyPhone;
  final ExtractedInfo? extractedInfo;
  final List<ConversationMessage> conversationHistory;

  const CaseModel({
    required this.caseId,
    required this.phone,
    required this.lang,
    required this.source,
    required this.state,
    required this.createdAt,
    this.familyName,
    this.familyPhone,
    this.extractedInfo,
    required this.conversationHistory,
  });

  bool get isActive => state == 'processing';

  factory CaseModel.fromJson(Map<String, dynamic> j) => CaseModel(
    caseId:              j['case_id'] as String,
    phone:               j['phone'] as String,
    lang:                j['lang'] as String,
    source:              j['source'] as String? ?? 'ivr',
    state:               j['state'] as String,
    createdAt:           (j['created_at'] as num).toInt(),
    familyName:          j['family_name'] as String?,
    familyPhone:         j['family_phone'] as String?,
    extractedInfo:       j['extracted_info'] != null
        ? ExtractedInfo.fromJson(j['extracted_info'] as Map<String, dynamic>)
        : null,
    conversationHistory: (j['conversation_history'] as List? ?? [])
        .map((e) => ConversationMessage.fromJson(e as Map<String, dynamic>))
        .toList(),
  );
}
