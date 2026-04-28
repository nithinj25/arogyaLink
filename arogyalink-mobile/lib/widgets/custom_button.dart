import 'package:flutter/material.dart';
import '../core/theme/app_colors.dart';

enum BtnVariant { primary, secondary, danger, ghost }
enum BtnSize    { sm, md, lg }

class CustomButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  final BtnVariant variant;
  final BtnSize size;
  final IconData? icon;
  final bool loading;
  final bool fullWidth;

  const CustomButton({
    super.key,
    required this.label,
    this.onPressed,
    this.variant = BtnVariant.primary,
    this.size = BtnSize.md,
    this.icon,
    this.loading = false,
    this.fullWidth = false,
  });

  @override
  Widget build(BuildContext context) {
    final bg = switch (variant) {
      BtnVariant.primary   => AppColors.stone900,
      BtnVariant.secondary => Colors.transparent,
      BtnVariant.danger    => AppColors.emergency,
      BtnVariant.ghost     => Colors.transparent,
    };
    final fg = switch (variant) {
      BtnVariant.primary   => Colors.white,
      BtnVariant.secondary => AppColors.stone800,
      BtnVariant.danger    => Colors.white,
      BtnVariant.ghost     => AppColors.stone600,
    };
    final padding = switch (size) {
      BtnSize.sm => const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      BtnSize.md => const EdgeInsets.symmetric(horizontal: 24, vertical: 11),
      BtnSize.lg => const EdgeInsets.symmetric(horizontal: 32, vertical: 14),
    };
    final fontSize = switch (size) {
      BtnSize.sm => 12.0, BtnSize.md => 14.0, BtnSize.lg => 15.0,
    };

    final child = Row(
      mainAxisSize: fullWidth ? MainAxisSize.max : MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        if (loading)
          SizedBox(width: 14, height: 14, child: CircularProgressIndicator(
            color: fg, strokeWidth: 2,
          ))
        else if (icon != null) ...[
          Icon(icon, size: fontSize + 2, color: fg),
          const SizedBox(width: 6),
        ],
        if (!loading) Text(label,
          style: TextStyle(fontSize: fontSize, fontWeight: FontWeight.w500, color: fg),
        ),
      ],
    );

    final shape = RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(100),
      side: variant == BtnVariant.secondary
          ? const BorderSide(color: AppColors.stone300, width: 1.5)
          : BorderSide.none,
    );

    return SizedBox(
      width: fullWidth ? double.infinity : null,
      child: ElevatedButton(
        onPressed: loading ? null : onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: bg,
          foregroundColor: fg,
          elevation: 0,
          padding: padding,
          shape: shape,
          shadowColor: Colors.transparent,
        ),
        child: child,
      ),
    );
  }
}
