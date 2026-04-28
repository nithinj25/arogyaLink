import 'package:flutter/material.dart';
import '../core/theme/app_colors.dart';

class LanguageSelector extends StatelessWidget {
  final String value;
  final ValueChanged<String> onChanged;

  const LanguageSelector({super.key, required this.value, required this.onChanged});

  static const _langs = [
    ('en-IN', '🇮🇳', 'English'),
    ('hi-IN', '🇮🇳', 'हिंदी'),
    ('kn-IN', '🇮🇳', 'ಕನ್ನಡ'),
    ('te-IN', '🇮🇳', 'తెలుగు'),
  ];

  @override
  Widget build(BuildContext context) {
    return Row(
      children: _langs.map((l) {
        final (code, flag, name) = l;
        final selected = value == code;
        return Padding(
          padding: const EdgeInsets.only(right: 8),
          child: GestureDetector(
            onTap: () => onChanged(code),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 150),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: selected ? AppColors.stone900 : Colors.white,
                borderRadius: BorderRadius.circular(100),
                border: Border.all(
                  color: selected ? AppColors.stone900 : AppColors.stone200,
                  width: 1.5,
                ),
              ),
              child: Text('$flag  $name',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: selected ? FontWeight.w600 : FontWeight.normal,
                  color: selected ? Colors.white : AppColors.stone600,
                ),
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}
