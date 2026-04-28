import 'package:flutter/material.dart';
import '../../core/services/api_service.dart';
import '../../core/theme/app_colors.dart';
import '../../widgets/custom_button.dart';
import '../../widgets/language_selector.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});
  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _api = ApiService();
  bool _saving = false;
  String? _error;

  final _name    = TextEditingController();
  final _phone   = TextEditingController();
  final _village = TextEditingController();
  final _district= TextEditingController();
  final _state   = TextEditingController();
  String _lang   = 'en-IN';

  @override
  void dispose() {
    _name.dispose(); _phone.dispose(); _village.dispose();
    _district.dispose(); _state.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() { _saving = true; _error = null; });
    try {
      await _api.createFamily({
        'primary_name': _name.text.trim(),
        'phone':        _phone.text.trim(),
        'village':      _village.text.trim(),
        'district':     _district.text.trim(),
        'state':        _state.text.trim(),
        'language':     _lang,
        'members':      [{'id': 'm0', 'name': _name.text.trim(), 'age': 0, 'gender': 'M',
                          'relationship': 'self', 'conditions': [], 'allergies': [], 'medications': []}],
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Family registered successfully!'),
            backgroundColor: AppColors.accentGreen,
          ),
        );
        Navigator.of(context).pop();
      }
    } catch (e) {
      setState(() { _error = e.toString(); });
    } finally {
      setState(() { _saving = false; });
    }
  }

  InputDecoration _dec(String label, [String? hint]) => InputDecoration(
    labelText: label,
    hintText: hint,
    floatingLabelBehavior: FloatingLabelBehavior.always,
  );

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Register Family'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Text('Primary Contact',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                letterSpacing: 1.5, fontWeight: FontWeight.w600, color: AppColors.stone400,
              ),
            ),
            const SizedBox(height: 10),
            _Card(children: [
              TextFormField(
                controller: _name,
                decoration: _dec('Full Name *'),
                validator: (v) => v == null || v.isEmpty ? 'Required' : null,
              ),
              const SizedBox(height: 14),
              TextFormField(
                controller: _phone,
                decoration: _dec('Phone Number *', '+91 98765 43210'),
                keyboardType: TextInputType.phone,
                validator: (v) => v == null || v.isEmpty ? 'Required' : null,
              ),
            ]),

            const SizedBox(height: 20),
            Text('Language',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                letterSpacing: 1.5, fontWeight: FontWeight.w600, color: AppColors.stone400,
              ),
            ),
            const SizedBox(height: 10),
            _Card(children: [
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: LanguageSelector(value: _lang, onChanged: (v) => setState(() => _lang = v)),
              ),
            ]),

            const SizedBox(height: 20),
            Text('Home Address',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                letterSpacing: 1.5, fontWeight: FontWeight.w600, color: AppColors.stone400,
              ),
            ),
            const SizedBox(height: 10),
            _Card(children: [
              TextFormField(controller: _village,  decoration: _dec('Village / Town *'),
                validator: (v) => v == null || v.isEmpty ? 'Required' : null),
              const SizedBox(height: 14),
              TextFormField(controller: _district, decoration: _dec('District *'),
                validator: (v) => v == null || v.isEmpty ? 'Required' : null),
              const SizedBox(height: 14),
              TextFormField(controller: _state,    decoration: _dec('State *'),
                validator: (v) => v == null || v.isEmpty ? 'Required' : null),
            ]),

            if (_error != null) ...[
              const SizedBox(height: 14),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFFFEF2F2),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFFFECACA)),
                ),
                child: Text(_error!, style: const TextStyle(color: AppColors.emergency, fontSize: 13)),
              ),
            ],

            const SizedBox(height: 28),
            CustomButton(
              label: 'Register Family',
              loading: _saving,
              fullWidth: true,
              onPressed: _submit,
            ),
            const SizedBox(height: 12),
            CustomButton(
              label: 'Cancel',
              variant: BtnVariant.secondary,
              fullWidth: true,
              onPressed: () => Navigator.of(context).pop(),
            ),
          ],
        ),
      ),
    );
  }
}

class _Card extends StatelessWidget {
  final List<Widget> children;
  const _Card({required this.children});

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.all(16),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(16),
      border: Border.all(color: AppColors.stone200, width: 1.5),
    ),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: children),
  );
}
