import 'package:dio/dio.dart';
import '../models/family.dart';
import '../models/case_model.dart';

class ApiService {
  final Dio _dio;

  ApiService({String? baseUrl})
      : _dio = Dio(BaseOptions(
          baseUrl: baseUrl ?? const String.fromEnvironment(
            'API_URL',
            defaultValue: 'http://localhost:8082',
          ),
          connectTimeout: const Duration(seconds: 10),
          receiveTimeout: const Duration(seconds: 15),
          headers: {'Content-Type': 'application/json'},
        ));

  // ── Families ─────────────────────────────────────────────────────────

  Future<List<Family>> listFamilies({String? search}) async {
    final resp = await _dio.get('/families', queryParameters: {
      if (search != null && search.isNotEmpty) 'search': search,
    });
    return (resp.data as List).map((e) => Family.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<Family> getFamily(String phone) async {
    final resp = await _dio.get('/families/${Uri.encodeComponent(phone)}');
    return Family.fromJson(resp.data as Map<String, dynamic>);
  }

  Future<Family> createFamily(Map<String, dynamic> data) async {
    final resp = await _dio.post('/families', data: data);
    return Family.fromJson(resp.data as Map<String, dynamic>);
  }

  Future<Family> updateFamily(String phone, Map<String, dynamic> data) async {
    final resp = await _dio.put('/families/${Uri.encodeComponent(phone)}', data: data);
    return Family.fromJson(resp.data as Map<String, dynamic>);
  }

  Future<void> deleteFamily(String phone) async {
    await _dio.delete('/families/${Uri.encodeComponent(phone)}');
  }

  // ── Cases ────────────────────────────────────────────────────────────

  Future<List<CaseModel>> listCases({int limit = 50}) async {
    final resp = await _dio.get('/cases', queryParameters: {'limit': limit});
    return (resp.data as List).map((e) => CaseModel.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<CaseModel> getCase(String caseId) async {
    final resp = await _dio.get('/cases/$caseId');
    return CaseModel.fromJson(resp.data as Map<String, dynamic>);
  }

  Future<Map<String, dynamic>> getDashboardStats() async {
    final resp = await _dio.get('/cases/stats');
    return resp.data as Map<String, dynamic>;
  }
}
