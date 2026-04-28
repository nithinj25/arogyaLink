class FamilyMember {
  final String id;
  final String name;
  final int age;
  final String gender;
  final String relationship;
  final List<String> conditions;
  final List<String> allergies;
  final String? bloodGroup;
  final List<String> medications;

  const FamilyMember({
    required this.id,
    required this.name,
    required this.age,
    required this.gender,
    required this.relationship,
    required this.conditions,
    required this.allergies,
    this.bloodGroup,
    required this.medications,
  });

  factory FamilyMember.fromJson(Map<String, dynamic> j) => FamilyMember(
    id:           j['id'] as String,
    name:         j['name'] as String,
    age:          (j['age'] as num).toInt(),
    gender:       j['gender'] as String,
    relationship: j['relationship'] as String,
    conditions:   List<String>.from(j['conditions'] ?? []),
    allergies:    List<String>.from(j['allergies'] ?? []),
    bloodGroup:   j['blood_group'] as String?,
    medications:  List<String>.from(j['medications'] ?? []),
  );
}

class Family {
  final String phone;
  final String primaryName;
  final String language;
  final String? address;
  final String? village;
  final String? district;
  final String? state;
  final String? pin;
  final List<FamilyMember> members;
  final int callCount;
  final int? registeredAt;

  const Family({
    required this.phone,
    required this.primaryName,
    required this.language,
    this.address,
    this.village,
    this.district,
    this.state,
    this.pin,
    required this.members,
    required this.callCount,
    this.registeredAt,
  });

  factory Family.fromJson(Map<String, dynamic> j) => Family(
    phone:        j['phone'] as String,
    primaryName:  j['primary_name'] as String,
    language:     j['language'] as String,
    address:      j['address'] as String?,
    village:      j['village'] as String?,
    district:     j['district'] as String?,
    state:        j['state'] as String?,
    pin:          j['pin'] as String?,
    members:      (j['members'] as List? ?? [])
        .map((e) => FamilyMember.fromJson(e as Map<String, dynamic>))
        .toList(),
    callCount:    (j['call_count'] as num? ?? 0).toInt(),
    registeredAt: j['registered_at'] as int?,
  );

  String get displayLocation =>
      [village, district, state].where((s) => s != null && s.isNotEmpty).join(', ');
}
