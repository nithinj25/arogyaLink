import 'package:flutter/material.dart';

abstract class AppColors {
  // Stone palette (matches web tailwind config)
  static const stone50  = Color(0xFFFAFAF9);
  static const stone100 = Color(0xFFF5F5F4);
  static const stone200 = Color(0xFFE7E5E4);
  static const stone300 = Color(0xFFD6D3D1);
  static const stone400 = Color(0xFFA8A29E);
  static const stone500 = Color(0xFF78716C);
  static const stone600 = Color(0xFF57534E);
  static const stone700 = Color(0xFF44403C);
  static const stone800 = Color(0xFF292524);
  static const stone900 = Color(0xFF1C1917);
  static const stone950 = Color(0xFF0C0A09);

  // Accent
  static const accentBlue    = Color(0xFF1D57F6);
  static const accentMagenta = Color(0xFFFD73ED);
  static const accentCyan    = Color(0xFF00A1F1);
  static const accentOrange  = Color(0xFFE54F10);
  static const accentGreen   = Color(0xFF53F399);
  static const accentYellow  = Color(0xFFFFD102);

  // Emergency red
  static const emergency = Color(0xFFDC2626);

  // Semantic
  static const background      = stone50;
  static const backgroundDark  = stone950;
  static const surfaceLight     = Colors.white;
  static const surfaceDark      = stone900;
  static const borderLight      = stone200;
  static const borderDark       = stone800;
  static const textPrimary      = stone900;
  static const textSecondary    = stone600;
  static const textMuted        = stone400;
}
