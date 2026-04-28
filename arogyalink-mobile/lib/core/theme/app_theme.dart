import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import 'app_colors.dart';

abstract class AppTheme {
  static ThemeData get light => _build(Brightness.light);
  static ThemeData get dark  => _build(Brightness.dark);

  static ThemeData _build(Brightness brightness) {
    final isDark = brightness == Brightness.dark;
    final bg      = isDark ? AppColors.backgroundDark  : AppColors.background;
    final surface = isDark ? AppColors.surfaceDark      : AppColors.surfaceLight;
    final border  = isDark ? AppColors.borderDark       : AppColors.borderLight;
    final textPri = isDark ? Colors.white               : AppColors.textPrimary;
    final textSec = isDark ? AppColors.stone400         : AppColors.textSecondary;

    final base = GoogleFonts.interTextTheme().apply(
      bodyColor: textPri,
      displayColor: textPri,
    );

    return ThemeData(
      brightness: brightness,
      scaffoldBackgroundColor: bg,
      colorScheme: ColorScheme(
        brightness: brightness,
        primary: AppColors.stone900,
        onPrimary: Colors.white,
        secondary: AppColors.accentBlue,
        onSecondary: Colors.white,
        error: AppColors.emergency,
        onError: Colors.white,
        background: bg,
        onBackground: textPri,
        surface: surface,
        onSurface: textPri,
      ),

      textTheme: base.copyWith(
        displayLarge:  base.displayLarge?.copyWith(fontFamily: GoogleFonts.playfairDisplay().fontFamily, fontWeight: FontWeight.w600),
        displayMedium: base.displayMedium?.copyWith(fontFamily: GoogleFonts.playfairDisplay().fontFamily, fontWeight: FontWeight.w600),
        displaySmall:  base.displaySmall?.copyWith(fontFamily: GoogleFonts.playfairDisplay().fontFamily, fontWeight: FontWeight.w600),
        headlineLarge: base.headlineLarge?.copyWith(fontFamily: GoogleFonts.playfairDisplay().fontFamily, fontWeight: FontWeight.w600),
        headlineMedium:base.headlineMedium?.copyWith(fontFamily: GoogleFonts.playfairDisplay().fontFamily, fontWeight: FontWeight.w600),
        headlineSmall: base.headlineSmall?.copyWith(fontFamily: GoogleFonts.playfairDisplay().fontFamily, fontWeight: FontWeight.w600),
        bodyLarge:     base.bodyLarge?.copyWith(color: textPri),
        bodyMedium:    base.bodyMedium?.copyWith(color: textSec),
        bodySmall:     base.bodySmall?.copyWith(color: textSec),
      ),

      appBarTheme: AppBarTheme(
        backgroundColor: surface,
        foregroundColor: textPri,
        elevation: 0,
        scrolledUnderElevation: 0,
        systemOverlayStyle: isDark ? SystemUiOverlayStyle.light : SystemUiOverlayStyle.dark,
        titleTextStyle: GoogleFonts.playfairDisplay(
          color: textPri,
          fontSize: 18,
          fontWeight: FontWeight.w600,
        ),
        iconTheme: IconThemeData(color: textSec, size: 20),
        shape: Border(bottom: BorderSide(color: border, width: 1.5)),
      ),

      cardTheme: CardTheme(
        color: surface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: BorderSide(color: border, width: 1.5),
        ),
        margin: EdgeInsets.zero,
      ),

      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surface,
        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: border, width: 1.5),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: border, width: 1.5),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: AppColors.stone500, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppColors.emergency, width: 1.5),
        ),
        hintStyle: GoogleFonts.inter(color: AppColors.stone400, fontSize: 14),
        labelStyle: GoogleFonts.inter(color: textSec, fontSize: 12, fontWeight: FontWeight.w500),
      ),

      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.stone900,
          foregroundColor: Colors.white,
          elevation: 0,
          shadowColor: Colors.transparent,
          shape: const StadiumBorder(),
          padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 12),
          textStyle: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w500),
        ),
      ),

      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: textPri,
          side: BorderSide(color: border, width: 1.5),
          shape: const StadiumBorder(),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 10),
          textStyle: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w500),
        ),
      ),

      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: textSec,
          textStyle: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w500),
        ),
      ),

      dividerTheme: DividerThemeData(color: border, thickness: 1.5, space: 0),

      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        backgroundColor: surface,
        selectedItemColor: AppColors.stone900,
        unselectedItemColor: AppColors.stone400,
        type: BottomNavigationBarType.fixed,
        elevation: 0,
        selectedLabelStyle: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.w500),
        unselectedLabelStyle: GoogleFonts.inter(fontSize: 11),
      ),

      floatingActionButtonTheme: const FloatingActionButtonThemeData(
        backgroundColor: AppColors.emergency,
        foregroundColor: Colors.white,
        elevation: 0,
        focusElevation: 0,
        hoverElevation: 0,
        shape: CircleBorder(),
      ),
    );
  }
}
