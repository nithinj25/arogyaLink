import 'package:flutter/material.dart';
import '../core/models/case_model.dart';
import '../core/theme/app_colors.dart';

class CaseCard extends StatelessWidget {
  final CaseModel c;
  final VoidCallback? onTap;
  const CaseCard({super.key, required this.c, this.onTap});

  String _timeAgo(int ms) {
    final diff = DateTime.now().millisecondsSinceEpoch - ms;
    final s = diff ~/ 1000;
    if (s < 60) return '${s}s ago';
    final m = s ~/ 60;
    if (m < 60) return '${m}m ago';
    final h = m ~/ 60;
    if (h < 24) return '${h}h ago';
    return DateTime.fromMillisecondsSinceEpoch(ms).toString().substring(0, 10);
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppColors.stone200, width: 1.5),
        ),
        child: Row(
          children: [
            Container(
              width: 8, height: 8,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: c.isActive ? AppColors.emergency : AppColors.stone300,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(c.familyName ?? c.phone,
                    style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14, color: AppColors.stone800),
                  ),
                  const SizedBox(height: 2),
                  Text(c.extractedInfo?.symptom ?? 'No symptom recorded',
                    style: const TextStyle(fontSize: 12, color: AppColors.stone500),
                    maxLines: 1, overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(_timeAgo(c.createdAt), style: const TextStyle(fontSize: 11, color: AppColors.stone400)),
                const SizedBox(height: 4),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: c.isActive ? const Color(0xFFFEF3C7) : const Color(0xFFDCFCE7),
                    borderRadius: BorderRadius.circular(100),
                    border: Border.all(
                      color: c.isActive ? const Color(0xFFFCD34D) : const Color(0xFF86EFAC),
                    ),
                  ),
                  child: Text(c.state,
                    style: TextStyle(
                      fontSize: 10, fontWeight: FontWeight.w500,
                      color: c.isActive ? const Color(0xFF92400E) : const Color(0xFF166534),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
